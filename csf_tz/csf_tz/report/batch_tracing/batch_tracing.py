# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

# import frappe
from csf_tz.csftz_hooks.batches import get_batch_info


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": "Creation Date",
            "fieldname": "creation_date",
            "fieldtype": "Date",
            "width": 180,
        },
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 130,
        },
        {
            "label": "Batch No",
            "fieldname": "batch_no",
            "fieldtype": "Link",
            "options": "Batch",
            "width": 100,
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Reference Type",
            "fieldname": "reference_type",
            "fieldtype": "Link",
            "options": "DocType",
            "width": 150,
        },
        {
            "label": "Reference Name",
            "fieldname": "reference_name",
            "fieldtype": "Dynamic Link",
            "options": "reference_type",
            "width": 150,
        },
        {
            "label": "Qty",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100,
        },
    ]
    return columns


def get_data(filters):
    data = []
    if filters.get("batch"):
        data = get_batch_info(filters.get("batch"))
    return data
