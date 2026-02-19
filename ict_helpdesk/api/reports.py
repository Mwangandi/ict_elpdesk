"""
ict_helpdesk/api/reports.py
"""
import frappe
import json
from frappe import _
from frappe.utils import now_datetime, get_datetime, add_days, today, nowdate


@frappe.whitelist()
def get_dashboard_data() -> dict:
    _require_privileged()

    now       = now_datetime()
    today_str = today()

    # ── Month boundaries ──
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ── Executive KPIs ──
    open_tickets = frappe.db.count("ICT Ticket", filters={
        "status": ["not in", ["Resolved", "Completed"]]
    })

    resolved_this_month = frappe.db.count("ICT Ticket", filters={
        "status": ["in", ["Resolved", "Completed"]],
        "modified": [">=", month_start],
    })

    critical_open = frappe.db.count("ICT Ticket", filters={
        "issue_priority": "Critical",
        "status": ["not in", ["Resolved", "Completed"]],
    })

    # ── Avg resolution time (hours) ──
    resolved = frappe.db.sql("""
        SELECT creation, modified FROM `tabICT Ticket`
        WHERE status IN ('Resolved','Completed')
        AND modified >= %s
    """, (month_start,), as_dict=True)

    avg_resolution_hrs = None
    if resolved:
        total_hrs = sum(
            (get_datetime(r.modified) - get_datetime(r.creation)).total_seconds() / 3600
            for r in resolved
        )
        avg_resolution_hrs = round(total_hrs / len(resolved), 1)

    # ── Alerts: Unassigned > 24hrs ──
    cutoff_24h = add_days(now, -1)
    unassigned_raw = frappe.get_all("ICT Ticket",
        filters={
            "assigned_officer": ["in", ["", None]],
            "status": ["not in", ["Resolved", "Completed"]],
            "creation": ["<=", cutoff_24h],
        },
        fields=["name", "issue_summary", "creation"],
        limit=10,
    )
    unassigned_over_24h = [{
        **t,
        "hours_open": int((now - get_datetime(t.creation)).total_seconds() / 3600)
    } for t in unassigned_raw]

    # ── Alerts: High/Critical with no update in 24hrs ──
    critical_raw = frappe.get_all("ICT Ticket",
        filters={
            "issue_priority": ["in", ["High", "Critical"]],
            "status": ["not in", ["Resolved", "Completed"]],
            "modified": ["<=", cutoff_24h],
        },
        fields=["name", "issue_priority", "department", "creation"],
        limit=10,
    )
    critical_no_response = [{
        **t,
        "hours_open": int((now - get_datetime(t.creation)).total_seconds() / 3600)
    } for t in critical_raw]

    # ── Alerts: Overloaded officers (more than 10 open tickets) ──
    officer_loads = frappe.db.sql("""
        SELECT assigned_officer AS officer, COUNT(*) AS open_count
        FROM `tabICT Ticket`
        WHERE status NOT IN ('Resolved','Completed')
        AND assigned_officer IS NOT NULL AND assigned_officer != ''
        GROUP BY assigned_officer
        HAVING open_count > 10
        ORDER BY open_count DESC
    """, as_dict=True)

    # ── Aging tickets (unresolved > 7 days) ──
    aging_raw = frappe.get_all("ICT Ticket",
        filters={
            "status": ["not in", ["Resolved", "Completed"]],
            "creation": ["<=", add_days(now, -7)],
        },
        fields=["name", "status", "creation"],
        order_by="creation asc",
        limit=10,
    )
    aging_tickets = [{
        **t,
        "days_open": int((now - get_datetime(t.creation)).total_seconds() / 86400)
    } for t in aging_raw]

    # ── Tickets per day (last 7) ──
    since_7 = add_days(today_str, -7)
    daily_raw = frappe.db.sql("""
        SELECT DATE(creation) AS date, COUNT(*) AS count
        FROM `tabICT Ticket`
        WHERE creation >= %s
        GROUP BY DATE(creation)
        ORDER BY date ASC
    """, (since_7,), as_dict=True)
    ticket_count_per_day = {
        "dates":  [str(r.date) for r in daily_raw],
        "counts": [r.count for r in daily_raw],
    }

    # ── Tickets per department ──
    dept_raw = frappe.db.sql("""
        SELECT department, COUNT(*) AS count
        FROM `tabICT Ticket`
        WHERE department IS NOT NULL AND department != ''
        GROUP BY department ORDER BY count DESC
    """, as_dict=True)

    # ── Tickets by issue type (from check fields) ──
    issue_rows = frappe.db.sql("""
        SELECT
            department,
            SUM(IF(software_issue_check = 1, 1, 0))  AS software,
            SUM(IF(hardware_issue_check = 1, 1, 0))  AS hardware,
            SUM(IF(internet_issue_check = 1, 1, 0))  AS internet,
            SUM(IF(clearance_issue_check = 1, 1, 0)) AS clearance
        FROM `tabICT Ticket`
        WHERE department IS NOT NULL AND department != ''
        GROUP BY department
    """, as_dict=True)

    # Flat issue type totals for the doughnut chart
    tickets_by_issue_type = [
        {"issue_type": "Software",  "count": sum(r.software  or 0 for r in issue_rows)},
        {"issue_type": "Hardware",  "count": sum(r.hardware  or 0 for r in issue_rows)},
        {"issue_type": "Internet",  "count": sum(r.internet  or 0 for r in issue_rows)},
        {"issue_type": "Clearance", "count": sum(r.clearance or 0 for r in issue_rows)},
    ]

    # Stacked issue type per department
    issue_type_per_department = {
        "departments": [r["department"] for r in issue_rows],
        "issue_types": ["Software", "Hardware", "Internet", "Clearance"],
        "data": {
            r["department"]: {
                "Software":  r["software"]  or 0,
                "Hardware":  r["hardware"]  or 0,
                "Internet":  r["internet"]  or 0,
                "Clearance": r["clearance"] or 0,
            }
            for r in issue_rows
        }
    }

    # ── Officer: open ticket count (joined to ICT Staff for full name) ──
    officer_open_raw = frappe.db.sql("""
        SELECT
            COALESCE(s.full_name, t.assigned_officer) AS officer,
            COUNT(*) AS count
        FROM `tabICT Ticket` t
        LEFT JOIN `tabICT Staff` s ON t.assigned_officer = s.name
        WHERE t.status NOT IN ('Resolved','Completed')
        AND t.assigned_officer IS NOT NULL AND t.assigned_officer != ''
        GROUP BY t.assigned_officer ORDER BY count DESC
    """, as_dict=True)

    # ── Officer performance: assigned vs resolved ──
    officer_perf_raw = frappe.db.sql("""
        SELECT
            COALESCE(s.full_name, t.assigned_officer) AS officer,
            COUNT(*) AS assigned,
            SUM(CASE WHEN t.status IN ('Resolved','Completed') THEN 1 ELSE 0 END) AS resolved
        FROM `tabICT Ticket` t
        LEFT JOIN `tabICT Staff` s ON t.assigned_officer = s.name
        WHERE t.assigned_officer IS NOT NULL AND t.assigned_officer != ''
        GROUP BY t.assigned_officer ORDER BY assigned DESC
    """, as_dict=True)

    # ── Officer avg resolution time ──
    officer_res_raw = frappe.db.sql("""
        SELECT
            COALESCE(s.full_name, t.assigned_officer) AS officer,
            ROUND(AVG(TIMESTAMPDIFF(HOUR, t.creation, t.modified)), 1) AS avg_hours
        FROM `tabICT Ticket` t
        LEFT JOIN `tabICT Staff` s ON t.assigned_officer = s.name
        WHERE t.status IN ('Resolved','Completed')
        AND t.assigned_officer IS NOT NULL AND t.assigned_officer != ''
        GROUP BY t.assigned_officer ORDER BY avg_hours ASC
    """, as_dict=True)

    return {
        # Executive KPIs
        "open_tickets":          open_tickets,
        "resolved_this_month":   resolved_this_month,
        "avg_resolution_hrs":    avg_resolution_hrs,
        "critical_open":         critical_open,
        # Alerts
        "unassigned_over_24h":   unassigned_over_24h,
        "critical_no_response":  critical_no_response,
        "overloaded_officers":   officer_loads,
        "aging_tickets":         aging_tickets,
        # Ticket analytics
        "ticket_count_per_day":      ticket_count_per_day,
        "tickets_per_department":    dept_raw,
        "tickets_by_issue_type":     tickets_by_issue_type,
        "issue_type_per_department": issue_type_per_department,
        # Officer performance
        "tickets_per_officer":     officer_open_raw,
        "officer_performance":     officer_perf_raw,
        "officer_resolution_time": officer_res_raw,
    }


