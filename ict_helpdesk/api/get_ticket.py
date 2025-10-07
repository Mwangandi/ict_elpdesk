import frappe

@frappe.whitelist(allow_guest=False)
def check_ticket_exists(ticket_no):
    """Check if ICT Ticket exists by name or ID"""
    return frappe.db.exists("ICT Ticket", ticket_no)


@frappe.whitelist()
def get_user_tickets(priority=None, status=None):
    """Return tickets depending on user's role (Officer or Requester), with optional filters."""
    user = frappe.session.user

    if not user or user == "Guest":
        return []

    # Get user roles
    roles = frappe.get_roles(user)

    # Define ICT officer roles
    officer_roles = [
        "ICT Officer I",
        "ICT Officer II",
        "ICT Officer III",
        "Senior ICT Officer",
        "Chief ICT Officer"
    ]

    # Check role
    is_officer = any(role in roles for role in officer_roles)

    # Base filters
    if is_officer:
        email = frappe.db.get_value("User", user, "email")
        filters = {"assigned_officer_email": email}
    elif "ICT Director" in roles or "Administrator" in roles:
        filters = {}  # See all
    else:
        filters = {"owner": user}  # Normal user

    # Apply web page filters (from JS)
    if priority:
        filters["issue_priority"] = priority
    if status:
        filters["status"] = status

    # Fetch tickets
    tickets = frappe.get_all(
        "ICT Ticket",
        filters=filters,
        fields=[
            "name",
            "personal_number",
            "full_name",
            "mobile_no",
            "email",
            "issue_summary",
            "recurring_issue_check",
            "software_issue_type",
            "software_issue_description",
            "county_device_check",
            "tag_number",
            "serial_number",
            "device_office",
            "hardware_issue_description",
            "internet_issue_check",
            "internet_issue_type",
            "network_issue_description",
            "clearance_issue_check",
            "clearance_issue_description",
            "issue_priority",
            "assigned_officer",
            "assigned_officer_email",
            "assigned_officer_mobile",
            "status",
            "creation"
        ],
        order_by="creation desc"
    )

    return tickets
