# # ict_helpdesk/api/session.py

# import frappe

# def custom_boot_session(bootinfo):
#     """Redirect web users to role-based home pages, but keep Desk users in /app."""
#     user = frappe.session.user

#     # Skip system and guest users
#     if user in ("Guest",):
#         return

#     # Detect login context
#     user_type = frappe.db.get_value("User", user, "user_type")
#     # user_type = "System User" (Desk) or "Website User" (Portal)

#     # Only apply redirects for Website Users
#     if user_type == "Website User":
#         roles = frappe.get_roles(user)
#         if "Requester" in roles:
#             bootinfo["home_page"] = "/ticket"
#         elif "Director" in roles:
#             bootinfo["home_page"] = "/director-page"
#         elif "Administrator" in roles:
#             bootinfo["home_page"] = "/admin-dashboard"
#         else:
#             bootinfo["home_page"] = "/"
