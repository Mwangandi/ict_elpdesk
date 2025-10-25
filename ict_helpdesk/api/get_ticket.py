import frappe

@frappe.whitelist(allow_guest=False)
def check_ticket_exists(ticket_no):
    """Check if ICT Ticket exists by name or ID"""
    return frappe.db.exists("ICT Ticket", ticket_no)


import frappe

@frappe.whitelist()
def get_user_tickets(priority=None, status=None):
    user = frappe.session.user

    # Fetch staff info
    staff = frappe.db.get_value(
        "ICT Staff",
        {"email": user},
        ["email", "designation"],
        as_dict=True
    )
    role_profile = frappe.db.get_value("User", user, "role_profile_name")


    filters = {}

    if not staff:
        # Not ICT staff → show own tickets only
        filters["owner"] = user

    else:
        designation = staff.designation or ""

        if any(title in designation for title in ["ICT Officer", "Senior ICT Officer", "Chief ICT Officer"]):
            # Officer can only see assigned tickets
            filters["assigned_officer_email"] = staff.email
        elif "ICT Director" in designation or role_profile == "Admin 2":
            # Director or admin → see all
            filters = {}
        else:
            # Default case (normal employee)
            filters["owner"] = user

    # Apply frontend filters (from JS)
    if priority:
        filters["issue_priority"] = priority
    if status:
        filters["status"] = status

    tickets = frappe.get_all(
        "ICT Ticket",
        filters=filters,
        fields=[
            "name",
            "personal_number",
            "full_name",
            "mobile_no",
            "email",
            "department",
            "issue_summary",
            "recurring_issue_check",
            "software_issue_type",
            "software_issue_description",
            "county_device_check",
            "issue_priority",
            "assigned_officer",
            "assigned_officer_email",
            "assigned_officer_mobile",
            "status",
        ],
        order_by="creation desc"
    )

    return tickets
