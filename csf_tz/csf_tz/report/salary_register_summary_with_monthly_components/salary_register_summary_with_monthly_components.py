
import frappe
import erpnext
from frappe.utils import flt, getdate
from frappe import _, msgprint
from frappe.utils.nestedset import get_descendants_of

import calendar

def execute(filters=None):
	company_currency = erpnext.get_company_currency(filters.get("company"))

	prev_first_date, prev_last_date, prev_month, prev_year = get_prev_month_date(filters)

	prev_salary_slips = get_prev_salary_slips(filters, company_currency, prev_first_date, prev_last_date)

	
	columns = get_columns(filters, prev_month, prev_year)
	data = get_data(filters, company_currency, prev_salary_slips)

	return columns, data

def get_columns(filters, prev_month, prev_year):
	cur_month_name = calendar.month_name[getdate(filters.from_date).month]
	cur_year = getdate(filters.from_date).year

	prev_month_name = calendar.month_name[prev_month]

	columns = [
		{
			"fieldname": "salary_component",
			"label": _("Salary Component"),
			"fieldtype": "Data",
			"width": 300
		},
		{
			"fieldname": "total_prev_month",
			"label": _("{0} {1}".format(prev_month_name, prev_year)),
			"fieldtype": "Float",
			"width": 300,
			"precision": 2
		},
		{
			"fieldname": "total_cur_month",
			"label": _("{0} {1}".format(cur_month_name, cur_year)),
			"fieldtype": "Float",
			"width": 300,
			"precision": 2
		}
	]
	return columns


def get_data(filters, company_currency, prev_salary_slips):
	records = []
	currency = None
	if filters.get('currency'):
		currency = filters.get('currency')

	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return []

	records.append({
		"salary_component": "Total Employees",
		"total_prev_month": len(prev_salary_slips),
		"total_cur_month": len(salary_slips)
	})
	records.append({"salary_component": "", "total_prev_month": "", "total_cur_month": ""})

	prev_ss_basic, prev_ss_earnings, prev_ss_deductions = get_salary_map(prev_salary_slips)

	basic_data, total_prev_basic, total_cur_basic = get_basic_data(records, salary_slips, currency, company_currency, prev_ss_basic)
	
	earnings_data, total_prev_earning, total_cur_earning = get_earnings_data(basic_data, salary_slips, currency, company_currency, prev_ss_earnings)

	cur_gross_pay = total_cur_earning + total_cur_basic
	prev_gross_pay = total_prev_earning + total_prev_basic

	earnings_data.append({
		"salary_component": "GROSS PAY",
		"total_prev_month": prev_gross_pay,
		"total_cur_month": cur_gross_pay
	})

	data = get_deduction_data(earnings_data, salary_slips, currency, company_currency, prev_ss_deductions, cur_gross_pay, prev_gross_pay)
	
	return data


def get_basic_data(data, salary_slips, currency, company_currency, prev_ss_basic):
	ss_basic_map = get_ss_basic_map(salary_slips, currency, company_currency)
	
	total_cur_basic = 0
	unique_cur_basic_salary_components = []
	unique_prev_basic_salary_components = []
	total_prev_basic = sum(flt(d.total_prev_month) for d  in prev_ss_basic)
	for cur_basic_row in ss_basic_map:
		total_cur_basic += cur_basic_row["total_cur_month"]

		for prev_basic_row in prev_ss_basic:
			if cur_basic_row.get("salary_component") == prev_basic_row.get("salary_component"):
				cur_basic_row.update({"total_prev_month": prev_basic_row.get("total_prev_month")})
				data.append(cur_basic_row)

				unique_cur_basic_salary_components.append(cur_basic_row.get("salary_component"))
				unique_prev_basic_salary_components.append(prev_basic_row.get("salary_component"))

		if cur_basic_row.get("salary_component") not in unique_cur_basic_salary_components:
			unique_cur_basic_salary_components.append(cur_basic_row.get("salary_component"))

			data.append({
				"salary_component": cur_basic_row.get("salary_component"),
				"total_prev_month": 0,
				"total_cur_month": cur_basic_row.get("total_cur_month") or 0
			})
	
	for row in prev_ss_basic:
		if row.salary_component not in unique_prev_basic_salary_components:
			data.append({
				"salary_component": row.get("salary_component"),
				"total_prev_month": row.get("total_prev_month") or 0,
				"total_cur_month": 0
			})
	
	return data, total_prev_basic, total_cur_basic