@frappe.whitelist()
def get_list(
    doctype='ICT Ticket',
    fields=None,
    filters=None,
    order_by=None,
    limit_page_length=5000,
):
    """Lightweight server-side wrapper for frappe.get_list, restricted to ICT Ticket."""
    if doctype != "ICT Ticket":
        frappe.throw(_("This endpoint only allows fetching ICT Ticket"))

    if isinstance(fields, str) and fields:
        try:
            fields = json.loads(fields)
        except Exception:
            fields = [f.strip() for f in fields.split(",") if f.strip()]
    if not fields:
        fields = ["name"]

    if isinstance(filters, str) and filters:
        try:
            filters = json.loads(filters)
        except Exception:
            pass

    try:
        limit_page_length = int(limit_page_length)
    except Exception:
        limit_page_length = 5000

    return frappe.get_list(
        "ICT Ticket",
        fields=fields,
        filters=filters,
        order_by=order_by,
        limit_page_length=limit_page_length,
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _require_privileged():
    _require_roles(["ICT Officer", "ICT Manager", "ICT Director",
                    "System Manager", "Administrator"])


def _require_roles(allowed_roles):
    user_roles = frappe.get_roles(frappe.session.user)
    if not any(r in user_roles for r in allowed_roles):
        frappe.throw(_("You do not have permission."), frappe.PermissionError)
        
        
        
@frappe.whitelist()
def update_asset(
    asset_id:           str,
    device_name:        str = "",
    serial_number:      str = "",
    device_model:       str = "",
    device_ram:         str = "",
    device_storage:     str = "",
    device_department:  str = "",
    device_directorate: str = "",
    device_office:      str = "",
    officer_in_charge:  str = "",
    status:             str = "",
) -> dict:
    """
    Update fields on an existing Asset Data record.

    Args:
        asset_id (str): Asset Data document name (tag_number).

    Returns:
        dict: Updated document.
    """
    # TODO: Change the roles to match
    _require_roles(["ICT Director", "ICT Manager", "System Manager",
                    "Administrator", "ICT Officer"])

    if not asset_id:
        frappe.throw(_("asset_id is required."))

    if status and status not in ASSET_STATUSES:
        frappe.throw(_("Invalid status '{0}'.").format(status))

    doc = frappe.get_doc("Asset Data", asset_id)

    if device_name:        doc.device_name        = device_name.strip()
    if serial_number:      doc.serial_number      = serial_number.strip()
    if device_model:       doc.device_model       = device_model.strip()
    if device_ram:         doc.device_ram         = device_ram.strip()
    if device_storage:     doc.device_storage     = device_storage.strip()
    if device_department:  doc.device_department  = device_department.strip()
    if device_directorate: doc.device_directorate = device_directorate.strip()
    if device_office:      doc.device_office      = device_office.strip()
    if officer_in_charge:  doc.officer_in_charge  = officer_in_charge.strip()
    if status:             doc.status             = status

    doc.save(ignore_permissions=False)
    frappe.db.commit()

    return doc.as_dict()