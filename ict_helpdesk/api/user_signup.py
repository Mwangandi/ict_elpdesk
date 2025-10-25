import frappe

@frappe.whitelist(allow_guest=True)
def create_requester_user(
    personal_number=None,
    first_name=None,
    middle_name=None,
    last_name=None,
    mobile_no=None,
    department=None,
    directorate=None,
    email=None,
    location=None,
    gender=None
):
    """Create a new Frappe user and assign 'Requester' role"""
    DEFAULT_PASSWORD = frappe.conf.get("default_signup_password") or "default123"

    if frappe.db.exists("User", email):
        return {"status": "exists", "message": "User already exists"}

    # Create new user document
    user = frappe.new_doc("User")
    user.personal_number = personal_number
    user.first_name = first_name
    user.middle_name = middle_name
    user.last_name = last_name
    user.mobile_no = mobile_no
    user.department = department
    user.directorate = directorate
    user.location = location
    user.gender = gender
    user.email = email
    user.enabled = 1
    user.new_password = DEFAULT_PASSWORD # send welcome email
    user.send_welcome_email = 0

    # Assign "Requester" role before inserting
    user.append("roles", {"role": "Requester"})

    # Assign role profile
    # user.role_profile_name = "Requester"

    # Assign module profile
    user.module_profile = "Requester"

    # Send welcome email
    user.send_welcome_email = 1

    user.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        # "message": f"User {email} created successfully",
        # "user": user.name
    }
