"""
ict_helpdesk/api/assigned_officer.py
--------------------------------------
ICT Officer management API.
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_ict_officers() -> list:
    """
    Return all ICT Staff with their open ticket counts.

    Returns:
        list[dict]: Staff records enriched with ticket_count.
    """
    try:
        _require_roles(["ICT Officer", "ICT Manager", "ICT Director",
                        "System Manager", "Administrator"])

        officers = frappe.get_all(
            "ICT Staff",
            fields=[
                "name",
                "full_name",
                "email",
                "mobile_no",
                "designation",
                "personal_number",
            ],
            order_by="full_name asc",
        )

        # Enrich each officer with their assigned open ticket count
        for officer in officers:
            officer["ticket_count"] = frappe.db.count(
                "ICT Ticket",
                filters={
                    "assigned_officer": officer["name"],
                    "status": ["not in", ["Completed", "Resolved"]],
                },
            )

        return officers

    except frappe.PermissionError:
        raise
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_ict_officers Error")
        frappe.throw(_("Could not retrieve officers."))


@frappe.whitelist()
def get_officer_details(officer_name: str) -> dict:
    """
    Return details for a single ICT Staff member by full_name.

    Args:
        officer_name (str): Full name of the ICT Staff member.

    Returns:
        dict: Officer fields.
    """
    _require_roles(["ICT Officer", "ICT Manager", "ICT Director",
                    "System Manager", "Administrator"])

    if not officer_name:
        frappe.throw(_("officer_name is required."))

    officer = frappe.get_value(
        "ICT Staff",
        {"full_name": officer_name},
        ["name", "full_name", "email", "mobile_no", "designation", "personal_number"],
        as_dict=True,
    )

    if not officer:
        frappe.throw(_("Officer {0} not found.").format(officer_name))

    return officer


@frappe.whitelist()
def add_ict_officer(
    full_name:       str,
    email:           str,
    designation:     str,
    mobile_no:       str = "",
    personal_number: str = "",
    first_name:      str = "",
    middle_name:     str = "",
    last_name:       str = "",
) -> dict:
    """
    Create a new ICT Staff record and a corresponding Frappe User account.

    Args:
        full_name       (str): Officer's full name.
        email           (str): Email address (becomes the Frappe username).
        designation     (str): Job title / designation.
        mobile_no       (str): Optional mobile phone number.
        personal_number (str): Optional personal/staff number.
        first_name      (str): First name.
        middle_name     (str): Middle name.
        last_name       (str): Last name.

    Returns:
        dict: Newly created ICT Staff document.
    """
    _require_roles(["ICT Director", "ICT Manager", "System Manager", "Administrator"])

    if not full_name or not email or not designation:
        frappe.throw(_("full_name, email, and designation are required."))

    email = email.strip().lower()

    if not frappe.utils.validate_email_address(email):
        frappe.throw(_("Please provide a valid email address."))

    if frappe.db.exists("ICT Staff", {"email": email}):
        frappe.throw(_("A staff member with email {0} already exists.").format(email))

    # ── Create ICT Staff document ──
    officer_doc = frappe.get_doc({
        "doctype":         "ICT Staff",
        "full_name":       full_name.strip(),
        "first_name":      first_name.strip(),
        "middle_name":     middle_name.strip(),
        "last_name":       last_name.strip(),
        "email":           email,
        "mobile_no":       mobile_no.strip(),
        "designation":     designation.strip(),
        "personal_number": personal_number.strip(),
    })
    officer_doc.insert(ignore_permissions=False)

    # ── Create / update Frappe User account ──
    _create_or_update_frappe_user(
        email=email,
        full_name=full_name.strip(),
        mobile_no=mobile_no.strip(),
        role="ICT Officer",
    )

    frappe.db.commit()

    frappe.publish_realtime(
        event="officer_added",
        message={"officer": officer_doc.name, "full_name": full_name},
    )

    return officer_doc.as_dict()


@frappe.whitelist()
def deactivate_officer(officer_id: str) -> dict:
    """
    Since ICT Staff has no is_active field, this deletes the record entirely.

    Args:
        officer_id (str): ICT Staff document name.

    Returns:
        dict: Deleted document data.
    """
    _require_roles(["ICT Director", "ICT Manager", "System Manager", "Administrator"])

    if not officer_id:
        frappe.throw(_("officer_id is required."))

    doc = frappe.get_doc("ICT Staff", officer_id)
    data = doc.as_dict()
    frappe.delete_doc("ICT Staff", officer_id, ignore_permissions=False)
    frappe.db.commit()

    return data


# ── Internal helpers ──────────────────────────────────────────────────────────

def _require_roles(allowed_roles: list) -> None:
    """Raise PermissionError if the current user has none of the allowed roles."""
    user_roles = frappe.get_roles(frappe.session.user)
    if not any(r in user_roles for r in allowed_roles):
        frappe.throw(
            _("You do not have permission to perform this action."),
            frappe.PermissionError,
        )


def _create_or_update_frappe_user(
    email: str,
    full_name: str,
    mobile_no: str,
    role: str,
) -> None:
    """
    Ensure a Frappe User exists for this staff member and has the correct role.
    If the user already exists, just adds the role.
    """
    if frappe.db.exists("User", email):
        user_doc = frappe.get_doc("User", email)
    else:
        names = full_name.split(" ", 1)
        user_doc = frappe.get_doc({
            "doctype":            "User",
            "email":              email,
            "first_name":         names[0],
            "last_name":          names[1] if len(names) > 1 else "",
            "mobile_no":          mobile_no,
            "user_type":          "System User",
            "send_welcome_email": 1,
        })
        user_doc.insert(ignore_permissions=True)

    # Add role if not already present
    existing_roles = [r.role for r in user_doc.roles]
    if role not in existing_roles:
        user_doc.append("roles", {"role": role})
        user_doc.save(ignore_permissions=True)