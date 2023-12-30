# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from csf_tz.stanbic.doctype.stanbic_payments_initiation.xml import get_xml
from csf_tz.stanbic.pgp import encrypt_pgp


class StanbicPaymentsInitiation(Document):
    def validate(self):
        self.validate_data()

    def set_data(self):
        payroll_entry_doc = frappe.get_cached_doc("Payroll Entry", self.payroll_entry)
        self.set_entries(payroll_entry_doc)
        self.insert(ignore_permissions=True)
        self.reload()
        self.xml = get_xml(self)
        public_key = frappe.get_cached_value(
            "Stanbic Setting", self.stanbic_setting, "pgp_public_key"
        )
        self.encrypted_xml = encrypt_pgp(self.xml, public_key)
        self.save(ignore_permissions=True)

    def set_entries(self, payroll_entry_doc=None):
        if not payroll_entry_doc:
            payroll_entry_doc = frappe.get_cached_doc(
                "Payroll Entry", self.payroll_entry
            )
        self.number_of_transactions = 0
        self.control_sum = 0
        self.stanbic_payments_info = []
        # get all salay slips
        salary_slips = self.get_salary_slips()
        for slip in salary_slips:
            entry = self.append("stanbic_payments_info", {})
            entry.salary_slip = slip.name
            entry.employee = slip.employee
            entry.transfer_currency = slip.currency
            entry.transfer_amount = slip.net_pay
            self.number_of_transactions += 1
            self.control_sum += slip.net_pay

    def validate_data(self):
        self.validate_entries(self.payroll_entry)

    def validate_entries(self, payroll_entry_doc=None):
        # to be add validation as it required
        pass

    def get_salary_slips(self):
        slips = frappe.get_all(
            "Salary Slip",
            filters={"payroll_entry": self.payroll_entry},
            fields=[
                "name",
                "employee",
                "employee_name",
                "company",
                "docstatus",
                "currency",
                "net_pay",
            ],
        )
        # check if all slips are submitted
        for slip in slips:
            if slip.docstatus != 1:
                frappe.throw(
                    "Salary Slip {0} is not submitted".format(slip.name),
                    title="Salary Slip Not Submitted",
                )
        return slips
