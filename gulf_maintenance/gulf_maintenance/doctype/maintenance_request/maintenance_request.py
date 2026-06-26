# Copyright (c) 2026, Mubashir Bashir and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class MaintenanceRequest(Document):
	def validate(self):
		self.calculate_parts_cost()
		self.apply_workflow_side_effects()

	def apply_workflow_side_effects(self):
		"""Set the fields that specific workflow transitions are supposed to set.

		We detect the transition by comparing the in-memory workflow_state with the
		last-saved one, so a field is only stamped on the exact transition that owns
		it (e.g. parts_approved is set ONLY when a Manager moves the doc from
		'Awaiting Approval' to 'In Progress' via Approve Parts).
		"""
		before = self.get_doc_before_save()
		prev_state = before.workflow_state if before else None

		# Approve Parts: Awaiting Approval -> In Progress
		if self.workflow_state == "In Progress" and prev_state == "Awaiting Approval":
			self.parts_approved = 1

		# Customer Sign-off: Completed -> Signed Off
		if self.workflow_state == "Signed Off" and prev_state == "Completed":
			self.customer_signoff = 1
			if not self.signoff_date:
				self.signoff_date = today()

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
