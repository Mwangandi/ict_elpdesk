from frappe.utils import nowdate, add_days, getdate
import frappe, json
from frappe import _

@frappe.whitelist()
def get_dashboard_data():
    data = {}

    # === 1. Ticket Count per Day (last 7 days) ===
    days = [add_days(nowdate(), -i) for i in range(6, -1, -1)]
    counts = []
    for d in days:
        count = frappe.db.count("ICT Ticket", {
            "creation": [">=", f"{d} 00:00:00", "<=", f"{d} 23:59:59"]
        })
        counts.append(count)
    data["ticket_count_per_day"] = {"dates": days, "counts": counts}

    # === 2. Ticket Count per Department ===
    dept_counts = frappe.db.sql("""
        SELECT department, COUNT(*) as count
        FROM `tabICT Ticket`
        WHERE department IS NOT NULL AND department != ''
        GROUP BY department
        ORDER BY count DESC
    """, as_dict=True)
    data["tickets_per_department"] = dept_counts

    # === 3. Issue Type per Department ===
    # We'll derive "Issue Type" dynamically from the *_check fields
    issue_rows = frappe.db.sql("""
        SELECT
            department,
            SUM(IF(software_issue_check = 1, 1, 0)) AS software,
            SUM(IF(hardware_issue_check = 1, 1, 0)) AS hardware,
            SUM(IF(internet_issue_check = 1, 1, 0)) AS internet,
            SUM(IF(clearance_issue_check = 1, 1, 0)) AS clearance
        FROM `tabICT Ticket`
        WHERE department IS NOT NULL AND department != ''
        GROUP BY department
    """, as_dict=True)

    data["issue_type_per_department"] = {
        "departments": [r["department"] for r in issue_rows],
        "issue_types": ["Software", "Hardware", "Internet", "Clearance"],
        "data": {
            r["department"]: {
                "Software": r["software"],
                "Hardware": r["hardware"],
                "Internet": r["internet"],
                "Clearance": r["clearance"]
            }
            for r in issue_rows
        }
    }

    # === 4. Tickets per Officer ===
    officer_counts = frappe.db.sql("""
        SELECT 
            s.full_name AS officer,
            s.designation,
            COUNT(t.name) AS count
        FROM `tabICT Ticket` t
        LEFT JOIN `tabICT Staff` s
            ON t.assigned_officer_email = s.email
        WHERE s.designation IS NOT NULL
        GROUP BY s.full_name, s.designation
        ORDER BY count DESC
    """, as_dict=True)
    data["tickets_per_officer"] = officer_counts

    return data


@frappe.whitelist()
def get_list(doctype='ICT Ticket', fields=None, filters=None, order_by=None, limit_page_length=5000):
    """
    Lightweight server-side wrapper for client.get_list limited to ICT Ticket.
    Accepts:
      - doctype: must be "ICT Ticket"
      - fields: list or JSON string (e.g. '["creation","status"]' or "creation,status")
      - filters: list/dict or JSON string (e.g. '[["creation",">=","2025-01-01"]]')
      - order_by: string
      - limit_page_length: int

    Returns list of dicts.
    """
    # Safety: restrict to ICT Ticket for this endpoint
    if doctype != "ICT Ticket":
        frappe.throw(_("This endpoint only allows fetching ICT Ticket"))

    # normalize fields
    if isinstance(fields, str) and fields:
        try:
            fields = json.loads(fields)
        except Exception:
            # allow comma-separated string like "creation,status"
            fields = [f.strip() for f in fields.split(",") if f.strip()]
    if not fields:
        fields = ["name"]

    # normalize filters
    if isinstance(filters, str) and filters:
        try:
            filters = json.loads(filters)
        except Exception:
            # leave as-is (frappe.get_list accepts list/dict)
            pass

    # Ensure sensible limit
    try:
        limit_page_length = int(limit_page_length)
    except Exception:
        limit_page_length = 5000

    # Call frappe.get_list (safe, server-side)
    results = frappe.get_list(
        "ICT Ticket",
        fields=fields,
        filters=filters,
        order_by=order_by,
        limit_page_length=limit_page_length
    )

    return results
