import frappe

def custom_login_redirect():
    """Redirect all users after login to /ict-helpdesk web page."""
    if frappe.session.user == "Guest":
        return "/login"
    return "/ict-helpdesk"