from selcom_apigw_client import apigwClient
import json
import frappe
from frappe import _
import base64
import re

# Initialize API client
selcom_settings = frappe.get_doc("Selcom Settings")
apiKey = selcom_settings.get_password("api_key")
apiSecret = selcom_settings.get_password("api_secret")
baseUrl = selcom_settings.get_password("base_url")


def create_order_log(
    method, status, request_json, response, reference, order_id, docname=None
):
    doc = frappe.new_doc("Selcom Order Log")
    doc.date = frappe.utils.today()
    doc.time = frappe.utils.nowtime()
    doc.method = method
    if docname:
        doc.registration_docname = docname
    doc.status = status
    doc.reference = reference
    doc.order_id = order_id
    doc.request_data = json.dumps(request_json, indent=4)
    doc.response_data = json.dumps(response, indent=4)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()


def get_coupon_discount(coupon_code, company_type):
    if frappe.db.exists({"doctype": "TAFINA Coupon", "name": coupon_code}):
        coupon = frappe.get_doc("TAFINA Coupon", coupon_code)
        if coupon.used:
            return (
                None,
                "Coupon has already been used. Kindly check your last email and you may pay using the link provided.",
            )
        if coupon.company != company_type:
            return (
                None,
                "Company does not match the coupon. Recheck the company name and/or coupon code.",
            )
        if coupon.full_discount:
            return (
                1.0,
                "A full discount has been applied to make this registration FREE OF COST to you.",
            )
        else:
            return (
                0.1,
                "A 10% discount has been applied to your registration. Kindly make the payment.",
            )
    else:
        return None, "Invalid coupon code."


