"""
ict_helpdesk/api/assets.py
----------------------------
ICT Asset Management API for the Director Portal.
"""

import frappe
from frappe import _


ASSET_STATUSES = ["Active", "In Maintenance", "Decommissioned", "In Storage"]

# Fields the ICT Officer may edit through the portal.
# tag_number and serial_number are intentionally excluded —
# they are hardware identifiers and require a formal process to change.
_EDITABLE_FIELDS = (
    "device_name",
    "device_model",
    "device_ram",
    "device_storage",
    "device_department",
    "device_directorate",
    "device_office",
    "officer_in_charge",
    "status",
    "notes",
)


@frappe.whitelist()
def get_ict_assets(status: str = "") -> list:
    """
    Return Asset Data records, optionally filtered by status.

    Args:
        status (str): Asset status (e.g. "Active"). Empty returns everything.

    Returns:
        list[dict]: Asset records.
    """
    try:
        _require_privileged()

        filters = {}
        if status:
            filters["status"] = status

        assets = frappe.get_all(
            "Asset Data",
            filters=filters,
            fields=[
                "name",
                "tag_number",
                "serial_number",
                "device_name",
                "device_model",
                "device_ram",
                "device_storage",
                "device_department",
                "device_directorate",
                "device_office",
                "officer_in_charge",
                "status",
            ],
            order_by="device_name asc",
            limit_page_length=1000,
        )

        return assets

    except frappe.PermissionError:
        raise
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_ict_assets Error")
        frappe.throw(_("Could not retrieve assets."))


@frappe.whitelist()
def get_asset_detail(asset_id: str) -> dict:
    """
    Return full detail of a single Asset Data record.

    Args:
        asset_id (str): Asset Data document name (tag_number).

    Returns:
        dict: Full asset document.
    """
    _require_privileged()

    if not asset_id:
        frappe.throw(_("asset_id is required."))

    doc = frappe.get_doc("Asset Data", asset_id)
    return doc.as_dict()


@frappe.whitelist()
def add_ict_asset(
    tag_number:          str,
    device_name:         str,
    serial_number:       str = "",
    device_model:        str = "",
    device_ram:          str = "",
    device_storage:      str = "",
    device_department:   str = "",
    device_directorate:  str = "",
    device_office:       str = "",
    officer_in_charge:   str = "",
    status:              str = "Active",
) -> dict:
    """
    Create a new Asset Data record.

    Args:
        tag_number         (str): Unique asset tag number (document name).
        device_name        (str): Human-readable device name.
        serial_number      (str): Manufacturer serial number.
        device_model       (str): Device model.
        device_ram         (str): RAM specification.
        device_storage     (str): Storage specification.
        device_department  (str): Owning department.
        device_directorate (str): Owning directorate.
        device_office      (str): Physical office location.
        officer_in_charge  (str): Officer responsible for the asset.
        status             (str): Initial status (default "Active").

    Returns:
        dict: Newly created Asset Data document.
    """
    _require_roles(["ICT Director", "ICT Manager", "System Manager",
                    "Administrator", "ICT Officer"])

    if not tag_number or not device_name:
        frappe.throw(_("tag_number and device_name are required."))

    if status not in ASSET_STATUSES:
        frappe.throw(_("Invalid status '{0}'.").format(status))

    if frappe.db.exists("Asset Data", tag_number):
        frappe.throw(_("An asset with tag number {0} already exists.").format(tag_number))

    doc = frappe.get_doc({
        "doctype":            "Asset Data",
        "tag_number":         tag_number.strip(),
        "device_name":        device_name.strip(),
        "serial_number":      serial_number.strip(),
        "device_model":       device_model.strip(),
        "device_ram":         device_ram.strip(),
        "device_storage":     device_storage.strip(),
        "device_department":  device_department.strip(),
        "device_directorate": device_directorate.strip(),
        "device_office":      device_office.strip(),
        "officer_in_charge":  officer_in_charge.strip(),
        "status":             status,
    })
    doc.insert(ignore_permissions=False)
    frappe.db.commit()

    return doc.as_dict()


