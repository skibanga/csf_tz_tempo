# Copyright (c) 2024, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CSFTZBankCharges(Document):
    def validate(self):
        self.total_bank_charges = sum(
            row.debit_amount
            for row in self.get("csf_tz_bank_charges_detail")
            if row.debit_amount > 0
        )

    def on_submit(self):
        payments = []
        for detail in self.get("csf_tz_bank_charges_detail"):
            pe_details = self.create_pe(
                detail.debit_amount, detail.value_date, detail.reference_number
            )

            detail.ref_docname = pe_details["reference_name"]
            detail.ref_doctype = pe_details["reference_type"]
            payments.append(pe_details)

        pi = frappe.new_doc("Purchase Invoice")
        pi.supplier = self.bank_supplier
        pi.append(
            "items",
            {
                "item_code": "Bank Charges",
                "qty": 1,
                "rate": self.total_bank_charges,
                "amount": self.total_bank_charges,
            },
        )
        pi.save(
            ignore_permissions=True,
        )
        pi.submit()
        self.ref_pi = pi.name
        frappe.msgprint(f"PI {pi.name} created successfully")

        invoices = {
            "invoice_type": pi.doctype,
            "invoice_number": pi.name,
            "invoice_date": pi.posting_date,
            "amount": pi.grand_total,
            "outstanding_amount": pi.outstanding_amount,
            "currency": pi.currency,
            "exchange_rate": self.exchange_rate,
        }
        self.payment_reconcile(payments, invoices)

    def create_pe(self, debit_amount, value_date, reference_number):
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.party_type = "Supplier"
        pe.party = self.bank_supplier
        pe.paid_to = self.account
        pe.paid_amount = debit_amount
        pe.received_amount = debit_amount
        pe.source_exchange_rate = self.exchange_rate
        pe.paid_from = self.account
        pe.paid_from_account_currency = self.currency
        pe.reference_date = value_date
        pe.reference_no = reference_number

        pe.save(
            ignore_permissions=True,
        )
        pe.submit()
        frappe.msgprint(f"PE {pe.name} created successfully")
        return {
            "reference_type": pe.doctype,
            "reference_name": pe.name,
            "posting_date": pe.posting_date,
            "amount": pe.unallocated_amount,
            "unallocated_amount": pe.unallocated_amount,
            "difference_amount": 0,
            "currency": pe.paid_from_account_currency,
            "exchange_rate": self.exchange_rate,
        }

    def payment_reconcile(self, payments, invoices):

        from erpnext.accounts.party import get_party_account

        reconcile = frappe.new_doc("Payment Reconciliation")
        reconcile.party_type = "Supplier"
        reconcile.party = self.bank_supplier
        reconcile.company = self.company
        reconcile.receivable_payable_account = get_party_account(
            "Supplier", self.bank_supplier, self.company
        )
        reconcile.get_unreconciled_entries()
        reconcile.allocate_entries(
            {
                "invoices": [invoices],
                "payments": payments,
            }
        )
        reconcile.reconcile()
