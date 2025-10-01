# Copyright (c) 2025, Pantech Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ICTTicket(Document):
    def validate(self):
        if not (self.software_issue_check or self.hardware_issue_check or self.clearance_issue_check or self.internet_issue_check):
            frappe.throw("You must select at least one issue type: Software, Hardware, or Clearance.")

    def before_workflow_action(self, action):
        if action.to_state == "Awaiting Approval" and not self.personal_number:
            frappe.throw("Please enter your Personal Number before sending for approval")

        elif action.to_state == "In Progress" and (not self.issue_priority or not self.assigned_officer):
            frappe.throw("Please set both Priority and Assigned Officer before moving to In Progress")

        elif action.to_state == "Resolved" and not self.resolve_issue_check:
            frappe.throw("Please confirm the issue is resolved by checking the Resolve Issue Check box")

        elif action.to_state == "Awaiting Review":
            if (not self.report and not self.report_attachment) or not self.resolve_issue_check:
                frappe.throw("Please write or attach a report before sending for review")

        elif action.to_state == "Completed" and not self.ticket_complete:
            frappe.throw("Please confirm the ticket is completed by checking the Completed Check box")
    def before_save(self):
        """Check if workflow_state changed to Completed"""
        if self.has_value_changed("workflow_state") and self.workflow_state == "Completed":
            self.submit_on_complete()
    def submit_on_complete(self):
        """Auto-submit when workflow_state changes to Completed"""
        if self.docstatus == 0:  # Only if it's still a draft
            try:
                self.submit()
                frappe.msgprint(f"Ticket {self.name} has been auto-submitted since it is completed.")
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Auto Submit on Completed Failed")
	

