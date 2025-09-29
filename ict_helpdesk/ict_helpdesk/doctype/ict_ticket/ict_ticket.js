// Copyright (c) 2025, Pantech Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on("ICT Ticket", {
    // Auto populating requester details from personal_number
    personal_number: function(frm){
        if(!frm.doc.personal_number) return;

        frappe.call({
            method: "ict_helpdesk.api.get_user_data.ticket_personal_num",
            args: {personal_number: frm.doc.personal_number},
            callback: function(r){
                console.log(r.message) // For Testing TODO: delete 
                const full_name = r.message.first_name+ " " + r.message.middle_name + " " + r.message.last_name;
                frm.set_value("full_name", full_name);
                frm.set_df_property("full_name", "hidden", 0);
                frm.refresh_field("full_name");
                const fields = [
                    "phone_number", "email", "mobile_no","department", "directorate", "location", "designation"
                ]
                fields.forEach(function(fieldname) {
                    if(r.message[fieldname]){
                        frm.set_value(fieldname, r.message[fieldname]);
                        frm.set_df_property(fieldname, "hidden", 0);
                        frm.refresh_field(fieldname);
                    }
                });
            }
        })
    },
    tag_number: function(frm){
        if(!frm.doc.tag_number) return;

        if (frm.doc.tag_number){ 
            frappe.call({
                method: "ict_helpdesk.api.device_data.get_tag_number",
                args: {"tag_number": frm.doc.tag_number},
                callback: function(r){
                    console.log(r.message);
                    const fields = [
                        "serial_number","county_device_type", "device_model", "device_ram", "device_storage", 
                        "device_department", "device_directorate", "device_office", "officer_in_charge"
                    ]
                    const specific_fields = [
                        "device_ram", "device_storage"
                    ]
                    // if device is all-in-one || laptop || system unit then show ram and storage
                    fields.forEach(function(fieldname) {
                        if(r.message[fieldname]){
                            frm.set_value(fieldname, r.message[fieldname]);
                            frm.set_df_property(fieldname, "hidden", 0);
                            frm.refresh_field(fieldname);
                        }
                    });
                    if(r.message.device_name == "All in One" || r.message.device_name == "Laptop" || r.message.device_name == "System Unit"){
                        specific_fields.forEach(function(fieldname){
                            if(r.message[fieldname]){
                                frm.set_value(fieldname, r.message[f]);
                                frm.set_df_property(fieldname, "hidden", 0);
                                frm.refresh_field(fieldname);
                            }
                        });
                    }

                }
            });
        }
    },
    serial_number: function (frm){
        if(!frm.doc.serial_number) return;

        frappe.call({
            method: "ict_helpdesk.api.device_data.get_serial_num" ,
            args: {"serial_number": frm.doc.serial_number},
            callback: function(r){
                console.log(r.message);
                const fields = [
                    "tag_number","device_name", "device_model", 
                    "device_department", "device_directorate", "device_office", "officer_in_charge"
                ]
                const specific_fields = [
                    "device_ram", "device_storage"
                ]
                // if device is all-in-one || laptop || system unit then show ram and storage
                fields.forEach(function(fieldname) {
                    if(r.message[fieldname]){
                        frm.set_value(fieldname, r.message[fieldname]);
                        frm.set_df_property(fieldname, "hidden", 0);
                        frm.refresh_field(fieldname);
                    }
                });
                if(r.message.device_name == "All in One" || r.message.device_name == "Laptop" || r.message.device_name == "System Unit"){
                    specific_fields.forEach(function(fieldname){
                        if(r.message[fieldname]){
                            frm.set_value(fieldname, r.message[f]);
                            frm.set_df_property(fieldname, "hidden", 0);
                            frm.refresh_field(fieldname);
                        }
                    });
                }
            }
        });
    },
    software_issue_check: function(frm){
        if(software_issue_check == 0){
            const software_section = [
                "software_issue_select", "software_issue_description"
            ]
            software_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
            });
            frm.refresh_field(software_section);
        }
        // Remeber revenue is under finance
        // TODO: Fill in the departments and their directories
        const finance_issues = [
            "IFMIS", "IB", "Windows"
        ]
        const hr_issues = [
            "Windows", "Excel", "office"
        ]
        const health_issues = [
            "SHA Portal", "Windows", "Office"
        ]
        // Check department and directorate
        if(frm.doc.department == "Finance and Economic PLanning"){
            finance_issues.forEach(function (fieldname){
                frm.set_df_property("software_issue_type", "options", finance_issues.join("\n"));
                frm.refresh_field(fieldname);
            })
        }
        if(frm.doc.department == "Health Services"){
            health_issues.forEach(function (fieldname){
                frm.set_df_property("software_issue_type", "options", health_issues.join("\n"));
                frm.refresh_field(fieldname);
            });
        }
        if(frm.doc.department == "Devolution"){
            health_issues.forEach(function (fieldname){
                frm.set_df_property("software_issue_type", "options", hr_issues.join("\n"));
                frm.refresh_field(fieldname);
            });
        }
    },
     // CLEAR FIELDS IF CHECK UNCHECKED: IF FAILS FALL TO RELOAD THE WHOLE PAGE
    hardware_issue_check: function(frm){
        if(frm.doc.hardware_issue_check == 0){
            const hardware_section = [
                "county_device_check", "tag_nuber", "serial_number", "device_name", "device_model", "device_ram","device_storage",
                "device_department", "device_directorate", "device_office", "officer_in_charge", "device_status"
            ]
            hardware_section.forEach(function(fieldname){
                frm,set_value(fieldname, null);
                frm.refresh_field(fieldname);
            });
            
        }
    },
    county_device_check: function(frm){
        if(frm.doc.county_device_check == 0){
            const device_section = [
                "tag_nuber", "serial_number", "device_name", "device_model", "device_ram","device_storage",
                "device_department", "device_directorate", "device_office", "officer_in_charge", "device_status"
            ]
            device_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
                frm.refresh_field(fieldname);
            });
            
        }
    },
    internet_issue_check: function(frm){
        if(internet_issue_check == 0){
            const internet_section = [
                "internet_issue_type", "internet_issue_description"
            ]
            internet_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
                frm.refresh_field(fieldname);
            });
            
        }
    },
     clearance_issue_check: function(frm){
        if(clearance_issue_check == 0){
            frm.set_value("clearance_issue_description", "");
            frm.refresh_field("clearance_issue_description");
        }
    },
    assigned_officer: function(frm){
        if(!assigned_officer){return}
        frappe.call({
            method: "ict_helpdesk.api.assigned_officer.get_assigned_officer",
            callback: function(r){
                frm.set_df_property("assigned_officer", "options", r.message.full_name);
                frm.refresh_field("assigned_officer");
            }
            })
    },
    workflow_state: function(frm) {
        const approval_fields = [
            "personal_number", "issue_summary", "image_attachment", "recurring_issue_check", "software_issue_check",
            "type_of_issue", "software_issue_description", "hardware_issue_check", "hardware_issue_description", 
            "county-device_check", "tag_number","serial_number", "internet_issue_check", "internet_issue_type", 
            "internet_issue_description", "clearance_issue_check", "clearance_issue_description"
        ];

        const progress_fields = [
            ...approval_fields,
            "issue_priority", "assigned_officer", "assigned_officer_email", "assigned_officer_phone"
        ];

        const resolved_fields = [
            ...progress_fields,
            "delegate_to", "report_attachment","report", "resolve_issue_check"
        ];

        if(frm.doc.workflow_state == "Awaiting Approval"){
            approval_fields.forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
            });
            frm.refresh_fields(approval_fields);

            frappe.call({
                method: "ict_helpdesk.api.assigned_officer.get_ict_officers",
                callback: function(r) {
                    if (r.message) {
                        let options = [""];
                        r.message.forEach(officer => {
                            options.push(officer.full_name);
                        });

                        frm.set_df_property("assigned_officer", "options", options);
                        frm.refresh_field("assigned_officer");
                    }
                }
            });

        }
        else if(["In Progress", "On Hold", "Delegated"].includes(frm.doc.workflow_state)){
            progress_fields.forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
            });
            frm.refresh_fields(progress_fields);

        }
        else if(frm.doc.workflow_state == "Resolved"){
            resolved_fields.forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
            });
            frm.refresh_fields(resolved_fields);

        }
        else if(frm.doc.workflow_state == "Awaiting Review"){
            ["report_attachment", "report"].forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 0);
            });
            frm.refresh_fields(["report_attachment", "report"]);

        }
        else if(frm.doc.workflow_state == "Completed"){
            // Lock ALL fields on the form
            Object.keys(frm.fields_dict).forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
            });
            frm.refresh_fields();
        }
    },
    // AUTO POPULATE ASSIGNED OFFICER EMAIL & MOBILE NO
     assigned_officer: function(frm) {
        if (!frm.doc.assigned_officer) return;

        frappe.call({
            method: "ict_helpdesk.api.assigned_officer.get_officer_details",
            args: {
                officer_name: frm.doc.assigned_officer
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("assigned_officer_email", r.message.email);
                    frm.set_value("assigned_officer_phone", r.message.mobile_no);
                    // TODO:  See if refresh is needed
                }
            }
        });
    },
    before_workflow_action: function (frm) {
        if (frm.selected_workflow_action && frm.selected_workflow_action.to_state === "Awaiting Approval") {
            if(!frm.doc.personal_number){
                frappe.throw(__("Please enter your Personal Number before sending for approval"));
            }
        }
        else if (frm.selected_workflow_action && frm.selected_workflow_action.to_state === "In Progress") {
            if (!frm.doc.priority || !frm.doc.assigned_to) {
                frappe.throw(__("Please set both Priority and Assigned Officer before moving to In Progress"));
            }
        }
        else if (frm.selected_workflow_action && frm.selected_workflow_action.to_state === "Resolved") {
            if(frm.doc.resolve_ticket_check == 0){
                frappe.throw(__("Please confirm the issue is resolved by checking the Resolve Issue Check box"));
            }
        }
        else if (frm.selected_workflow_action && frm.selected_workflow_action.to_state === "Awaiting Review") {
            if((!frm.doc.report || frm.doc.report_attachment) && frm.doc.resolve_ticket_check == 0){
                frappe.throw(__("Please write or attach a report before sending for review"));
            }
        }
        else if(frm.selected_workflow_action && frm.selected_workflow_action.to_state === "Completed"){
            if(frm.doc.completed_check == 0){
                frappe.throw(__("Please confirm the ticket is completed by checking the Completed Check box"));
            }
        }
    },
	refresh(frm) {

	},
    validate: function(frm) {
        if (!frm.doc.software_issue_check && !frm.doc.hardware_issue_check && !frm.doc.internet_issue_check && !frm.doc.clearance_issue_check) {
            frappe.throw(__("You must select at least one issue type: Software, Hardware, or Clearance."));
        }
    },
});
