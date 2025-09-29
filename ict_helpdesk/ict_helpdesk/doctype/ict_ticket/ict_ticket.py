# Copyright (c) 2025, Pantech Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ICTTicket(Document):
    def validate(self):
        if not (self.software_issue_check or self.hardware_issue_check or self.clearance_issue_check or self.internet_issue_check):
            frappe.throw("You must select at least one issue type: Software, Hardware, or Clearance.")
	

