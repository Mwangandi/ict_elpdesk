"""
ict_helpdesk/api/get_ticket.py
--------------------------------
Ticket retrieval API — aligned to the actual ICT Ticket & ICT Staff schema.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def check_ticket_exists(ticket_no):
    """Check if an ICT Ticket exists by name / ID."""
    return frappe.db.exists("ICT Ticket", ticket_no)


@frappe.whitelist()
def get_user_tickets(priority=None, status=None):
    """
    Return ICT Tickets visible to the current user based on their designation.

    Access rules:
      - ICT Officer / Senior ICT Officer / Chief ICT Officer
            → only tickets assigned to them (by email)
      - ICT Director or role_profile_name == "Admin 2"
            → all tickets
      - Non-ICT staff (no ICT Staff record)
            → only tickets they raised (owner)
      - Anyone else with an ICT Staff record but no matching designation
            → only tickets they raised (owner)

    Args:
        priority (str | None): Filter by issue_priority (Low/Medium/High/Critical).
        status   (str | None): Filter by status field.

    Returns:
        list[dict]: Matching ICT Ticket records.
    """
    user = frappe.session.user

    # ── Determine role from ICT Staff record ──────────────────────────────
    staff = frappe.db.get_value(
        "ICT Staff",
        {"email": user},
        ["email", "designation"],
        as_dict=True,
    )

    role_profile = frappe.db.get_value("User", user, "role_profile_name")

    filters = {}

    if not staff:
        # Not in ICT Staff — regular employee, show own tickets only
        filters["owner"] = user
    else:
        designation = staff.designation or ""

        OFFICER_TITLES = [
            "ICT Officer",
            "Senior ICT Officer",
            "Chief ICT Officer",
        ]

        if any(title in designation for title in OFFICER_TITLES):
            # Officers see only tickets assigned to them
            filters["assigned_officer_email"] = staff.email

        elif "ICT Director" in designation or role_profile == "Admin 2":
            # Director / admin sees everything — no extra filters
            filters = {}

        else:
            # ICT Staff member with an unrecognised designation
            filters["owner"] = user

    # ── Apply optional frontend filters ──────────────────────────────────
    if priority:
        filters["issue_priority"] = priority

    if status:
        filters["status"] = status

    # ── Query ─────────────────────────────────────────────────────────────
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
        order_by="creation desc",
    )

    return tickets


@frappe.whitelist()
def get_ticket_detail(ticket_id):
    """
    Return the full document for a single ICT Ticket.
    Enforces the same access rules as get_user_tickets.

    Args:
        ticket_id (str): The ticket name / ID.

    Returns:
        dict: Full ticket document.
    """
    if not ticket_id:
        frappe.throw(_("ticket_id is required."))

    _assert_ticket_access(ticket_id)

    doc = frappe.get_doc("ICT Ticket", ticket_id)
    return doc.as_dict()


# ── Internal helpers ──────────────────────────────────────────────────────────

def _assert_ticket_access(ticket_id):
    """
    Raise PermissionError if the current user is not allowed to view the ticket.

    - Director / Admin 2          → always allowed
    - Officer                     → allowed if assigned_officer_email matches
    - Everyone else               → allowed only if they are the owner
    """
    user = frappe.session.user

    staff = frappe.db.get_value(
        "ICT Staff",
        {"email": user},
        ["email", "designation"],
        as_dict=True,
    )

    role_profile = frappe.db.get_value("User", user, "role_profile_name")

    # Directors / Admins — full access
    if staff and (
        "ICT Director" in (staff.designation or "")
        or role_profile == "Admin 2"
    ):
        return

    ticket = frappe.db.get_value(
        "ICT Ticket",
        ticket_id,
        ["owner", "assigned_officer_email"],
        as_dict=True,
    )

    if not ticket:
        frappe.throw(_("Ticket {0} not found.").format(ticket_id))

    OFFICER_TITLES = [
        "ICT Officer",
        "Senior ICT Officer",
        "Chief ICT Officer",
    ]

    # Officers — can view only tickets assigned to them
    if staff and any(title in (staff.designation or "") for title in OFFICER_TITLES):
        if ticket.assigned_officer_email == staff.email:
            return
        frappe.throw(
            _("You do not have permission to view this ticket."),
            frappe.PermissionError,
        )

    # Everyone else — only their own tickets
    if ticket.owner != user:
        frappe.throw(
            _("You do not have permission to view this ticket."),
            frappe.PermissionError,
        )