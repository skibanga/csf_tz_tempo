# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import pyotp
from pyqrcode import create as qrcreate

import frappe
from frappe.model.document import Document


class OTPRegister(Document):
    def validate(self):
        self.set_party_name()
        self.set_otp_secret()

    def set_party_name(self):
        if not self.party:
            return
        if self.party_type == "Customer":
            self.party_name = frappe.get_cached_value(
                "Customer", self.party, "customer_name"
            )
        elif self.party_type == "Supplier":
            self.party_name = frappe.get_cached_value(
                "Supplier", self.party, "supplier_name"
            )
        elif self.party_type == "Employee":
            self.party_name = frappe.get_cached_value(
                "Employee", self.party, "employee_name"
            )
        elif self.party_type == "User":
            self.party_name = frappe.get_cached_value("User", self.party, "full_name")
        elif self.party_type == "Contact":
            self.party_name = frappe.get_cached_value(
                "Contact", self.party, "first_name"
            )
        elif self.party_type == "Lead":
            self.party_name = frappe.get_cached_value("Lead", self.party, "lead_name")
        elif self.party_type == "Sales Partner":
            self.party_name = self.party
        elif self.party_type == "Student":
            first_name, middle_name, last_name = frappe.get_cached_value(
                "Student", self.party, ["first_name", "middle_name", "last_name"]
            )
            self.party_name = " ".join(
                filter(None, [first_name, middle_name, last_name])
            )
        elif self.party_type == "Guardian":
            self.party_name = frappe.get_cached_value(
                "Guardian", self.party, "guardian_name"
            )
        elif self.party_type == "Donor":
            self.party_name = frappe.get_cached_value("Donor", self.party, "donor_name")
        elif self.party_type == "Member":
            self.party_name = frappe.get_cached_value(
                "Member", self.party, "member_name"
            )
        elif self.party_type == "Patient":
            self.party_name = frappe.get_cached_value(
                "Patient", self.party, "patient_name"
            )
        elif self.party_type == "Instructor":
            self.party_name = frappe.get_cached_value(
                "Instructor", self.party, "instructor_name"
            )
        elif self.party_type == "Sales Person":
            self.party_name = frappe.get_cached_value(
                "Sales Person", self.party, "sales_person_name"
            )
        elif self.party_type == "Teacher":
            self.party_name = frappe.get_cached_value(
                "Teacher", self.party, "teacher_name"
            )
        elif self.party_type == "Tenant":
            self.party_name = frappe.get_cached_value(
                "Tenant", self.party, "tenant_name"
            )
        elif self.party_type == "Visitor":
            self.party_name = frappe.get_cached_value(
                "Visitor", self.party, "visitor_name"
            )

        if not self.party_name:
            self.party_name = self.party

        if not self.user_name:
            self.user_name = self.party_name

    def set_otp_secret(self):
        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()

    def get_otp_secret(self):
        return self.get_password("otp_secret")


@frappe.whitelist()
def register_otp(otp_doc):
    otp_doc = frappe._dict(frappe.parse_json(otp_doc))
    otp_doc = frappe.get_doc(otp_doc)
    if otp_doc.docstatus == 1:
        frappe.throw("Document is already submitted")
    if otp_doc.registered:
        frappe.throw("OTP already registered")
    if otp_doc.otp_type == "OTP APP":
        register_otp_app(otp_doc)
    elif otp_doc.otp_type == "SMS":
        register_otp_sms(otp_doc)
    elif otp_doc.otp_type == "Email":
        register_otp_email(otp_doc)


def register_otp_sms(otp_doc=None):
    frappe.throw("SMS OTP not implemented")
    return


def register_otp_email(otp_doc=None):
    frappe.throw("Email OTP not implemented")
    return


def register_otp_app(otp_doc):
    frappe.msgprint(str(f"<img src='https://api.qrserver.com/v1/create-qr-code/?data={otp_doc.get_otp_secret()}&size=220x220&margin=0'>"))

    return
