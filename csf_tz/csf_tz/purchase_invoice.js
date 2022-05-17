frappe.ui.form.on("Purchase Invoice", {
    supplier: function(frm) {
        if (!frm.doc.supplier) {
            return
        }
        setTimeout(function() {
            if (!frm.doc.tax_category){
                frappe.call({
                    method: "csf_tz.custom_api.get_tax_category",
                    args: {
                        doc_type: frm.doc.doctype,
                        company: frm.doc.company,
                    },
                    callback: function(r) {
                        if(!r.exc) {
                            frm.set_value("tax_category", r.message);
                            frm.trigger("tax_category");
                        }
                    }
                });           
        }
          }, 1000);   
    },
    setup: function(frm) {
        frm.set_query("taxes_and_charges", function() {
			return {
				"filters": {
                    "company": frm.doc.company,
				}
			};
        });
        frappe.call({
            method: "erpnext.accounts.doctype.accounting_dimension.accounting_dimension.get_dimensions",
            callback: function(r) {
                if(!r.exc) {
                    const dimensions = [];
                    r.message[0].forEach(element => {
                        dimensions.push(element.fieldname);
                    });
                    frm.dimensions = dimensions;
                    // console.log(frm.dimensions);
                    
                }
            }
        });  
        // const dimensions_fields = $("div.frappe-control[data-fieldname='expense_type']")
        // console.log(dimensions_fields);
    },
    onload: function(frm){
        frm.dimensions.forEach(i => {
            let dimension_field = $(`div.frappe-control[data-fieldname='${i}']`).find("input");
            dimension_field.on("focusout",function() {
                frm.doc.items.forEach(row => {
                    row[i]=frm.doc[i];
                });
                frm.refresh_field("items");
            });
        });
    },

});
frappe.ui.form.on("Purchase Invoice Item", {
    form_render: (frm, cdt, cdn) => {
        $('[data-fieldname="csf_tz_create_wtax_entry"]').removeClass('btn-default')
            .addClass('btn-info align-middle text-white font-weight-bold').css({
                'font-size': '14px', 'border-radius': '6px', 'width': '180px'
            });
    },
    items_add: function(frm, cdt, cdn) {
        var row = frappe.get_doc(cdt, cdn);
        frm.dimensions.forEach(i => {
            row[i]=frm.doc[i];
        });
        frm.refresh_field("items");
    },
    csf_tz_create_wtax_entry: (frm, cdt, cdn) => {
        frappe.call('csf_tz.custom_api.make_withholding_tax_gl_entries_for_purchase', {
            doc: frm.doc, method: 'From Front End'
        }).then(r => {
            frm.refresh();
        });
    }
});