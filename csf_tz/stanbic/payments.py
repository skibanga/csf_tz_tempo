import frappe


@frappe.whitelist()
def make_payments_initiation(payroll_entry_name, currency, stanbic_setting_name=None):
    if currency and not stanbic_setting_name:
        company = frappe.get_cached_value(
            "Payroll Entry", payroll_entry_name, "company"
        )
        stanbic_setting_doc = frappe.get_doc(
            "Stanbic Setting", {"company": company, "currency": currency}
        )
        stanbic_setting_name = stanbic_setting_doc.name

    if not stanbic_setting_name:
        frappe.throw(
            "Stanbic Setting not found for currency {0}".format(currency),
            title="Stanbic Setting not found",
        )

    payments_initiation_doc = frappe.new_doc("Stanbic Payments Initiation")
    payments_initiation_doc.payroll_entry = payroll_entry_name
    payments_initiation_doc.stanbic_setting = stanbic_setting_name
    payments_initiation_doc.set_data()
    frappe.msgprint(
        _(f"Payments Initiation {payments_initiation_doc.name} created successfully.")
    )
    return payments_initiation_doc
