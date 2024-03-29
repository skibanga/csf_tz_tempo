// Copyright (c) 2023, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Price by Price List"] = {
	"filters": [
		{
			"fieldname": "item_description",
			"label": __("Item Description"),
			"fieldtype": "Data",
			"default": "",
			"wildcard_filter": 1,
			"mandatory": 1,
		}
	]
}