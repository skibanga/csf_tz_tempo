// Copyright (c) 2023, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('OTP Register', {
	refresh: function (frm) {
		// set filter for on party_type field
		frm.set_query("party_type", function () {
			return {
				filters: {
					"name": ["in", ["Customer", "Supplier", "Employee", "User", "Lead", "Student", "Guardian", "Instructor", "Member", "Sales Partner", "Sales Person", "Teacher", "Tenant", "Visitor", "Patient"]]
				}
			};
		});
		// if not Validate == 1 add custom button to validate OTP
		if (!frm.doc.registered && frm.doc.party_type && frm.doc.party && frm.doc.docstatus == 0) {
			frm.add_custom_button(__("Register OTP"), function () {
				// check if doc is not saved
				if (frm.is_dirty()) {
					frappe.show_alert({
						message: __("Please save the document first"),
						indicator: 'red'
					});
					return;
				}
				frappe.call({
					method: "csf_tz.authotp.doctype.otp_register.otp_register.register_otp",
					args: {
						"otp_doc": frm.doc
					},
					callback: function (r) {
						if (r.message) {
							frm.reload_doc();
						}
					}
				});
			});
		}

	},
	party_type: function (frm) {
		// clear party, party_name and user_name fields
		frm.set_value("party", "");
		frm.set_value("party_name", "");
		frm.set_value("user_name", "");
	},
});
