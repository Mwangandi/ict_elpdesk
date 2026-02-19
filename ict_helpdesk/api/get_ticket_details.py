import frappe

@frappe.whitelist()
def get_ticket_details(ticket_id):
    ticket = frappe.get_doc("ICT Ticket", ticket_id)

    return {
        "ticket_id": ticket.full_name,
        "mobile_no": ticket.mobile_no,
        "status": ticket.status,
        "department": ticket.department,
        }