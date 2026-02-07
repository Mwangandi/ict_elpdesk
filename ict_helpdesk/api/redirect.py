import frappe

def custom_login_redirect():
    """Redirect all users after login to /ict-helpdesk web page."""
    if frappe.session.user == "Guest":
        return "/login"
    return "/ict-helpdesk"


def login_redirect(login_manager=None):
    """Redirect Requester role users to /tickets after login or OTP."""
    try:
        # Prefer login_manager.user (passed by bench triggers), fallback to session
        user = None
        if login_manager and getattr(login_manager, "user", None):
            user = login_manager.user
        else:
            user = frappe.session.user

        # nothing to do for Guest
        if not user or user in ("Guest", "Administrator"):
            frappe.logger("ict_helpdesk").debug(f"login_redirect: skipping for user={user}")
            return

        # roles (safe)
        roles = frappe.get_roles(user) or []

        # role_profile via DB (bypass permission checks)
        role_profile = frappe.db.get_value("User", user, "role_profile_name")

        # debug log (remove later)
        frappe.logger("ict_helpdesk").info(
            f"login_redirect: user={user} roles={roles} role_profile={role_profile}"
        )

        # redirect condition
        if "Requester" in roles or role_profile == "Requester":
            # set redirect
            frappe.local.response["redirect_to"] = "/tickets"
            frappe.local.flags.redirect_location = "/tickets"
        else:
            frappe.logger("ict_helpdesk").debug(f"login_redirect: no redirect for {user}")
    except Exception as e:
        # ensure errors don't break login flow
        frappe.logger("ict_helpdesk").exception(f"login_redirect error: {e}")
