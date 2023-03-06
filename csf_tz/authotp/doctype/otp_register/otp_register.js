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

	},
	party_type: function (frm) {
		// clear party, party_name and user_name fields
		frm.set_value("party", "");
		frm.set_value("party_name", "");
		frm.set_value("user_name", "");
	},
});
