import frappe
from .sms import send_custom_sms as sms
from .get_director import get_director
 

# Director information
director = get_director()

if director:
    director_email = director.get("email")
    director_mobile = director.get("mobile_no")
else:
    frappe.log_error("No ICT Director found in ICT Staff", "Notification Error")
    director_email = None
    director_mobile = None


# send_custom_sms takes two parameters: number (string) and message(string)
@frappe.whitelist(allow_guest=False)
def send_notification(doc, method):
    # requester info
    requester_name = doc.full_name
    requester_email = doc.email
    requester_phone_number = doc.mobile_no
    requester_department = doc.department
    requester_location = doc.location

    # assigned officer info
    assigned_to = doc.assigned_officer
    assigned_to_email = doc.assigned_officer_email
    assigned_to_mobile = doc.assigned_officer_mobile

    if doc.has_value_changed("workflow_state") and doc.workflow_state == "Awaiting Approval":
        # send sms to directors
        director_message = f"New ICT Ticket {doc.name} from {requester_name},\n Dept: {requester_department},\n Location: {requester_location}. \nPlease review and approve."
        sms(director_mobile, director_message)
        # send email to directors
        frappe.sendmail(
            recipients=[director_email],
            subject=f"New ICT Ticket {doc.name} from {requester_department} Awaiting Approval",
            message=director_message
        )

        #send sms to requester
        requester_message = f"Your ICT Ticket {doc.name} has been created and is awaiting approval."
        sms(requester_phone_number, requester_message)

        # send email to requester
        frappe.sendmail(
            recipients=[requester_email],
            subject=f"New ICT Ticket {doc.name} Awaiting Approval",
            message=requester_message
        )

    elif doc.workflow_state == "In Progress":
        # send sms to assigned_to
        # TODO: Ensure assigned_to_mobile is a field in the doctype
        message_to_assigned = f"ICT Ticket {doc.name} has been assigned to you.\n Please take the necessary actions to resolve it."
        sms(assigned_to_mobile, message_to_assigned)
        # send email to assigned_to
        frappe.sendmail(
            recipients=[assigned_to_email],
            subject=f"ICT Ticket {doc.name} Assigned to You",
            message=message_to_assigned
        )

        # send sms to requester
        requester_progress_msg = f"Your ICT Ticket {doc.name} is now In Progress and being handled by {assigned_to}."
        sms(requester_phone_number, requester_progress_msg)
        # send email to requester
        frappe.sendmail(
            recipients=[requester_email],
            subject=f"ICT Ticket {doc.name} In Progress",
            message=requester_progress_msg
        )

    elif doc.workflow_state == "Delegated":
        intern_name = doc.delegated_to.intern_name
        intern_mobile = doc.delegated_to.intern_mobile
        intern_email = doc.delegated_to.intern_email
        # send sms to intern
        intern_message = f"ICT Ticket {doc.name} has been delegated to you.\n Please take the necessary actions to resolve it."
        sms(intern_mobile, intern_message)

        # send email to intern
        frappe.sendmail(
            recipients=[intern_email],
            subject=f"ICT Ticket {doc.name} Delegated to You",
            message=intern_message
        )

        # send sms to requester
        requester_delegate_msg = f"Your ICT Ticket {doc.name} has been delegated to {intern_name} for resolution."
        sms(requester_phone_number, requester_delegate_msg)

        # send email to requester
        frappe.sendmail(
            recipients=[requester_email],
            subject=f"ICT Ticket {doc.name} Delegated",
            message=requester_delegate_msg
        )

        # send sms to directors
        director_delegate_msg = f"ICT Ticket {doc.name} assigned to officer {assigned_to} has been delegated to {intern_name}."
        sms(director_mobile, director_delegate_msg)

        # send email to directors
        frappe.sendmail(
            recipients=[director_email],
            subject=f"ICT Ticket {doc.name} Delegated",
            message=director_delegate_msg
        )

    elif doc.workflow_state == "On Hold":
        # send sms to directors
        director_on_hold_msg = f"ICT Ticket {doc.name} assigned to officer {assigned_to} has been put On Hold awaiting further updates."
        sms(director_mobile, director_on_hold_msg)

        # send email to directors
        frappe.sendmail(
            recipients=[director_email],
            subject=f"ICT Ticket {doc.name} On Hold",
            message=director_on_hold_msg
        )

        # send sms to requester
        requester_on_hold_msg = f"Your ICT Ticket {doc.name} has been put On Hold awaiting further updates."
        sms(requester_phone_number, requester_on_hold_msg)

        # send email to requester
        frappe.sendmail(
            recipients=[requester_email],
            subject=f"ICT Ticket {doc.name} On Hold",
            message=requester_on_hold_msg
        )

    elif doc.workflow_state == "Resolved":
        # send sms to requester
        requester_resolved_msg = f"Your ICT Ticket {doc.name} has been resolved."
        sms(requester_phone_number, requester_resolved_msg)

        # send email to requester
        frappe.sendmail(
            recipients=[requester_email],
            subject=f"ICT Ticket {doc.name} Resolved",
            message=requester_resolved_msg
        )

        # send sms to directors
        director_resolved_msg = f"ICT Ticket {doc.name} assigned to officer {assigned_to} has been resolved. Pending review."
        sms(director_mobile, director_resolved_msg)

        # send email to directors
        frappe.sendmail(
            recipients=[director_email],
            subject=f"ICT Ticket {doc.name} Resolved",
            message=director_resolved_msg
        )
    elif doc.workflow_state == "Completed":
        # send sms to requester
        requester_completed_msg = f"Your ICT Ticket {doc.name} has been completed. Thank you for your patience."
        sms(requester_phone_number, requester_completed_msg)

        # send email to requester
        frappe.sendmail(
            recipients=[requester_email],
            subject=f"ICT Ticket {doc.name} Completed",
            message=requester_completed_msg
        )

        # send sms to directors
        director_completed_msg = f"ICT Ticket {doc.name} assigned to officer {assigned_to} has been completed."
        sms(director_mobile, director_completed_msg)

        # send email to directors
        frappe.sendmail(
            recipients=[director_email],
            subject=f"ICT Ticket {doc.name} Completed",
            message=director_completed_msg
        )
         