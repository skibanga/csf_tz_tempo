# Copyright (c) 2022, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from erpnext import get_company_currency
from frappe import _, msgprint
from frappe.utils import getdate, flt, cstr, cint
from frappe.utils.nestedset import get_descendants_of

import calendar

def execute(filters):
	company_currency = get_company_currency(filters.get("company"))

	prev_first_date, prev_last_date, prev_month, prev_year = get_prev_month_date(filters)
	cur_month_name = calendar.month_name[getdate(filters.from_date).month]
	cur_year = getdate(filters.from_date).year

	prev_month_name = calendar.month_name[prev_month]

	prev_salary_slips = get_prev_salary_slips(filters, company_currency, prev_first_date, prev_last_date)
	if len(prev_salary_slips) == 0:
		msgprint(_("No salary slip found for the previous month: {0} {1}".format(
			frappe.bold(calendar.month_name[prev_month]), frappe.bold(prev_year)))
		)
		return []

	
	columns = get_columns(filters, prev_month_name, cur_month_name, prev_year, cur_year)
	data, prev_ss_map, cur_ss_map = get_data(filters, company_currency, prev_salary_slips)
	report_summary = get_report_summary(prev_ss_map, cur_ss_map, prev_month_name, cur_month_name, prev_year, cur_year)

	return columns, data, None, None, report_summary