@frappe.whitelist()
def update_asset(
    asset_id:           str,
    device_name:        str,
    device_model:       str = "",
    device_ram:         str = "",
    device_storage:     str = "",
    device_department:  str = "",
    device_directorate: str = "",
    device_office:      str = "",
    officer_in_charge:  str = "",
    status:             str = "Active",
    notes:              str = "",
) -> dict:
    """
    Update the editable fields of an Asset Data record.

    tag_number and serial_number cannot be changed here — they are
    hardware identifiers and must be updated via a formal process.

    Args:
        asset_id           (str): Asset Data document name (required).
        device_name        (str): Human-readable device name (required).
        device_model       (str): Device model.
        device_ram         (str): RAM specification.
        device_storage     (str): Storage specification.
        device_department  (str): Owning department.
        device_directorate (str): Owning directorate.
        device_office      (str): Physical office location.
        officer_in_charge  (str): Officer responsible for the asset.
        status             (str): Asset status.
        notes              (str): Additional notes or remarks.

    Returns:
        dict: { success: True, ...updated fields } on success.
    """
    try:
        _require_roles(["ICT Officer", "ICT Manager", "ICT Director",
                        "System Manager", "Administrator"])

        if not asset_id:
            frappe.throw(_("asset_id is required."))
        if not device_name or not device_name.strip():
            frappe.throw(_("device_name is required."))
        if status not in ASSET_STATUSES:
            frappe.throw(_("Invalid status '{0}'.").format(status))

        doc = frappe.get_doc("Asset Data", asset_id)

        # Apply only whitelisted fields — tag_number and serial_number are untouched
        doc.device_name        = device_name.strip()
        doc.device_model       = device_model.strip()
        doc.device_ram         = device_ram.strip()
        doc.device_storage     = device_storage.strip()
        doc.device_department  = device_department.strip()
        doc.device_directorate = device_directorate.strip()
        doc.device_office      = device_office.strip()
        doc.officer_in_charge  = officer_in_charge.strip()
        doc.status             = status

        # Only write notes if the field exists on this installation's doctype
        if hasattr(doc, "notes"):
            doc.notes = notes.strip()

        doc.save(ignore_permissions=False)
        frappe.db.commit()

        return {
            "success":           True,
            "name":              doc.name,
            "device_name":       doc.device_name,
            "device_model":      doc.device_model,
            "device_ram":        doc.device_ram,
            "device_storage":    doc.device_storage,
            "device_department": doc.device_department,
            "device_directorate":doc.device_directorate,
            "device_office":     doc.device_office,
            "officer_in_charge": doc.officer_in_charge,
            "status":            doc.status,
            "notes":             getattr(doc, "notes", ""),
            "modified":          str(doc.modified),
        }

    except frappe.PermissionError:
        raise
    except frappe.ValidationError:
        raise
    except Exception:
        frappe.log_error(frappe.get_traceback(), "update_asset Error")
        frappe.throw(_("Could not update asset."))


@frappe.whitelist()
def update_asset_status(asset_id: str, status: str, notes: str = "") -> dict:
    """
    Update the status of an Asset Data record.

    Args:
        asset_id (str): Asset Data document name.
        status   (str): New status value.
        notes    (str): Optional notes about the status change.

    Returns:
        dict: Updated asset document.
    """
    _require_roles(["ICT Director", "ICT Manager", "System Manager",
                    "Administrator", "ICT Officer"])

    if not asset_id or not status:
        frappe.throw(_("asset_id and status are required."))

    if status not in ASSET_STATUSES:
        frappe.throw(_("Invalid status '{0}'.").format(status))

    doc = frappe.get_doc("Asset Data", asset_id)
    doc.status = status
    if notes:
        doc.add_comment("Info", notes)
    doc.save(ignore_permissions=False)
    frappe.db.commit()

    return doc.as_dict()


@frappe.whitelist()
def get_asset_summary() -> dict:
    """
    Return aggregated asset counts broken down by status and department.
    Used for dashboard KPI cards.

    Returns:
        dict: {
            total,
            by_status: {status: count},
            by_department: {department: count}
        }
    """
    _require_privileged()

    all_assets = frappe.get_all(
        "Asset Data",
        fields=["status", "device_department"],
        limit_page_length=5000,
    )

    by_status     = {}
    by_department = {}

    for a in all_assets:
        s = a.get("status", "Unknown")
        d = a.get("device_department", "Unknown")
        by_status[s]     = by_status.get(s, 0)     + 1
        by_department[d] = by_department.get(d, 0) + 1

    return {
        "total":         len(all_assets),
        "by_status":     by_status,
        "by_department": by_department,
    }


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
