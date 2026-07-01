# Copyright (c) 2026, Mubashir Bashir and contributors
# For license information, please see license.txt

from frappe import _


def get_data():
	"""Show the Sales Invoice(s) raised from this request in the form's
	Connections tab. The link is resolved through the Sales Invoice
	`maintenance_request` field, so no reference is stored on the request."""
	return {
		"fieldname": "maintenance_request",
		"transactions": [
			{"label": _("Billing"), "items": ["Sales Invoice"]},
		],
	}
