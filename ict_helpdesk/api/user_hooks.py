import frappe
from .sms import send_custom_sms as sms

def set_default_user_settings(doc, method=None):
    """Automatically sets default password, role, and module profile for new users"""
    
    # Generate a random default password
    default_password = "default123"
    frappe.utils.password.update_password(user=doc.email, pwd=default_password)

    
    # Assign the "Requester" role if not already assigned
    if not frappe.db.exists("Has Role", {"parent": doc.name, "role": "Requester"}):
        doc.add_roles("Requester")
    
    # Assign "Requester" module profile
    doc.module_profile = "Requester"
    doc.save(ignore_permissions=True)
    
    # sms the credentials to the user
    sms(doc.mobile_no, f"Your account has been created. \nUsername: {doc.email}, \nPassword: {default_password}")

    frappe.db.commit()
