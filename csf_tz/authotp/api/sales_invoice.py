# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt


import frappe
from frappe import _

def on_submit(doc, method):
    otp_active = frappe.get_cached_value("OTP Settings", "OTP Settings", "active")
    if otp_active and not doc.authotp_validated:
        frappe.throw(_("OTP not validated, please validated OTP first"))