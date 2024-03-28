import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
    df = {
        "fieldname": "allow_negative",
        "label": "Allow Negative",
        "fieldtype": "Check",
        "insert_after": "disabled",
    }

    create_custom_field("Salary Component", df)
