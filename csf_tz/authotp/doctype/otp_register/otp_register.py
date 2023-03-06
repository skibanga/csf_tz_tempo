# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OTPRegister(Document):
    def validate(self):
        self.set_party_name()

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
