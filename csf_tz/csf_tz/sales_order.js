frappe.require([
    '/assets/csf_tz/js/shortcuts.js',
]);

frappe.ui.form.on("Sales Order", {
    customer: function (frm) {
        if (!frm.doc.customer) {
            return;
        }
        frappe.call({
            method: 'csf_tz.csftz_hooks.customer.get_customer_total_unpaid_amount',
            args: {
                customer: frm.doc.customer,
                company: frm.doc.company,
            },
            callback: function (r, rt) {
                if (r.message) {
                    console.info(r.message);
                }
            }
        });
        setTimeout(function () {
            if (!frm.doc.tax_category) {
                frappe.call({
                    method: "csf_tz.custom_api.get_tax_category",
                    args: {
                        doc_type: frm.doc.doctype,
                        company: frm.doc.company,
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            frm.set_value("tax_category", r.message);
                            frm.trigger("tax_category");
                        }
                    }
                });
            }
        }, 1000);
    },
    default_item_discount: function (frm) {
        frm.doc.items.forEach(item => {
            frappe.model.set_value(item.doctype, item.name, 'discount_percentage', frm.doc.default_item_discount);
        });
    },
});

frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+q',
    action: () => {
        ctrlQ("Sales Order Item");
    },
    page: this.page,
    description: __('Select Item Warehouse'),
    ignore_inputs: true,
});

frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+i',
    action: () => {
        ctrlI("Sales Order Item");
    },
    page: this.page,
    description: __('Select Customer Item Price'),
    ignore_inputs: true,
});


frappe.ui.keys.add_shortcut({
    shortcut: 'ctrl+u',
    action: () => {
        ctrlU("Sales Order Item");
    },
    page: this.page,
    description: __('Select Item Price'),
    ignore_inputs: true,
});