def get_earnings_data(data, salary_slips, currency, company_currency, prev_ss_earnings):
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)

	total_cur_earning = 0
	unique_cur_earnings_salary_components = []
	unique_prev_earnings_salary_components = []
	total_prev_earning = sum(flt(d.total_prev_month) for d  in prev_ss_earnings)
	for cur_earning_row in ss_earning_map:
		total_cur_earning += cur_earning_row["total_cur_month"]

		for prev_earning_row in prev_ss_earnings:
			if cur_earning_row.get("salary_component") == prev_earning_row.get("salary_component"):
				cur_earning_row.update({"total_prev_month": prev_earning_row.get("total_prev_month")})
				data.append(cur_earning_row)

				unique_cur_earnings_salary_components.append(cur_earning_row.get("salary_component"))
				unique_prev_earnings_salary_components.append(prev_earning_row.get("salary_component"))


		if cur_earning_row.get("salary_component") not in unique_cur_earnings_salary_components:
			unique_cur_earnings_salary_components.append(cur_earning_row.get("salary_component"))

			data.append({
				"salary_component": cur_earning_row.get("salary_component"),
				"total_prev_month": 0,
				"total_cur_month": cur_earning_row.get("total_cur_month") or 0
			})
	
	for row in prev_ss_earnings:
		if row.salary_component not in unique_prev_earnings_salary_components:
			data.append({
				"salary_component": row.get("salary_component"),
				"total_prev_month": row.get("total_prev_month") or 0,
				"total_cur_month": 0
			})
	
	data.append({
		"salary_component": "Total Allowances",
		"total_prev_month": total_prev_earning,
		"total_cur_month": total_cur_earning
	})

	return data, total_prev_earning, total_cur_earning


def get_deduction_data(data, salary_slips, currency, company_currency, prev_ss_deductions, cur_gross_pay, prev_gross_pay):
	ss_deduction_map = get_ss_ded_map(salary_slips, currency, company_currency)

	total_cur_deduction = 0
	unique_cur_deduction_salary_components = []
	unique_prev_deduction_salary_components = []
	total_prev_deduction = sum(flt(d.total_prev_month) for d  in prev_ss_deductions)
	for cur_deduction_row in ss_deduction_map:
		total_cur_deduction += cur_deduction_row["total_cur_month"]

		for prev_deduction_row in prev_ss_deductions:
			if cur_deduction_row.get("salary_component") == prev_deduction_row.get("salary_component"):
				cur_deduction_row.update({"total_prev_month": prev_deduction_row.get("total_prev_month")})
				data.append(cur_deduction_row)

				unique_cur_deduction_salary_components.append(cur_deduction_row.get("salary_component"))
				unique_prev_deduction_salary_components.append(prev_deduction_row.get("salary_component"))

		
		if cur_deduction_row.get("salary_component") not in unique_cur_deduction_salary_components:
			unique_cur_deduction_salary_components.append(cur_deduction_row.get("salary_component"))

			data.append({
				"salary_component": cur_deduction_row.get("salary_component"),
				"total_prev_month": 0,
				"total_cur_month": cur_deduction_row.get("total_cur_month") or 0
			})
	
	
	for row in prev_ss_deductions:
		if row.salary_component not in unique_prev_deduction_salary_components:
			data.append({
				"salary_component": row.get("salary_component"),
				"total_prev_month": row.get("total_prev_month"),
				"total_cur_month": 0
			})
	
	data.append({
		"salary_component": "Total Deductions",
		"total_prev_month": total_prev_deduction,
		"total_cur_month": total_cur_deduction
	})

	data.append({
		"salary_component": "NET PAY BEFORE LOAN",
		"total_prev_month": prev_gross_pay + total_prev_deduction,
		"total_cur_month": cur_gross_pay + total_cur_deduction
	})

	return data


def get_prev_month_date(filters):
	prev_month = getdate(filters.from_date).month - 1
	prev_year = getdate(filters.from_date).year

	if prev_month == 0:
		prev_month = 12
		prev_year = prev_year - 1

	prev_first_date =  getdate(str(prev_year) + "-" + str(prev_month) + "-" + "01")
	prev_last_date = getdate(str(prev_year) + "-" + str(prev_month) + "-" + "{0}".format(calendar.monthrange(prev_year, prev_month)[1]))

	return prev_first_date, prev_last_date, prev_month, prev_year


