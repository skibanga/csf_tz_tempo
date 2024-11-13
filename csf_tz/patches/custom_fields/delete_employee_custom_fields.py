import frappe

def execute():
    fields = ['employee_country', 'employee_country_code', 'bank_country', 'bank_country_code', 'beneficiary_bank_bic']
    for field in fields:
        frappe.db.delete("Custom Field", {"fieldname": field})
    frappe.db.commit()
