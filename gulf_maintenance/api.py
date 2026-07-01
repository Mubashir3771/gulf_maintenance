# Copyright (c) 2026, Mubashir Bashir and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

LABOUR_ITEM_CODE = "Maintenance Labour"


@frappe.whitelist()
def create_sales_invoice(maintenance_request):
	"""Create a DRAFT, Update-Stock Sales Invoice from a Signed-Off request.

	Parts become stock invoice lines (so inventory + COGS post on submit) and
	labour is added as a separate non-stock service line. The invoice is left as
	a Draft for the office to review before posting — no GL entries until submit.
	"""
	mr = frappe.get_doc("Maintenance Request", maintenance_request)

	# --- guards (be safe) ---
	if mr.workflow_state != "Signed Off":
		frappe.throw(_("Sales Invoice can only be created when the request is in 'Signed Off' state (current: {0}).").format(mr.workflow_state or "Draft"))

	existing = frappe.db.exists("Sales Invoice", {"maintenance_request": mr.name, "docstatus": ["<", 2]})
	if existing:
		frappe.throw(_("This request is already linked to Sales Invoice {0}.").format(existing))

	has_parts = bool(mr.parts_used)
	has_labour = flt(mr.hours_spent) > 0 and flt(mr.labour_rate) > 0
	if not has_parts and not has_labour:
		frappe.throw(_("Nothing to bill: add parts and/or record labour hours and rate first."))

	company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		frappe.throw(_("No default Company is configured. Set one in Global Defaults."))

	si = frappe.new_doc("Sales Invoice")
	si.customer = mr.customer
	si.company = company
	si.update_stock = 1
	si.maintenance_request = mr.name  # proper link back to the request (shown in its dashboard)

	# Parts -> stock lines (carry the warehouse so valuation/COGS hit the right bin)
	for row in mr.parts_used:
		if not row.item:
			continue
		si.append("items", {
			"item_code": row.item,
			"qty": flt(row.qty),
			"rate": flt(row.rate),
			"warehouse": row.warehouse,
		})

	# Labour -> separate non-stock service line
	if has_labour:
		si.append("items", {
			"item_code": LABOUR_ITEM_CODE,
			"qty": flt(mr.hours_spent),
			"rate": flt(mr.labour_rate),
		})

	si.insert(ignore_permissions=False)  # DRAFT only — do NOT submit

	# Advance the request to Billed via the workflow. 'Billed' is a submitted state
	# (docstatus 1), so this submits + locks the request. The SI links back through
	# its own `maintenance_request` field — nothing is stored on the request itself.
	from frappe.model.workflow import apply_workflow

	apply_workflow(mr, "Create Invoice")

	frappe.msgprint(_("Draft Sales Invoice {0} created.").format(si.name), alert=True)
	return si.name
