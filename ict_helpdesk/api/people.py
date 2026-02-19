"""
ict_helpdesk/api/people.py
----------------------------
People Directory API — ICT Staff.

DocType: "ICT Staff"
Fields: personal_number, first_name, middle_name, last_name,
        full_name, mobile_no, email, designation
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_ict_people() -> list:
    """
    Return all ICT Staff records.

    Returns:
        list[dict]: Staff records.
    """
    try:
        _require_privileged()

        people = frappe.get_all(
            "ICT Staff",
            fields=[
                "name",
                "personal_number",
                "full_name",
                "first_name",
                "middle_name",
                "last_name",
                "email",
                "mobile_no",
                "designation",
            ],
            order_by="full_name asc",
            limit_page_length=1000,
        )

        return people

    except frappe.PermissionError:
        raise
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_ict_people Error")
        frappe.throw(_("Could not retrieve people directory."))


@frappe.whitelist()
def get_people_summary() -> dict:
    """
    Return counts of staff grouped by designation. Used for KPI cards.

    Returns:
        dict: {total, by_designation: {designation: count}}
    """
    _require_privileged()

    all_people = frappe.get_all(
        "ICT Staff",
        fields=["designation"],
        limit_page_length=2000,
    )

    by_designation = {}
    for p in all_people:
        d = p.get("designation", "Unknown")
        by_designation[d] = by_designation.get(d, 0) + 1

    return {
        "total":          len(all_people),
        "by_designation": by_designation,
    }


@frappe.whitelist()
def add_ict_person(
    full_name:       str,
    email:           str,
    personal_number: str,
    designation:     str = "",
    first_name:      str = "",
    middle_name:     str = "",
    last_name:       str = "",
    mobile_no:       str = "",
) -> dict:
    """
    Add a new ICT Staff member.

    Args:
        full_name       (str): Full name (used as document name).
        email           (str): Email address.
        personal_number (str): Staff personal/ID number (required).
        designation     (str): Job title / designation.
        first_name      (str): First name.
        middle_name     (str): Middle name.
        last_name       (str): Last name.
        mobile_no       (str): Mobile phone number.

    Returns:
        dict: Newly created ICT Staff document.
    """
    _require_roles(["ICT Director", "ICT Manager", "System Manager",
                    "Administrator", "ICT Officer"])

    if not full_name or not email or not personal_number:
        frappe.throw(_("full_name, email, and personal_number are required."))

    email = email.strip().lower()

    if not frappe.utils.validate_email_address(email):
        frappe.throw(_("Please provide a valid email address."))

    if frappe.db.exists("ICT Staff", {"email": email}):
        frappe.throw(_("A staff member with email {0} already exists.").format(email))

    if frappe.db.exists("ICT Staff", {"personal_number": personal_number}):
        frappe.throw(_("A staff member with personal number {0} already exists.").format(personal_number))

    doc = frappe.get_doc({
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
    doc.insert(ignore_permissions=False)
    frappe.db.commit()

    return doc.as_dict()


@frappe.whitelist()
def get_person_detail(person_id: str) -> dict:
    """
    Return full detail of a single ICT Staff member.

    Args:
        person_id (str): ICT Staff document name (full_name).

    Returns:
        dict: Staff document.
    """
    _require_privileged()

    if not person_id:
        frappe.throw(_("person_id is required."))

    doc = frappe.get_doc("ICT Staff", person_id)

    if not doc:
        frappe.throw(_("Staff member {0} not found.").format(person_id))

    return doc.as_dict()


@frappe.whitelist()
def delete_ict_person(person_id: str) -> dict:
    """
    Delete an ICT Staff record.

    Args:
        person_id (str): ICT Staff document name.

    Returns:
        dict: Confirmation with deleted document name.
    """
    _require_roles(["ICT Director", "ICT Manager", "System Manager", "Administrator"])

    if not person_id:
        frappe.throw(_("person_id is required."))

    doc = frappe.get_doc("ICT Staff", person_id)
    data = doc.as_dict()
    frappe.delete_doc("ICT Staff", person_id, ignore_permissions=False)
    frappe.db.commit()

    return {"deleted": person_id, "full_name": data.get("full_name")}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _require_privileged() -> None:
    _require_roles(["ICT Officer", "ICT Manager", "ICT Director",
                    "System Manager", "Administrator"])


def _require_roles(allowed_roles: list) -> None:
    """Raise PermissionError if the current user has none of the allowed roles."""
    user_roles = frappe.get_roles(frappe.session.user)
    if not any(r in user_roles for r in allowed_roles):
        frappe.throw(
            _("You do not have permission to perform this action."),
            frappe.PermissionError,
        )