// Copyright (c) 2025, Pantech Solutions and contributors
// For license information, please see license.txt
   
frappe.ui.form.on("ICT Ticket", {
    onload_post_render: function(frm) {
        frm.events.apply_workflow_rules(frm);
        frm.events.validate_workflow_transition(frm);
        // reacptcha script
        if (!window.grecaptcha) {
            $.getScript('https://www.google.com/recaptcha/api.js?render=6Ld4PeErAAAAALE3KDQlh2aMtYpGuKEOwiQVW9EN');
        }
    },
    refresh: function(frm) {
        frm.events.apply_workflow_rules(frm);
        frm.events.set_department_software_options(frm);
        frm.events.validate_workflow_transition(frm);
        frm.recaptcha_verified = false;
    },
    department: function(frm) {
        frm.events.set_department_software_options(frm);
    },
    workflow_state: function(frm){
        frm.events.validate_workflow_transition(frm);
        frm.events.apply_workflow_rules(frm);
    },

    validate_workflow_transition: function(frm) {
        if (!frm.doc.workflow_action || !frm.doc.workflow_action.to_state) return;

        const validators = {
            "Awaiting Approval": () => {
                if (!frm.doc.personal_number) {
                    frappe.throw(__("Please enter your Personal Number before sending for approval"));
                }
            },
            "In Progress": () => {
                if (!frm.doc.issue_priority || !frm.doc.assigned_officer) {
                    frappe.throw(__("Please set both Priority and Assigned Officer before moving to In Progress"));
                }
            },
            "Resolved": () => {
                if (frm.doc.resolve_issue_check == 0) {
                    frappe.throw(__("Please confirm the issue is resolved by checking the Resolve Issue Check box"));
                }
            },
            "Awaiting Review": () => {
                if ((!frm.doc.report && !frm.doc.report_attachment) || frm.doc.resolve_issue_check == 0) {
                    frappe.throw(__("Please write or attach a report before sending for review"));
                }
            },
            "Completed": () => {
                if (frm.doc.ticket_complete == 0) {
                    frappe.throw(__("Please confirm the ticket is completed by checking the Completed Check box"));
                }
            }
        };
         // Run validator if it exists for the target state
        if (validators[action.to_state]) {
            validators[action.to_state]();
        }
    },
    apply_workflow_rules: function(frm) {
        const approval_fields = [
            "issue_summary", "image_attachment", "recurring_issue_check", "software_issue_check",
            "software_issue_type", "software_issue_description", "hardware_issue_check", "hardware_issue_description", 
            "county_device_check", "personal_number", "tag_number", "serial_number",
            "internet_issue_check", "internet_issue_type", "internet_issue_description",
            "clearance_issue_check", "clearance_issue_description"
        ];

        const progress_fields = [
            ...approval_fields,
            "issue_priority", "assigned_officer", "assigned_officer_email", "assigned_officer_mobile","issue_delegation_check"
        ];

        const resolved_fields = [
            ...progress_fields,
            "delegate_to", "report_attachment", "report", "resolve_issue_check"
        ];


        if (frm.doc.workflow_state === "Awaiting Approval") {
            approval_fields.forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
            });

            frappe.call({
                method: "ict_helpdesk.api.assigned_officer.get_ict_officers",
                callback: function(r) {
                    if (r.message) {
                        let options = [""];
                        r.message.forEach(officer => {
                            options.push(officer.full_name);
                        });
                        frm.set_df_property("assigned_officer", "options", options.join("\n"));
                        frm.refresh_field("assigned_officer");
                    }
                }
            });
        }
        else if (frm.doc.workflow_state === "In Progress" || frm.doc.workflow_state === "On Hold" || frm.doc.workflow_state === "Delegated") {
            if (!frm.doc.issue_priority || !frm.doc.assigned_officer) {
                frappe.throw(__("Please set both Priority and Assigned Officer before moving to In Progress"));
            }
            progress_fields.forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
                frm.set_df_property(fieldname, "hidden", 0);
            });
        }
        else if (frm.doc.workflow_state === "Resolved") {
            resolved_fields.forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
            });
        }
        else if (frm.doc.workflow_state === "Awaiting Review") {
            ["report_attachment", "report"].forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 0);
            });
            frm.refresh_fields(["report_attachment", "report"]);
            resolved_fields.forEach(function(fieldname){
                frm.set_df_property(fieldname, "read_only", 1);
            });
            frm.refresh_fields(resolved_fields);
        }
        else if (frm.doc.workflow_state === "Completed") {
            Object.keys(frm.fields_dict).forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
            });
        }

        frm.refresh_fields();
    },

    // DEPARTMENT AUTO POPULATE
    set_department_software_options: function(frm) {
        if (frm.doc.software_issue_check == 0) {
            const software_section = ["software_issue_type", "software_issue_description"];
            software_section.forEach(fieldname => {
                frm.set_value(fieldname, "");
                frm.refresh_field(fieldname);
            });
        }

        const finance_issues = ["IFMIS", "IB", "Windows"];
        const hr_issues = ["Windows", "Excel", "Office"];
        const health_issues = ["SHA Portal", "Windows", "Office"];

        if (frm.doc.department == "Finance and Economic Planning") {
            frm.set_df_property("software_issue_type", "options", finance_issues.join("\n"));
        }
        else if (frm.doc.department == "Health Services") {
            frm.set_df_property("software_issue_type", "options", health_issues.join("\n"));
        }
        else if (frm.doc.department == "Devolution") {
            frm.set_df_property("software_issue_type", "options", hr_issues.join("\n"));
        }
        else {
            // fallback options so it's never empty
            frm.set_df_property("software_issue_type", "options", ["Select an Option", "Windows", "Office"].join("\n"));
        }

        frm.refresh_field("software_issue_type");
    },

