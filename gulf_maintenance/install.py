# Copyright (c) 2026, Mubashir Bashir and contributors
# For license information, please see license.txt

import frappe

LABOUR_ITEM_CODE = "Maintenance Labour"

ROLES = ["Maintenance User", "Maintenance Technician", "Maintenance Manager"]

WORKFLOW_STATES = [
	"Draft", "Assigned", "Awaiting Approval", "In Progress",
	"Completed", "Signed Off", "Billed",
]
WORKFLOW_ACTIONS = [
	"Assign", "Submit for Approval", "Approve Parts", "Reject",
	"Start Work", "Mark Complete", "Customer Sign-off", "Create Invoice",
]


def after_install():
	"""Make the build self-contained on a fresh install.

	Order matters: fixtures are imported (alphabetically) AFTER this hook runs, and
	the Workflow fixture (`workflow.json`) links to Workflow State / Workflow Action
	Master records. Those masters sort *after* `workflow.json`, so we must create
	them here first or the Workflow fixture import fails with LinkValidationError.
	Same for the roles the DocType permissions and Workflow transitions reference.
	"""
	create_roles()
	setup_workflow_masters()
	create_labour_item()
	setup_role_permissions()


def create_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
				ignore_permissions=True
			)
	frappe.db.commit()


def setup_workflow_masters():
	"""Pre-create the custom Workflow State / Action Master records the Workflow
	fixture depends on (the fixture re-imports them with full definitions)."""
	for state in WORKFLOW_STATES:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state}).insert(
				ignore_permissions=True
			)
	for action in WORKFLOW_ACTIONS:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc(
				{"doctype": "Workflow Action Master", "workflow_action_name": action}
			).insert(ignore_permissions=True)
	frappe.db.commit()


# Read access the maintenance roles need so the Maintenance Request form is usable
# (selecting customer / equipment owner / technician / parts item & warehouse) and
# so the office can raise the draft invoice.
ROLE_PERMISSIONS = {
	# doctype: { role: [ptypes] }
	"Customer": {
		"Maintenance User": ["read"],
		"Maintenance Technician": ["read"],
		"Maintenance Manager": ["read"],
	},
	"Item": {
		"Maintenance User": ["read"],
		"Maintenance Technician": ["read"],
		"Maintenance Manager": ["read"],
	},
	"Warehouse": {
		"Maintenance User": ["read"],
		"Maintenance Technician": ["read"],
		"Maintenance Manager": ["read"],
	},
	"Employee": {
		"Maintenance User": ["read"],
		"Maintenance Technician": ["read"],
		"Maintenance Manager": ["read"],
	},
	# Office raises the DRAFT invoice; posting (submit) stays an Accounts function.
	"Sales Invoice": {
		"Maintenance User": ["read", "write", "create"],
		"Maintenance Manager": ["read"],
	},
}


def setup_role_permissions():
	from frappe.permissions import add_permission, update_permission_property

	for doctype, role_map in ROLE_PERMISSIONS.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for role, ptypes in role_map.items():
			# create the row (idempotent — add_permission no-ops if it already exists)
			if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role, "permlevel": 0}):
				add_permission(doctype, role, 0)
			for ptype in ptypes:
				update_permission_property(doctype, role, 0, ptype, 1, validate=False)
	frappe.db.commit()


def create_labour_item():
	if frappe.db.exists("Item", LABOUR_ITEM_CODE):
		return

	# Ensure the "Services" item group exists (it ships with ERPNext, but be safe).
	if not frappe.db.exists("Item Group", "Services"):
		root = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ["in", ["", None]]}, "name") or "All Item Groups"
		frappe.get_doc({
			"doctype": "Item Group",
			"item_group_name": "Services",
			"parent_item_group": root,
			"is_group": 0,
		}).insert(ignore_permissions=True)

	frappe.get_doc({
		"doctype": "Item",
		"item_code": LABOUR_ITEM_CODE,
		"item_name": LABOUR_ITEM_CODE,
		"item_group": "Services",
		"stock_uom": "Hour" if frappe.db.exists("UOM", "Hour") else "Nos",
		"is_stock_item": 0,
		"is_sales_item": 1,
		"is_purchase_item": 0,
		"description": "Maintenance labour billed by the hour.",
	}).insert(ignore_permissions=True)
	frappe.db.commit()
