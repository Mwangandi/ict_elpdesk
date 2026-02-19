import frappe
# Before Insert, assign module profile
@frappe.whitelist(allow_guest=True)
def assign_module_profile(doc, method):
    try:
        # if doc.user_type != "Website User":
        #     # TODO: Change the message
        #     frappe.throw("Request Administrator to handle this for you!")
        #     return
        doc.module_profile = "Requester"
        doc.send_welcome_email = 1
    except Exception as e:
        frappe.log_error(
            f"Error setting up new user {doc.email}: {str(e)}", 
            "User Setup Error"
        )
            
        
# After Insert assign role profile
@frappe.whitelist(allow_guest=True)
def assign_role_profile(doc, method):
    try:
        # if doc.user_type != "Website User":
        #     frappe.throw("Please request administrator to handle this for you!")
        #     return
        doc.role_profile_name = "Requester"
        if not doc.has_role("Requester"):
            doc.add_roles("Requester")
        doc.save()
    except Exception as e:
        # TODO: Hii itasumbua, fix this
        frappe.log_error(
            f"Error setting up role profile for user {doc.email}: {str(e)}",
            "Role Profile Setup Error"
        )