// ======================================== AUTO POPULATING PERSONAL NUMBER ===========================================================================
    personal_number: function(frm){
        if(!frm.doc.personal_number) return;

        frappe.call({
            method: "ict_helpdesk.api.get_user_data.ticket_personal_num",
            args: {personal_number: frm.doc.personal_number},
            callback: function(r){ 
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
        });
    },
// ============================================================================================================================================

// ===================================================== AUTOPOPULATING DEVICE ========================================================================
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
        if(frm.doc.software_issue_check == 0){
            const software_section = [
                "software_issue_type",
                "software_issue_description"
            ];
            software_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
            });
            frm.refresh_field(software_section);
        }
    },
    hardware_issue_check: function(frm){
        if(frm.doc.hardware_issue_check == 0){
            const hardware_section = [
                "county_device_check", "tag_number", "serial_number", "device_name", "device_model", "device_ram","device_storage",
                "device_department", "device_directorate", "device_office", "officer_in_charge", "device_status"
            ]
            hardware_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
                frm.refresh_field(fieldname);
            });
            frm.refresh_field(["county_device_check", "tag_number", "serial_number", "device_name", "device_model", "device_ram","device_storage",
                "device_department", "device_directorate", "device_office", "officer_in_charge", "device_status"])
        }
    },
    county_device_check: function(frm){
        if(frm.doc.county_device_check == 0){
            const device_section = [
                "tag_number", "serial_number", "device_name", "device_model", "device_ram","device_storage",
                "device_department", "device_directorate", "device_office", "officer_in_charge", "device_status"
            ]
            device_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
            });
            frm.refresh_field(device_section);
        }
    },
    internet_issue_check: function(frm){
        if(frm.doc.internet_issue_check == 0){
            const internet_section = [
                "internet_issue_type", "network_issue_description"
            ]
            internet_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
            });
            frm.refresh_field(internet_section);
        }
    },
    clearance_issue_check: function(frm){
        if(frm.doc.clearance_issue_check == 0){
            frm.set_value("clearance_issue_description", "");
            frm.refresh_field("clearance_issue_description");
        }
    },
    assigned_officer: function(frm) {
        if (!frm.doc.assigned_officer) return;

        frappe.call({
            method: "ict_helpdesk.api.assigned_officer.get_officer_details",
            args: {
                officer_name: frm.doc.assigned_officer
            },
            callback: function(r) {
                if (r.message) {
                    console.log(r.message);
                    frm.set_value("assigned_officer_email", r.message.email);
                    frm.set_df_property("assigned_officer_email", "hidden", 0);
                    frm.set_value("assigned_officer_mobile", r.message.mobile_no);
                    frm.set_df_property("assigned_officer_mobile", "hidden", 0);
                    frm.refresh_fields(["assigned_officer_email", "assigned_officer_mobile"]);
                }
            }
        });
    },
    validate: function(frm) {
        // Prevent infinite loop: skip if already verified
        if (frm.recaptcha_verified) {
            frappe.validated = true;

            // Now check your other conditions
            if (
                !frm.doc.software_issue_check &&
                !frm.doc.hardware_issue_check &&
                !frm.doc.internet_issue_check &&
                !frm.doc.clearance_issue_check
            ) {
                frappe.throw(__("You must select at least one issue type: Software, Hardware, Internet, or Clearance."));
            }

            return; // Allow normal save
        }

        // Stop normal validation flow until reCAPTCHA passes
        frappe.validated = false;

        grecaptcha.ready(function() {
            grecaptcha.execute('6Ld4PeErAAAAALE3KDQlh2aMtYpGuKEOwiQVW9EN', { action: 'submit_ticket' })
                .then(function(token) {
                    frappe.call({
                        method: "ict_helpdesk.api.recaptcha.verify_recaptcha",
                        args: { token: token },
                        callback: function(r) {
                            if (r.message === true) {
                                // Mark verified to prevent re-loop
                                frm.recaptcha_verified = true;
                                frappe.validated = true;

                                // Save again silently
                                frm.save();
                            } else {
                                frappe.msgprint(__('reCAPTCHA verification failed. Please try again.'));
                            }
                        }
                    });
                });
        });
    },


    // validate: function(frm) {
    //     // Stop normal validation flow until reCAPTCHA passes
    //     frappe.validated = false;

    //     grecaptcha.ready(function() {
    //         grecaptcha.execute('6Ld4PeErAAAAALE3KDQlh2aMtYpGuKEOwiQVW9EN', {action: 'submit_ticket'}).then(function(token) {
    //             // Verify token server-side
    //             frappe.call({
    //                 method: "ict_helpdesk.api.recaptcha.verify_recaptcha",
    //                 args: { token: token },
    //                 callback: function(r) {
    //                     if (r.message === true) {
    //                         frappe.validated = true;
    //                         frm.events.after_recaptcha_pass(frm);
    //                     } else {
    //                         frappe.msgprint(__('reCAPTCHA verification failed. Please try again.'));
    //                     }
    //                 }
    //             });
    //         });
    //     });
    //     if (!frm.doc.software_issue_check && !frm.doc.hardware_issue_check && !frm.doc.internet_issue_check && !frm.doc.clearance_issue_check) {
    //         frappe.throw(__("You must select at least one issue type: Software, Hardware, or Clearance."));
    //     }
    // },



    // after_recaptcha_pass: function(frm) {
    // frappe.validated = true;
    // frm.save('Save');
    // }
});


