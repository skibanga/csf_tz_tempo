import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Employee":[
            dict(
                fieldname= "bank_account_name",
                fieldtype="Data",
                label="Bank Account Name",         
                translatable= 1,
            ),
            dict(
                fieldname= "custom_employee_country_codes",
                fieldtype="Link",
                options="Country",
                label="Employee Country",
            ),
            dict(
                fieldname= "custom_employee_country",
                fieldtype="Data",
                fetch_from="employee_country.code",
                label="Employee Country",         
                translatable= 1,
            ),
        ]
    }
    create_custom_fields(fields, update=True) 