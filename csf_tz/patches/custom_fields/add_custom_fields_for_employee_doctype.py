import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    patches = ["csf_tz.patches.custom_fields.add_custom_for_employee_doctype", "csf_tz.patches.custom_fields.add_custom_field_for_employee_doctype"]
    for patch_name in patches:
        patch_doc = frappe.get_doc("Patch Log", {"Patch": patch_name})
        frappe.delete_doc("Patch Log", patch_doc.name)

    fields = {
        "Employee":[
            dict(
                fieldname= "bank_account_name",
                fieldtype="Data",
                label="Bank Account Name",         
                translatable= 1,
            ),
            dict(
                fieldname= "employee_country_code",
                fieldtype="Link",
                options="Country",
                label="Employee Country Code",
            ),
            dict(
                fieldname= "employee_country",
                fieldtype="Data",
                fetch_from="employee_country.code",
                label="Employee Country",         
                translatable= 1,
            ),
            dict(
                fieldname= "bank_country",
                fieldtype="Link",
                options="Country",
                label="Bank Country",
                insert_after="bank_code",
            ),
            dict(
                fieldname= "bank_country_code",
                fieldtype="Data",
                options="Country",                
                fetch_from="bank_country.code",
                label="Bank Country Code",
                read_only= 1,         
                translatable= 1,
            ),
            dict(
                fieldname= "beneficiary_bank_bic",
                fieldtype="Data",
                label="Beneficiary Bank BIC",
                translatable= 1,
            ),
        ]
    }
    create_custom_fields(fields, update=True)