def get_salary_map(prev_salary_slips):
	prev_ss_basic = frappe.db.sql("""
        SELECT sd.salary_component, SUM(sd.amount) as total_prev_month 
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name 
        AND sd.parent in (%s)
        AND do_not_include_in_total = 0
        AND sd.parentfield = 'earnings' 
        AND sd.salary_component = 'Basic'
        GROUP BY sd.salary_component 
        ORDER BY sd.salary_component ASC
	""" % (', '.join(['%s']*len(prev_salary_slips))), tuple([d.name for d in prev_salary_slips]), as_dict=1)

	prev_ss_earnings = frappe.db.sql("""
        SELECT sd.salary_component, SUM(sd.amount) as total_prev_month 
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name 
        AND sd.parent in (%s)
        AND do_not_include_in_total = 0 
        AND sd.parentfield = 'earnings' 
        AND sd.salary_component != 'Basic'
        GROUP BY sd.salary_component 
        ORDER BY sd.salary_component ASC
	""" % (', '.join(['%s']*len(prev_salary_slips))), tuple([d.name for d in prev_salary_slips]), as_dict=1)

	prev_ss_deductions = frappe.db.sql("""
        SELECT sd.salary_component, SUM(sd.amount) * -1 as total_prev_month 
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name AND sd.parent in (%s)
        AND do_not_include_in_total = 0 
        AND sd.parentfield = 'deductions' 
        GROUP BY sd.salary_component 
        ORDER BY sd.salary_component ASC
	""" % (', '.join(['%s']*len(prev_salary_slips))), tuple([d.name for d in prev_salary_slips]), as_dict=1)

	return prev_ss_basic, prev_ss_earnings, prev_ss_deductions


def get_prev_salary_slips(filters, company_currency, prev_first_date, prev_last_date):
	custom_filters = filters
	custom_filters.update({
		"prev_first_date": prev_first_date,
		"prev_last_date": prev_last_date
	})
	prev_conditions = get_prev_conditions(custom_filters, company_currency)
	prev_salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by employee"""% prev_conditions, filters, as_dict=1)

	return prev_salary_slips or []


def get_prev_conditions(filters, company_currency):
    conditions = ""
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    if filters.get("docstatus"):
        conditions += "docstatus = {0}".format(
            doc_status[filters.get("docstatus")])

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
        department_list = get_departments(
            filters.get("department"), filters.get("company"))
        conditions += 'and department in (' + ','.join(
            ("'"+n+"'" for n in department_list)) + ')'

    return conditions


def get_salary_slips(filters, company_currency):
    filters.update({"from_date": filters.get("from_date"),
                    "to_date": filters.get("to_date")})
    conditions, filters = get_conditions(filters, company_currency)
    salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
        order by employee""" % conditions, filters, as_dict=1)

    return salary_slips or []


def get_ss_basic_map(salary_slips, currency, company_currency):
    ss_basic = frappe.db.sql("""
        SELECT sd.salary_component, SUM(sd.amount) as total_cur_month 
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name 
        AND sd.parent in (%s)
        AND do_not_include_in_total = 0 
        AND sd.parentfield = 'earnings' 
        AND sd.salary_component = 'Basic'
        GROUP BY sd.salary_component 
        ORDER BY sd.salary_component ASC""" %
                             (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

    return ss_basic


def get_ss_earning_map(salary_slips, currency, company_currency):
    ss_earnings = frappe.db.sql("""
        SELECT sd.salary_component, SUM(sd.amount) as total_cur_month 
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name 
        AND sd.parent in (%s)
        AND do_not_include_in_total = 0 
        AND sd.parentfield = 'earnings' 
        AND sd.salary_component != 'Basic'
        GROUP BY sd.salary_component 
        ORDER BY sd.salary_component ASC""" %
                                (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

    return ss_earnings


def get_ss_ded_map(salary_slips, currency, company_currency):
    ss_deductions = frappe.db.sql("""
        SELECT sd.salary_component, SUM(sd.amount) * -1 as total_cur_month 
        FROM `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name AND sd.parent in (%s)
        AND do_not_include_in_total = 0 
        AND sd.parentfield = 'deductions' 
        GROUP BY sd.salary_component 
        ORDER BY sd.salary_component ASC""" %
                                  (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)
    return ss_deductions


def get_conditions(filters, company_currency):
    conditions = ""
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    if filters.get("docstatus"):
        conditions += "docstatus = {0}".format(
            doc_status[filters.get("docstatus")])

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
        department_list = get_departments(
            filters.get("department"), filters.get("company"))
        conditions += 'and department in (' + ','.join(
            ("'"+n+"'" for n in department_list)) + ')'

    return conditions, filters


def get_departments(department,company):
    departments_list = get_descendants_of("Department", department)
    departments_list.append(department)
    return departments_list