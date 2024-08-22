import frappe
from selcom_apigw_client import apigwClient

def execute(filters=None):
    columns = [
        {"fieldname": "order_id", "label": "Order ID", "fieldtype": "Data", "width": 100},
        {"fieldname": "creation_date", "label": "Creation Date", "fieldtype": "Date", "width": 150},
        {"fieldname": "amount", "label": "Amount", "fieldtype": "Data", "width": 100},
        {"fieldname": "payment_status", "label": "Payment Status", "fieldtype": "Data", "width": 150},
    ]

    selcom_settings = frappe.get_doc("Selcom Settings", "Selcom Settings")

    base_url = selcom_settings.get_password('base_url')
    api_key = selcom_settings.get_password('api_key')
    api_secret = selcom_settings.get_password('api_secret')

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    client = apigwClient.Client(base_url, api_key, api_secret)

    list_orders_dict = {
        "fromdate": from_date,
        "todate": to_date
    }

    list_orders_path = "/checkout/list-orders"

    try:
        response = client.getFunc(list_orders_path, list_orders_dict)

        if not isinstance(response, dict):
            frappe.throw("Error: Unexpected response format received from the API.")

        frappe.logger().debug(f"Raw API response: {response}")

        if response.get("resultcode") == "000":
            orders_data = response.get("data", [])

            data = []
            for order in orders_data:
                data.append([
                    order.get("order_id"),
                    order.get("creation_date"),
                    order.get("amount"),
                    order.get("payment_status")
                ])

            return columns, data
        else:
            frappe.throw(f"Error from API: {response.get('message')} (Code: {response.get('resultcode')})")

    except Exception as e:
        frappe.throw(f"Unexpected error: {str(e)}")
        return columns, []
