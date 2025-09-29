# Copyright (c) 2025, Pantech Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ICTTicket(Document):
    def validate(self):
        if not (self.software_issue_check or self.hardware_issue_check or self.clearance_issue_check or self.internet_issue_check):
            frappe.throw("You must select at least one issue type: Software, Hardware, or Clearance.")
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
	

