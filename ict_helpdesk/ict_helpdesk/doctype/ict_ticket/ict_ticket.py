# Copyright (c) 2025, Pantech Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

def get_permission_query_conditions(user):
    """Restrict ICT Officers to only see tickets assigned to them."""
    if not user or user == "Administrator":
        return None  # full access for admin

    # If user has role "ICT Officer"
    if "Chief ICT Officer" in frappe.get_roles(user) or "Senior ICT Officer" in frappe.get_roles(user) or "ICT Officer(I, II, III)" in frappe.get_roles(user):
        return f"""(`tabICT Ticket`.assigned_officer_email = '{user}')"""

    return None  # other roles see everything

def has_permission(doc, user):
    """Prevent officers from opening unassigned tickets directly."""
    if user == "Administrator":
        return True

    staff = frappe.db.get_value(
        "ICT Staff",
        {"email": user},
        ["email", "designation","mobile_no"],
        as_dict=True
    )

    if not staff:
        return True
    
    # Allow directors to view all
    if staff and "ICT Director" in (staff.designation or ""):
        return True
    # Restrict access to assigned tickets
    if "Chief ICT Officer" in staff.designation or "Senior ICT Officer" in staff.designation or "ICT Officer (I, II, III)" in staff.designation:
        return doc.assigned_officer_email == staff.email
    
    # Regular users only see their own
    return doc.owner == user



class ICTTicket(Document):
    def validate(self):
        if not (self.software_issue_check or self.hardware_issue_check or self.clearance_issue_check or self.internet_issue_check):
            frappe.throw("You must select at least one issue type: Software, Hardware, or Clearance.")
        # Workflow-specific checks
        if self.workflow_state == "In Progress":
            if not self.issue_priority or not self.assigned_officer:
                frappe.throw("Please set both Priority and Assigned Officer before moving to In Progress")
        elif self.workflow_state == "Resolved":
            if not self.resolve_issue_check:
                frappe.throw("Please confirm the issue is resolved by checking the Resolve Issue Check box")
            if self.resolve_issue_check and not (self.report or self.report_attachment):
                frappe.throw("Kindly write or attach your report before submitting for review")
        elif self.workflow_state == "Awaiting Review":
            if (not self.report and not self.report_attachment) or not self.resolve_issue_check:
                frappe.throw("Please write or attach a report before sending for review")
        elif self.workflow_state == "Completed":
            if not self.ticket_complete:
                frappe.throw("Please confirm the ticket is completed by checking the Completed Check box")

    def before_save(self):
        """Check if workflow_state changed to Completed"""
        if self.has_value_changed("workflow_state") and self.workflow_state == "Completed":
            self.submit_on_complete()
            
    def submit_on_complete(self):
        """Auto-submit when workflow_state changes to Completed"""
        if self.docstatus == 1 and self.workflow_state == "Completed":  # Only if it's still a draft
            try:
                self.submit()
                frappe.msgprint(f"Ticket {self.name} has been auto-submitted since it is completed.")
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Auto Submit on Completed Failed")
	