def get_columns(filters, prev_month_name, cur_month_name, prev_year, cur_year):
	columns = [
		{
			"fieldname": "employee",
			"label": _("Employee"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "employee_name",
			"label": _("Employee Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "department",
			"label": _("Department"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "total_basic_prev_month",
			"label": _("Basic {0}-{1}".format(prev_month_name, prev_year)),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "total_basic_cur_month",
			"label": _("Basic {0}-{1}".format(cur_month_name, cur_year)),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "basic_difference_amount",
			"label": _("Basic Difference Amount"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "total_earnings_prev_month",
			"label": _("Total Earnings {0}-{1}".format(prev_month_name, prev_year)),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "total_earnings_cur_month",
			"label": _("Total Earnings {0}-{1}".format(cur_month_name, cur_year)),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "earnings_difference_amount",
			"label": _("Earnings Difference Amount"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "total_deduction_prev_month",
			"label": _("Total Deduction {0}-{1}".format(prev_month_name, prev_year)),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "total_deduction_cur_month",
			"label": _("Total Deduction {0}-{1}".format(cur_month_name, cur_year)),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2
		},
		{
			"fieldname": "deduction_difference_amount",
			"label": _("Deduction Difference Amount"),
			"fieldtype": "Data",
			"width": 150
		},
	]
	return columns

def get_data(filters, company_currency, prev_salary_slips):
	salary_slips = get_cur_salary_slips(filters, company_currency)
	if len(salary_slips) == 0:
		msgprint(_("No salary slip found for the this month: {0} {1}".format(
			frappe.bold(calendar.month_name[getdate(filters.from_date).month]),
			frappe.bold(getdate(filters.from_date).year)))
		)
		return []
	
	prev_ss_map = get_prev_salary_map(prev_salary_slips)
	cur_ss_map = get_cur_salary_map(salary_slips)

	data = get_salary_details(prev_ss_map, cur_ss_map)

	return data, prev_ss_map, cur_ss_map

def get_report_summary(prev_ss_map, cur_ss_map, prev_month_name, cur_month_name, prev_year, cur_year):
	"""Show the summary of the report"""
	prev_no_employee = len(prev_ss_map)
	cur_no_employee = len(cur_ss_map)
	return [
		{
			"value": prev_no_employee,
			"indicator": "Green",
			"label": _("Total No of Employee for {0}-{1}".format(
				frappe.bold(prev_month_name),
				frappe.bold(prev_year)
			)),
			"datatype": "Int",
		},
		{
			"value": cur_no_employee,
			"indicator": "Green",
			"label": _("Total No of Employee for {0}-{1}".format(
				frappe.bold(cur_month_name),
				frappe.bold(cur_year)
			)),
			"datatype": "Int",
		},
	]

def get_salary_details(prev_ss, cur_ss):
	"""Merge employee details from current and previous months"""

	data = []
	unique_cur_employees = []
	unique_prev_employees = []
	for cur_ss_row in cur_ss:
		for prev_ss_row in prev_ss:
			if cur_ss_row.employee == prev_ss_row.employee:
				unique_prev_employees.append(prev_ss_row.get("employee"))
				unique_cur_employees.append(cur_ss_row.get("employee"))

				basic_amount_diff = flt(flt(cur_ss_row.get("basic_cur_month")) - flt(prev_ss_row.get("basic_prev_month")), 2)
				earnings_amount_diff = flt(flt(cur_ss_row.get("earnings_prev_month")) - flt(prev_ss_row.get("earnings_prev_month")), 2)
				deductions_amount_diff = flt(flt(cur_ss_row.get("deductions_prev_month")) - flt(prev_ss_row.get("deductions_prev_month")), 2)
				
				cur_ss_row.update({
					"total_basic_prev_month": prev_ss_row.get("total_basic_prev_month"),
					"total_earnings_prev_month": prev_ss_row.get("total_earnings_prev_month"),
					"total_deduction_prev_month": prev_ss_row.get("total_deduction_prev_month"),
					"basic_difference_amount": get_difference_amount_detail(basic_amount_diff),
					"earnings_difference_amount": get_difference_amount_detail(earnings_amount_diff),
					"deduction_difference_amount": get_difference_amount_detail(deductions_amount_diff)
				})
				data.append(cur_ss_row)

		# Update employee details for the current month if the employee is not in the list of employees for previous month
		if cur_ss_row.get("employee") not in unique_cur_employees:
			unique_cur_employees.append(cur_ss_row.get("employee"))
			cur_ss_row.update({
				"basic_difference_amount": "+ " + str(cur_ss_row.get("total_basic_cur_month")),
				"earnings_difference_amount": "+ " + str(cur_ss_row.get("total_earnings_cur_month")),
				"deduction_difference_amount": "+ " + str(cur_ss_row.get("total_deduction_cur_month"))
			})

			data.append(cur_ss_row)

	return update_unique_prev_employee_ss_details(data, prev_ss, unique_prev_employees)

def update_unique_prev_employee_ss_details(data, prev_ss, unique_prev_employees):
	""""Updating unique employee details of previous month if the employee is not in the list of employees for the current month"""

	for prev_row in prev_ss:
		if prev_row.get("employee") not in unique_prev_employees:
			unique_prev_employees.append(prev_row.get("employee"))
			prev_row.update({
				"basic_difference_amount": "+ " + str(prev_row.get("total_basic_prev_month")),
				"earnings_difference_amount": "+ " + str(prev_row.get("total_earnings_prev_month")),
				"deduction_difference_amount": "+ " + str(prev_row.get("total_deduction_prev_month"))
			})

			data.append(prev_row)
	return data

def get_difference_amount_detail(bsc_amount_diff):
	"""Show + or - sign on the amount difference between current and previous month"""

	result = ""
	if bsc_amount_diff > 0:
		result = "+" + cstr(bsc_amount_diff)
	elif bsc_amount_diff < 0:
		result = "-" + cstr(abs(bsc_amount_diff))
	else:
		result = "0"
	return result

def get_prev_salary_map(prev_salary_slips):
	"""Get amount details like total basic, total earnings, and total deductions from salary details for previous month"""

	return frappe.db.sql("""
        SELECT ss.employee, ss.employee_name, ss.department,
		SUM(IF((sd.parentfield = "earnings" AND sd.salary_component = "Basic"), sd.amount, 0)) AS total_basic_prev_month,
		SUM(IF((sd.parentfield = "earnings" AND sd.salary_component != "Basic"), sd.amount, 0)) AS total_earnings_prev_month,
		SUM(IF((sd.parentfield = "deductions"), sd.amount, 0)) AS total_deduction_prev_month
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name 
        AND sd.parent in (%s)
        AND sd.do_not_include_in_total = 0
		GROUP BY ss.employee
        ORDER BY ss.employee
	""" % (', '.join(['%s']*len(prev_salary_slips))), tuple([d.name for d in prev_salary_slips]), as_dict=1)

def get_cur_salary_map(salary_slips):
	"""Get amount details like total basic, total earnings, and total deductions from salary details for current month"""

	return frappe.db.sql("""
        SELECT ss.employee, ss.employee_name, ss.department,
		SUM(IF((sd.parentfield = "earnings" AND sd.salary_component = "Basic"), sd.amount, 0)) AS total_basic_cur_month,
		SUM(IF((sd.parentfield = "earnings" AND sd.salary_component != "Basic"), sd.amount, 0)) AS total_earnings_cur_month,
		SUM(IF((sd.parentfield = "deductions"), sd.amount, 0)) AS total_deduction_cur_month
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name 
        AND sd.parent in (%s)
        AND sd.do_not_include_in_total = 0
		GROUP BY ss.employee
        ORDER BY ss.employee
	""" % (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

def get_prev_salary_slips(filters, company_currency, prev_first_date, prev_last_date):
	"""Get submitted salary slips for precious month"""

	custom_filters = filters
	custom_filters.update({
		"prev_first_date": prev_first_date,
		"prev_last_date": prev_last_date
	})
	prev_conditions = get_prev_conditions(custom_filters, company_currency)
	prev_salary_slips = frappe.db.sql("""
		select name from `tabSalary Slip` where %s
		order by employee"""% 
	prev_conditions, filters, as_dict=1)

	return prev_salary_slips or []

def get_cur_salary_slips(filters, company_currency):
	"""Get salary slips for the current month"""

	filters.update({
		"from_date": filters.get("from_date"),
        "to_date": filters.get("to_date")
	})
	conditions, filters = get_cur_conditions(filters, company_currency)
	salary_slips = frappe.db.sql("""
		select name from `tabSalary Slip` where %s
        order by employee"""%
		conditions, filters, as_dict=1)
	
	return salary_slips or []

def get_prev_month_date(filters):
	"""Get date deatils for previous month"""

	prev_month = getdate(filters.from_date).month - 1
	prev_year = getdate(filters.from_date).year

	if prev_month == 0:
		prev_month = 12
		prev_year = prev_year - 1

	prev_first_date =  getdate(str(prev_year) + "-" + str(prev_month) + "-" + "01")
	prev_last_date = getdate(str(prev_year) + "-" + str(prev_month) + "-" + "{0}".format(
		calendar.monthrange(prev_year, prev_month)[1])
	)

	return prev_first_date, prev_last_date, prev_month, prev_year

def get_prev_conditions(filters, company_currency):
	"""Conditions that will be used to get salary slips for previous month"""
	
	# this is get submitted salary slips for the previous month
	conditions = "docstatus <= 1"

	if filters.get("prev_first_date"):
		conditions += " and start_date >= %(prev_first_date)s"
	if filters.get("prev_last_date"):
		conditions += " and end_date <= %(prev_last_date)s"
	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("employee"):
		conditions += " and employee = %(employee)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"
	if filters.get("department") and filters.get("company"):
		department_list = get_departments(filters.get("department"), filters.get("company"))
		conditions += 'and department in (' + ','.join(
            ("'"+n+"'" for n in department_list)) + ')'

	return conditions

def get_cur_conditions(filters, company_currency):
	"""Conditions that will be used to get salary slips for current month"""

	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if filters.get("from_date"):
		conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and end_date <= %(to_date)s"
	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("employee"):
		conditions += " and employee = %(employee)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"
	if filters.get("department") and filters.get("company"):
		department_list = get_departments(filters.get("department"), filters.get("company"))
		conditions += 'and department in (' + ','.join(
            ("'"+n+"'" for n in department_list)) + ')'

	return conditions, filters

def get_departments(department,company):
    departments_list = get_descendants_of("Department", department)
    departments_list.append(department)
    return departments_list