# Copyright (c) 2026, Mubashir Bashir and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class MaintenanceRequest(Document):
	def validate(self):
		self.calculate_parts_cost()
		self.reset_approval_on_parts_change()
		self.apply_workflow_side_effects()

	def before_submit(self):
		"""'Billed' is the only submitted state and must be reached through the
		'Create Sales Invoice' action (which creates the linked invoice first).
		Block the bare workflow action from billing a request with no invoice."""
		has_invoice = frappe.db.exists(
			"Sales Invoice", {"maintenance_request": self.name, "docstatus": ["<", 2]}
		)
		if not has_invoice:
			frappe.throw(
				_("Use the 'Create Sales Invoice' button — a request cannot be billed "
				  "without its Sales Invoice.")
			)

	def apply_workflow_side_effects(self):
		"""Set the fields that specific workflow transitions are supposed to set.

		The previous state is read from the committed DB value (reliable for both UI
		workflow actions and programmatic saves), so a field is only stamped on the
		exact transition that owns it (e.g. parts_approved is set ONLY when a Manager
		moves the doc from 'Awaiting Approval' to 'In Progress' via Approve Parts).
		"""
		prev_state = None if self.is_new() else self.get_db_value("workflow_state")

		# Approve Parts: Awaiting Approval -> In Progress
		if self.workflow_state == "In Progress" and prev_state == "Awaiting Approval":
			self.parts_approved = 1

		# Customer Sign-off: Completed -> Signed Off
		if self.workflow_state == "Signed Off" and prev_state == "Completed":
			self.customer_signoff = 1
			if not self.signoff_date:
				self.signoff_date = today()

	def reset_approval_on_parts_change(self):
		"""Close the approval loophole: if the parts cost is raised after a manager
		approved it, drop `parts_approved` so the > PKR 10,000 gate re-triggers and
		the increased cost must be re-approved."""
		if self.is_new() or not self.parts_approved:
			return
		prev_total = flt(self.get_db_value("total_parts_cost"))
		if flt(self.total_parts_cost) > prev_total:
			self.parts_approved = 0

	def calculate_parts_cost(self):
		"""Keep child `amount` and parent `total_parts_cost` correct server-side.

		This is the authoritative computation; the client script mirrors it only
		for instant UX. Totals must never depend on the browser.
		"""
		total = 0.0
		for row in self.parts_used:
			row.amount = flt(row.qty) * flt(row.rate)
			total += flt(row.amount)
		self.total_parts_cost = total
