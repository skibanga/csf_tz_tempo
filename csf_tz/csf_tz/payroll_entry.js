const buttonName = "Generate Stanbic Payments Initiation";
frappe.ui.form.on("Payroll Entry", {
    setup: function(frm) {
        frm.trigger("control_action_buttons");
        
    },
    refresh:function(frm) {
        frm.trigger("control_action_buttons");
        if (frm.doc.docstatus == 1) generate_payments_initiation(frm);
        else {
          frm.remove_custom_button(__(buttonName));
        }
  },
    },
    onload: (frm) => {
        frm.trigger("control_action_buttons");
    },
    workflow_state: (frm) => {
        if (frm.doc.has_payroll_approval == 1) {
            frm.refresh();
        }
    },
    create_update_slips_btn: function (frm) {
        if (frm.doc.docstatus != 1) {
            return
        }
        frm.add_custom_button(__("Update Salary Slips"), function() {
            frappe.call({
                method: 'csf_tz.csftz_hooks.payroll.update_slips',
                args: {
                    payroll_entry: frm.doc.name,
                },
                callback: function(r) {
                    if (r.message) {
                        console.log(r.message);
                    }
                }
            });
        });
    },
    create_print_btn: function (frm) {
        if (frm.doc.docstatus != 1) {
            return
        }
        frm.add_custom_button(__("Print Salary Slips"), function() {
            frappe.call({
                method: 'csf_tz.csftz_hooks.payroll.print_slips',
                args: {
                    payroll_entry: frm.doc.name,
                },
                // callback: function(r) {
                //     if (r.message) {
                //         frm.reload_doc();
                //     }
                // }
            });
        });
    },
    create_journal_entry_btn: function (frm) {
        if (frm.doc.docstatus != 1 || frm.doc.salary_slips_submitted == 1) {
            return;
        }
        frm.add_custom_button(__("Create Journal Entry"), function () {
            frappe.call({
                method: 'csf_tz.csftz_hooks.payroll.create_journal_entry',
                args: {
                    payroll_entry: frm.doc.name,
                },
                // callback: function(r) {
                //     if (r.message) {
                //         frm.reload_doc();
                //     }
                // }
            });
        });
    },

    control_action_buttons: (frm) => {
        if (frm.doc.docstatus == 1 && frm.doc.has_payroll_approval == 1) {
            if (frm.doc.workflow_state == "Salary Slips Created") {
                frm.trigger("create_update_slips_btn");
                $('[data-label="Submit%20Salary%20Slip"]').hide();
            } else if (
                frm.doc.workflow_state == "Approval Requested" ||
                frm.doc.workflow_state == "Change Requested" ||
                frm.doc.workflow_state.includes("Reviewed")
            ) {
                frm.clear_custom_buttons();
                frm.set_intro("");
                frm.set_intro(__("This Payroll Entry is under approval."));
            } else if (frm.doc.workflow_state.includes("Approved")) {
                frm.trigger("create_print_btn");
                frm.trigger("create_journal_entry_btn");
            }
        } else {
            frm.trigger("create_update_slips_btn");
            frm.trigger("create_print_btn");
            frm.trigger("create_journal_entry_btn");
        }
    },
});

function generate_payments_initiation(frm) {
  let condition = true;
  frappe.db
    .get_list("Salary Slip", {
      fields: ["name", "docstatus"],
      filters: {
        payroll_entry: frm.doc.name,
      },
    })
    .then((res) => {
      if (res.length == 0) condition = false;
      // loop through the salary slips and check if all are submitted
      res.forEach((slip) => {
        if (slip.docstatus != 1) {
          condition = false;
        }
      });
      // if all salary slips are submitted, add custom button
      if (condition == true) {
        add_generate_payments_initiation_button(frm);
      } else {
        frm.remove_custom_button(__(buttonName));
      }
    });
}

function add_generate_payments_initiation_button(frm) {
  frm.add_custom_button(__(buttonName), function () {
    frappe.call({
      method: "csf_tz.stanbic.payments.make_payments_initiation",
      args: {
        payroll_entry_name: frm.doc.name,
        currency: frm.doc.currency,
      },
      callback: function (r) {
        if (r.message) {
          console.log(r.message);
        }
      },
    });
  });
}
