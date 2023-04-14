import frappe
from frappe import _


def get_batch_info(batch_no):
    """
    search for batch info in
    1. batch
    2 .Purchase receipt
    3 .Purchase invoice
    4 .Stock entry
    5. Sales invoice
    6. Delivery note
    7. Stock Reconciliation
    """
    batch = frappe.get_cached_doc("Batch", batch_no)
    batch_info = []
    batch_info = get_batch_info_from_batch(batch, batch_info)
    batch_info = get_batch_info_from_purchase_receipt(batch, batch_info)
    batch_info = get_batch_info_from_purchase_invoice(batch, batch_info)
    batch_info = get_batch_info_from_stock_entry(batch, batch_info)
    batch_info = get_batch_info_from_sales_invoice(batch, batch_info)
    batch_info = get_batch_info_from_delivery_note(batch, batch_info)
    batch_info = get_batch_info_from_stock_reconciliation(batch, batch_info)

    # sort batch info by creation_date
    batch_info = sorted(batch_info, key=lambda k: k["creation_date"])
    return batch_info


def get_batch_info_from_batch(batch, batch_info):
    """
    search for batch info in batch
    """
    # convert creation date to date object
    posting_date = frappe.utils.data.getdate(batch.creation)
    batch_info.append(
        {
            "creation_date": batch.creation,
            "posting_date": posting_date,
            "batch_no": batch.name,
            "item_code": batch.item,
            "item_name": batch.item_name,
            "reference_type": "Batch",
            "reference_name": batch.name,
            "qty": batch.batch_qty,
        }
    )
    return batch_info


def get_batch_info_from_purchase_receipt(batch, batch_info):
    """
    search for batch info in Purchase receipt
    """
    for pr in frappe.get_all(
        "Purchase Receipt Item",
        filters={"batch_no": batch.name, "docstatus": 1},
        fields=["parent", "qty"],
    ):
        pr_doc = frappe.get_cached_doc("Purchase Receipt", pr.parent)
        batch_info.append(
            {
                "creation_date": pr_doc.creation,
                "posting_date": pr_doc.posting_date,
                "batch_no": batch.name,
                "item_code": batch.item,
                "item_name": batch.item_name,
                "reference_type": "Purchase Receipt",
                "reference_name": pr_doc.name,
                "qty": pr.qty,
            }
        )
    return batch_info


def get_batch_info_from_purchase_invoice(batch, batch_info):
    """
    search for batch info in Purchase invoice
    """
    for pi in frappe.get_all(
        "Purchase Invoice Item",
        filters={"batch_no": batch.name, "docstatus": 1},
        fields=["parent", "qty"],
    ):
        pi_doc = frappe.get_cached_doc("Purchase Invoice", pi.parent)
        if not pi_doc.update_stock:
            continue
        batch_info.append(
            {
                "creation_date": pi_doc.creation,
                "posting_date": pi_doc.posting_date,
                "batch_no": batch.name,
                "item_code": batch.item,
                "item_name": batch.item_name,
                "reference_type": "Purchase Invoice",
                "reference_name": pi_doc.name,
                "qty": pi.qty,
            }
        )
    return batch_info


def get_batch_info_from_stock_entry(batch, batch_info):
    """
    search for batch info in Stock entry
    """
    for se in frappe.get_all(
        "Stock Entry Detail",
        filters={"batch_no": batch.name, "docstatus": 1, "t_warehouse": ["!=", ""]},
        fields=["parent", "qty"],
    ):
        se_doc = frappe.get_cached_doc("Stock Entry", se.parent)
        batch_info.append(
            {
                "creation_date": se_doc.creation,
                "posting_date": se_doc.posting_date,
                "batch_no": batch.name,
                "item_code": batch.item,
                "item_name": batch.item_name,
                "reference_type": "Stock Entry",
                "reference_name": se_doc.name,
                "qty": se.qty,
            }
        )
        # if stock entry is manufacture
        if se_doc.purpose == "Manufacture":
            for se_item in se_doc.items:
                if (
                    se_item.batch_no
                    and se_item.batch_no != batch.name
                    and se_item.s_warehouse
                ):
                    se_batch_info = get_batch_info(se_item.batch_no)
                    batch_info.extend(se_batch_info)
    return batch_info


def get_batch_info_from_sales_invoice(batch, batch_info):
    """
    search for batch info in Sales invoice
    """
    for si in frappe.get_all(
        "Sales Invoice Item",
        filters={"batch_no": batch.name, "docstatus": 1},
        fields=["parent", "qty"],
    ):
        si_doc = frappe.get_cached_doc("Sales Invoice", si.parent)
        if not si_doc.update_stock:
            continue
        batch_info.append(
            {
                "creation_date": si_doc.creation,
                "posting_date": si_doc.posting_date,
                "batch_no": batch.name,
                "item_code": batch.item,
                "item_name": batch.item_name,
                "reference_type": "Sales Invoice",
                "reference_name": si_doc.name,
                "qty": si.qty,
            }
        )
    return batch_info


def get_batch_info_from_delivery_note(batch, batch_info):
    """
    search for batch info in Delivery note
    """
    for dn in frappe.get_all(
        "Delivery Note Item",
        filters={"batch_no": batch.name, "docstatus": 1},
        fields=["parent", "qty"],
    ):
        dn_doc = frappe.get_cached_doc("Delivery Note", dn.parent)
        batch_info.append(
            {
                "creation_date": dn_doc.creation,
                "posting_date": dn_doc.posting_date,
                "batch_no": batch.name,
                "item_code": batch.item,
                "item_name": batch.item_name,
                "reference_type": "Delivery Note",
                "reference_name": dn_doc.name,
                "qty": dn.qty,
            }
        )
    return batch_info


def get_batch_info_from_stock_reconciliation(batch, batch_info):
    """
    search for batch info in Stock Reconciliation
    """
    for sr in frappe.get_all(
        "Stock Reconciliation Item",
        filters={"batch_no": batch.name, "docstatus": 1},
        fields=["parent", "qty"],
    ):
        sr_doc = frappe.get_cached_doc("Stock Reconciliation", sr.parent)
        batch_info.append(
            {
                "creation_date": sr_doc.creation,
                "posting_date": sr_doc.posting_date,
                "batch_no": batch.name,
                "item_code": batch.item,
                "item_name": batch.item_name,
                "reference_type": "Stock Reconciliation",
                "reference_name": sr_doc.name,
                "qty": sr.qty,
            }
        )
    return batch_info
