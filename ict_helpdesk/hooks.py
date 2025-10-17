app_name = "ict_helpdesk"
app_title = "Ict Helpdesk"
app_publisher = "Pantech Solutions"
app_description = "Helpdesk App for ict department"
app_email = "pantechsupprt@gmail.com"
app_license = "mit"

# Apps
# ------------------

required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "ict_helpdesk",
		"logo": "/assets/ict_helpdesk/logo.png",
		"title": "Ict Helpdesk",
		"route": "/ict_helpdesk",
		"has_permission": "ict_helpdesk.api.permission.has_app_permission"
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ict_helpdesk/css/ict_helpdesk.css"
# app_include_js = "/assets/ict_helpdesk/js/ict_helpdesk.js"

# include js, css files in header of web template
# web_include_css = "/assets/ict_helpdesk/css/ict_helpdesk.css"
# web_include_js = "/assets/ict_helpdesk/js/ict_helpdesk.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ict_helpdesk/public/scss/website"

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
# app_include_icons = "ict_helpdesk/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ict_helpdesk.utils.jinja_methods",
# 	"filters": "ict_helpdesk.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ict_helpdesk.install.before_install"
# after_install = "ict_helpdesk.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ict_helpdesk.uninstall.before_uninstall"
# after_uninstall = "ict_helpdesk.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ict_helpdesk.utils.before_app_install"
# after_app_install = "ict_helpdesk.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ict_helpdesk.utils.before_app_uninstall"
# after_app_uninstall = "ict_helpdesk.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ict_helpdesk.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
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
# 		"ict_helpdesk.tasks.all"
# 	],
# 	"daily": [
# 		"ict_helpdesk.tasks.daily"
# 	],
# 	"hourly": [
# 		"ict_helpdesk.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ict_helpdesk.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ict_helpdesk.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ict_helpdesk.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ict_helpdesk.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ict_helpdesk.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ict_helpdesk.utils.before_request"]
# after_request = ["ict_helpdesk.utils.after_request"]

# Job Events
# ----------
# before_job = ["ict_helpdesk.utils.before_job"]
# after_job = ["ict_helpdesk.utils.after_job"]

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
# 	"ict_helpdesk.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# custom register form
website_route_rules = [
    {"from_route": "/signup", "to_route": "/register"}
]

# app_include_css = "/public/css/edit_login.css"
# website_include_css = ["/assets/ict_helpdesk/css/edit_login.css"]

# website_include_js = ["/assets/ict_helpdesk/js/edit_login.js"]

doc_events = {
    "ICT Ticket": {
        "on_update": "ict_helpdesk.api.notification.send_notification"
    },
    "User": {
        "after_insert": "ict_helpdesk.api.user_hooks.set_default_user_settings"
    }
}

# ict_helpdesk/hooks.py
# boot_session = "ict_helpdesk.api.session.custom_boot_session"

homepage = "ict-helpdesk"

website_route_redirects = [
    {"source": "/app", "target": "/ict-helpdesk"},
]

# login_manager = "ict_helpdesk.api.redirect.custom_login_redirect"

# login_redirect = "ict_helpdesk.api.redirect.custom_login_redirect"


