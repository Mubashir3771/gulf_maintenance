app_name = "gulf_maintenance"
app_title = "Gulf Maintenance"
app_publisher = "Mubashir Bashir"
app_description = "Gulf Maintenance"
app_email = "bashirmubashir798@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "gulf_maintenance",
		"logo": "/assets/gulf_maintenance/logo.svg",
		"title": "Gulf Maintenance",
		"route": "/desk/gulf-maintenance",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gulf_maintenance/css/gulf_maintenance.css"
# app_include_js = "/assets/gulf_maintenance/js/gulf_maintenance.js"

# include js, css files in header of web template
# web_include_css = "/assets/gulf_maintenance/css/gulf_maintenance.css"
# web_include_js = "/assets/gulf_maintenance/js/gulf_maintenance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gulf_maintenance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "gulf_maintenance/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "gulf_maintenance.utils.jinja_methods",
# 	"filters": "gulf_maintenance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "gulf_maintenance.install.before_install"
after_install = "gulf_maintenance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "gulf_maintenance.uninstall.before_uninstall"
# after_uninstall = "gulf_maintenance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "gulf_maintenance.utils.before_app_install"
# after_app_install = "gulf_maintenance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "gulf_maintenance.utils.before_app_uninstall"
# after_app_uninstall = "gulf_maintenance.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "gulf_maintenance.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gulf_maintenance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"gulf_maintenance.tasks.all"
# 	],
# 	"daily": [
# 		"gulf_maintenance.tasks.daily"
# 	],
# 	"hourly": [
# 		"gulf_maintenance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"gulf_maintenance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"gulf_maintenance.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "gulf_maintenance.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "gulf_maintenance.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gulf_maintenance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "gulf_maintenance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gulf_maintenance.utils.before_request"]
# after_request = ["gulf_maintenance.utils.after_request"]

# Job Events
# ----------
# before_job = ["gulf_maintenance.utils.before_job"]
# after_job = ["gulf_maintenance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"gulf_maintenance.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


# Fixtures
# --------
# Export this app's DB-stored configuration to git. Each entry is filtered so we
# only ever ship records this app owns — never unrelated/global records.
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Maintenance User", "Maintenance Technician", "Maintenance Manager"]]],
	},
	{
		"dt": "Workflow",
		"filters": [["name", "=", "Maintenance Request"]],
	},
	{
		"dt": "Workflow State",
		"filters": [["name", "in", [
			"Draft", "Assigned", "Awaiting Approval", "In Progress",
			"Completed", "Signed Off", "Billed",
		]]],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", [
			"Assign", "Submit for Approval", "Approve Parts", "Reject",
			"Start Work", "Mark Complete", "Customer Sign-off", "Create Invoice",
		]]],
	},
	{
		"dt": "Server Script",
		"filters": [["name", "=", "Maintenance Parts Approval Gate"]],
	},
	{
		"dt": "Client Script",
		"filters": [["name", "=", "Maintenance Request - Billing & Filters"]],
	},
	{
		"dt": "Notification",
		"filters": [["name", "=", "Maintenance Approval Required"]],
	},
	{
		"dt": "Workspace",
		"filters": [["name", "=", "Gulf Maintenance"]],
	},
]

