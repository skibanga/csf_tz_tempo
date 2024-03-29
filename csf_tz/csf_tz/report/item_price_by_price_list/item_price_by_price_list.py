# Copyright (c) 2024, Aakvatech and contributors
# For license information, please see license.txt

from frappe import _, db
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    # Dynamically fetch Price Lists for dynamic column creation
    price_lists = db.get_list("Price List", pluck="name")
    price_list_columns = [
        {
            "label": _(f"{price_list} Rate"),
            "fieldname": f"rate_{price_list.replace(' ', '_').lower()}",
            "fieldtype": "Currency",
            "width": 120,
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
        ]
    )
    return columns


def get_data(filters):
    conditions = ""
    if filters.get("item_description"):
        conditions += " AND i.description LIKE '%{}%'".format(
            filters["item_description"]
        )

    # Example SQL Query to fetch data
    data = db.sql(
        """
        SELECT
            i.item_code,
            i.description,
            i.default_tax_template,
            (SELECT SUM(bin.actual_qty) FROM `tabBin` bin WHERE bin.item_code=i.item_code) as total_qty,
            i.last_purchase_rate
        FROM
            `tabItem` i
        WHERE
            i.disabled = 0 {conditions}
    """.format(
            conditions=conditions
        ),
        as_dict=1,
    )

    # Add price list rates
    for d in data:
        for price_list in db.get_list("Price List", pluck="name"):
            rate = db.get_value(
                "Item Price",
                {"item_code": d.item_code, "price_list": price_list},
                "price_list_rate",
            )
            d[f"rate_{price_list.replace(' ', '_').lower()}"] = rate if rate else 0.0

    return data