def mark_coupon_as_used(coupon_code):
    coupon = frappe.get_doc("TAFINA Coupon", coupon_code)
    coupon.used = 1
    coupon.save(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def create_order_minimal(order_data):
    order_data = json.loads(order_data)

    package_prices = {
        "Individual": {
            "Basic": {"USD": 150, "TZS": 405000},
            "Standard": {"USD": 225, "TZS": 607500},
            "Premium": {"USD": 450, "TZS": 1215000},
            "Ordinary-1-day": {"TZS": 50000},
            "Ordinary-2-day": {"TZS": 100000},
        },
        "Corporate": {
            "Basic": {"USD": 300, "TZS": 810000},
            "Standard": {"USD": 450, "TZS": 1215000},
            "Premium": {"USD": 1250, "TZS": 3375000},
            "VIP": {"USD": 2500, "TZS": 6750000},
        },
        "Separate_FinTech": {
            "Single": {"USD": 93, "TZS": 250000},
            "Group of Three": {"USD": 260, "TZS": 700000},
        },
        "Sponsor": {
            "Bronze": {"USD": 4000, "TZS": 10800000},
            "Silver": {"USD": 7000, "TZS": 18900000},
            "Gold": {"USD": 12000, "TZS": 32400000},
            "Platinum": {"USD": 25000, "TZS": 67500000},
        },
    }

    form_type = order_data.get("form_type")
    if form_type not in package_prices:
        frappe.throw("Unknown form type")

    package_type = order_data.get("package")
    currency = order_data.get("package_currency")
    try:
        amount = package_prices[form_type][package_type][currency]
    except KeyError:
        frappe.throw("Package type or currency is not defined correctly.")

    package_qty = int(order_data.get("package_qty", 1))
    amount *= package_qty

    coupon_code = order_data.get("coupon")
    company = order_data.get("company")
    discount = 0
    if coupon_code:
        discount_rate, message = get_coupon_discount(coupon_code, company)
        if discount_rate is None:
            frappe.throw(message)
        discount = amount * discount_rate
        if discount_rate == 1.0:
            amount = 0
        else:
            amount -= discount

    redirect_url = "https://tafina-rsvp.aakvaerp.com/thank-you-for-the-payment"
    redirect_encoded_url = base64.b64encode(redirect_url.encode()).decode()

    order_id = frappe.generate_hash(length=10)
    docname, target_doctype = insert_based_on_form_type(order_data, order_id)

    if amount == 0:
        frappe.msgprint(_("Order created successfully with full discount"), alert=True)
        create_order_log(
            "Create Order",
            "Success",
            order_data,
            {"message": "Full discount applied. No payment required."},
            reference=order_id,
            order_id=order_id,
            docname=docname,
        )
        if coupon_code:
            mark_coupon_as_used(coupon_code)
        return {
            "success": True,
            "message": "Order created successfully with full discount. No payment required.",
            "payment_gateway_url": redirect_url,
        }

    client = apigwClient.Client(baseUrl, apiKey, apiSecret)

    call_back_url = "https://tafina-rsvp.aakvaerp.com/api/method/csf_tz.api.selcom.create_webhook_callback"
    callback_encoded_url = base64.b64encode(call_back_url.encode()).decode()

    pattern = r"^255\d{9}$"
    if re.match(pattern, order_data.get("mobile")):
        phone_number = order_data.get("mobile")
    else:
        frappe.throw(
            "Invalid phone number. It should start with '255' and be followed by 9 digits."
        )

    country = frappe.get_doc("Country", order_data.get("country"))

    orderDict = {
        "vendor": selcom_settings.get_password("vendor"),
        "order_id": order_id,
        "buyer_email": order_data.get("email"),
        "buyer_name": f"{order_data.get('first_name')} {order_data.get('last_name')}",
        "buyer_userid": "",
        "buyer_phone": phone_number,
        "gateway_buyer_uuid": "",
        "amount": round(float(amount)),
        "currency": currency,
        "payment_methods": "ALL",
        "redirect_url": redirect_encoded_url,
        "cancel_url": "",
        "webhook": callback_encoded_url,
        "billing.firstname": order_data.get("first_name"),
        "billing.lastname": order_data.get("last_name"),
        "billing.address_1": order_data.get("address_1"),
        "billing.address_2": "",
        "billing.city": order_data.get("city"),
        "billing.state_or_region": order_data.get("state_or_region"),
        "billing.postcode_or_pobox": order_data.get("postcode_or_pobox"),
        "billing.country": country.code.upper(),
        "billing.phone": phone_number,
        "buyer_remarks": "Payment",
        "merchant_remarks": "Payment",
        "no_of_items": 1,
    }

    orderPath = "/checkout/create-order"
    try:
        response = client.postFunc(orderPath, orderDict)
        if response.get("resultcode") != "000":
            create_order_log(
                "Create Order",
                "Failed",
                orderDict,
                response,
                reference=response.get("reference"),
                order_id=order_id,
                docname=docname,
            )
            frappe.db.set_value(target_doctype, docname, "payment_status", "Failed")
            return response

        else:
            encoded_url = response["data"][0]["payment_gateway_url"]
            decoded_url = base64.b64decode(encoded_url).decode("utf-8")
            frappe.db.set_value(target_doctype, docname, "payment_url", decoded_url)
            frappe.msgprint(_("Order created successfully"), alert=True)
            create_order_log(
                "Create Order",
                "Success",
                orderDict,
                response,
                reference=response.get("reference"),
                order_id=order_id,
                docname=docname,
            )
            if coupon_code:
                mark_coupon_as_used(coupon_code)
            return {
                "success": True,
                "message": "Payment notification logged successfully.",
                "payment_gateway_url": decoded_url,
            }

    except Exception as e:
        create_order_log(
            "Create Order",
            "Failed",
            orderDict,
            str(e),
            reference="",
            order_id=order_id,
            docname=docname,
        )
        frappe.db.set_value(target_doctype, docname, "payment_status", "Failed")
        frappe.throw(
            _("Failed to create order, please try again, or contact the administrator")
        )


@frappe.whitelist(allow_guest=True)
def create_webhook_callback(*args, **kwargs):
    doc = frappe.new_doc("Selcom Webhook Callback")
    doc.data = frappe.as_json(kwargs)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def get_order_id_status(order_log, order_id):
    client = apigwClient.Client(baseUrl, apiKey, apiSecret)
    orderStatusDict = {"order_id": order_id}
    orderStatusPath = "/checkout/order-status"
    response = client.getFunc(orderStatusPath, orderStatusDict)

    doc = frappe.get_doc("Selcom Order Log", order_log)
    doc.order_id_status_data = json.dumps(response, indent=4)
    doc.save(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def insert_based_on_form_type(order_data, order_id, payment_url=None):

    form_docs = {
        "Individual": "Registration",
        "Corporate": "Corporate Registration",
        "Sponsor": "Sponsor Registration",
        "Separate_FinTech": "Separate FinTech Package",
    }
    form_type = order_data.get("form_type")
    target_doctype = form_docs.get(form_type)

    if not target_doctype:
        frappe.throw("Invalid form type provided.")

    try:
        if isinstance(order_data, str):
            order_data = json.loads(order_data)

        doc = frappe.new_doc(target_doctype)

        for field, value in order_data.items():
            if hasattr(doc, field):
                setattr(doc, field, value)

        doc.full_name = f"{order_data.get('first_name')} {order_data.get('last_name')}"
        doc.order_id = order_id
        doc.payment_url = payment_url
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return doc.name, target_doctype

    except Exception as e:
        frappe.log_error(f"Error in insert_based_on_form_type: {str(e)}")
        frappe.throw(f"An error occurred: {str(e)}")
