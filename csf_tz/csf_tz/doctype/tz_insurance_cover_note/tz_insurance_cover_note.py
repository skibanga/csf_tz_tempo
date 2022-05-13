# Copyright (c) 2022, Aakvatech and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.model.document import Document

class TZInsuranceCoverNote(Document):
	pass

@frappe.whitelist()
def update_covernote_docs():
	"""Create or Update covernote document after getting necessary details from tira

	The routine to create or update covernote document runs on 00:00 am, 1st date of every month
	Forexample:
		for June: a routine will run on 00:00 am, June 1, 2022
	"""

	motor_vehicles = frappe.get_all('Vehicle', 'name')
	
	for vehicle in motor_vehicles:
		req = get_covernote_details(vehicle.name)
		try:
			for record in req.get('data'):
				if not frappe.db.exists('TZ Insurance Cover Note', record['coverNoteNumber']):
					doc = frappe.new_doc('TZ Insurance Cover Note')
				else:
					doc = frappe.get_doc('TZ Insurance Cover Note', record['coverNoteNumber'])
				
				for key, value in record.items():
					
					if key.lower() == 'motor':
						doc.insurance_motors = []
						doc.append('insurance_motors', {h.lower(): v for  h, v in value.items()})
					
					if key.lower() == 'company':
						doc.insurance_provider = []
						doc.append('insurance_provider', {
							h.lower(): json.dumps(v) if h == 'shareholders' else v for  h, v in value.items()
						})
					
					if key.lower() == 'policyholders':
						doc.policy_holders = []
						for i, row in enumerate(value):
							doc.append('policy_holders', {h.lower(): v for  h, v in row.items()})
					
					if key.lower() not in ['company', 'motor', 'policyholders']:
						doc.update({key.lower(): value})
					
				doc.vehicle = vehicle.name
				doc.save(ignore_permissions=True)
		
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), str(e))
	
	frappe.db.commit()
	return True

def get_covernote_details(regnumber):
	"""Fetch motor insurance details from tira

	:param regnumber: car registration number
	"""
	url = "https://tiramis.tira.go.tz/covernote/api/public/portal/verify"

	payload = json.dumps({
        "paramType": 2,
        "searchParam": regnumber
    })
	headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

	try:
		response = requests.post(url, headers=headers, data=payload, timeout=3000, verify=False)
		if response.status_code == 200:
			return json.loads(response.text)
		else:
			frappe.log_error(response.text, str(response.status_code))

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), str(e))


