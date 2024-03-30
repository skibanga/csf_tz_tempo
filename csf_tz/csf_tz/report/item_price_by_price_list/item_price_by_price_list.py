# Copyright (c) 2024, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _, db
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    # Dynamically fetch Price Lists for dynamic column creation
    price_lists = db.get_list("Price List", filters={"selling": 1}, pluck="name")
    price_list_columns = [
        {
            "label": _(f"{price_list} Excl"),
            "fieldname": f"rate_{price_list.replace(' ', '_').lower()}_excl",
            "fieldtype": "Currency",
        }
        for price_list in price_lists
    ]
    price_list_columns += [
        {
            "label": _(f"{price_list} Rate"),
            "fieldname": f"rate_{price_list.replace(' ', '_').lower()}",
            "fieldtype": "Currency",
        }
        for price_list in price_lists
    ]
    columns = (
        [
            {
                "label": _("Item Code"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 150,
            },
            {
                "label": _("Item Description"),
                "fieldname": "description",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": _("Default Item Tax Template"),
                "fieldname": "default_tax_template",
                "fieldtype": "Link",
                "options": "Item Tax Template",
                "width": 200,
            },
        ]
        + price_list_columns
        + [
            {
                "label": _("Total Qty"),
                "fieldname": "total_qty",
                "fieldtype": "Float",
                "width": 100,
            },
            {
                "label": _("Last Purchase Rate"),
                "fieldname": "last_purchase_rate",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "label": _("Valuation Rate"),
                "fieldname": "valuation_rate",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "label": _("Warehouse Qty"),
                "fieldname": "warehouse_qty",
                "fieldtype": "Data",
                "width": 120,
            },
        ]
    )
    return columns


def get_data(filters):
    conditions = ""
    if filters.get("item_description"):
        conditions += f""" AND (i.description LIKE '%{filters["item_description"]}%' OR i.item_code = '{filters["item_description"]}')"""

    # Example SQL Query to fetch data
    sql = f"""
        SELECT
            i.item_code,
            i.description,
            i.default_tax_template,
            SUM(b.actual_qty) as total_qty,
            i.last_purchase_rate,
            b.valuation_rate,
            GROUP_CONCAT(CONCAT(b.warehouse, ' - ', CAST(b.actual_qty AS INTEGER), '<br>')) as warehouse_qty
        FROM
            `tabItem` i
        LEFT OUTER JOIN `tabBin` b ON i.item_code = b.item_code
        WHERE i.disabled = 0
            AND i.is_sales_item = 1 {conditions}
        GROUP BY i.item_code
    """
    data = db.sql(
        sql,
        as_dict=1,
    )

    # Add price list rates
    for d in data:
        for price_list in db.get_list(
            "Price List", filters={"selling": 1}, pluck="name"
        ):
            rate = db.get_value(
                "Item Price",
                {"item_code": d.item_code, "price_list": price_list},
                "price_list_rate",
            )
            d[f"rate_{price_list.replace(' ', '_').lower()}"] = rate if rate else 0.0
            d[f"rate_{price_list.replace(' ', '_').lower()}_excl"] = (
                rate / (1 + (flt(filters["tax_rate"]) / 100)) if rate else 0.0
            )

    return data
