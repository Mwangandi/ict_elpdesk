// Copyright (c) 2025, Pantech Solutions and contributors
// For license information, please see license.txt

function rename_and_hide_buttons() {
    setTimeout(() => {
        // Rename the Save button to Submit
        const save_btn = $('.primary-action');
        if (save_btn.length) {
            save_btn.text('Submit');
            save_btn.attr('data-label', 'Submit');
        }

        // Hide workflow buttons and dropdowns
        $('.actions-btn-group').hide();
        $('.workflow-button, .btn-workflow').hide();
        $('.menu-btn-group').hide(); // Optional: hide 3-dot menu
    }, 500);
}
   
frappe.ui.form.on("ICT Ticket", {
    before_save(frm) {
        // TODO: Make sure you complete this for the on-hold, delegate
        if (frm.doc.workflow_state === "Open") {
            frm._auto_workflow_action = "Send for Approval";
        } else if (frm.doc.workflow_state === "Awaiting Approval") {
            frm._auto_workflow_action = "Approve";
        } else if (frm.doc.workflow_state === "In Progress") {
            frm._auto_workflow_action = "Resolve";
        } else if (frm.doc.workflow_state === "On Hold") {
            frm._auto_workflow_action = "Resolve";
        } else if (frm.doc.workflow_state === "Delegated") {
            frm._auto_workflow_action = "Resolve";
        } else if (frm.doc.workflow_state === "Resolved") {
            frm._auto_workflow_action = "Send for Review";
        } else if (frm.doc.workflow_state === "Awaiting Review") {
            frm._auto_workflow_action = "Complete";
        }
    },

    after_save(frm) {
        if (frm._auto_workflow_action) {
            frappe.xcall("frappe.model.workflow.apply_workflow", {
                doc: frm.doc,
                action: frm._auto_workflow_action
            }).then(() => {
                frm.reload_doc();
            }).catch(err => {
                frappe.msgprint({
                    title: __("Workflow transition failed"),
                    message: err.message || __("An error occurred while applying workflow."),
                    indicator: "red"
                });
            }).finally(() => {
                delete frm._auto_workflow_action;
            });
        }
    },

    //=========================================================
    onload_post_render: function(frm) {

        // Check if grecaptcha is available
        console.log('grecaptcha available:', typeof grecaptcha !== 'undefined');
        
        if (typeof grecaptcha === 'undefined') {
            console.error('reCAPTCHA library not loaded!');
        }

        // Hide Actions dropdown
        $('.actions-btn-group').hide();
        rename_and_hide_buttons();

        let save_btn = $('.primary-action');
        if (save_btn.length) {
            save_btn.text('Submit');
            save_btn.attr('data-label', 'Submit');
        }

        // Hide workflow buttons
        $('.workflow-button, .btn-workflow').hide();

        frm.events.apply_workflow_rules(frm);
        frm.events.serial_number(frm);
        frm.events.tag_number(frm);
        frm.events.validate_workflow_transition(frm);
        //====================
        if (frm.is_new()){
            frappe.call({
            method: "ict_helpdesk.api.get_user_data.ticket_personal_number",
            // args: {personal_number: frm.doc.personal_number},
            callback: function(r){ 
                console.log(r.message)
                const full_name = r.message.first_name+ " " + r.message.middle_name + " " + r.message.last_name;
                frm.set_value("full_name", full_name);
                frm.set_df_property("full_name", "hidden", 0);
                frm.refresh_field("full_name");
                const fields = [
                    "personal_number","phone_number", "email", "mobile_no","department", "directorate", "location", "designation"
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
        }
        // reacptcha script
        // Always change this code when changin the site key
        if (!window.grecaptcha) {
            $.getScript('https://www.google.com/recaptcha/api.js?render=6LcVAm4sAAAAANQ6bh6pGBGqdaiaZ0OQqEb-9Y6B');
        }
    },
    // after_save(frm) {
    //     // Check if the current workflow action is "Send for Approval"
    //     if (frm.doc.workflow_state === "Awaiting Approval" && frm.doc._last_workflow_action === "Send for Approval") {
    //         window.location.href("/app/ict-ticket");
    //     }
    // },
    refresh: function(frm) {
        // RENAME SAVE BUTTON TO SUBMIT
        rename_and_hide_buttons();

        // let save_btn = $('.primary-action');
        // if (save_btn.length) {
        //     save_btn.text('Submit');
        //     save_btn.attr('data-label', 'Submit');
        // }
        // ============================================
        setTimeout(() => {
            $('.actions-btn-group, .workflow-button, .btn-workflow').hide();
        }, 500);
        // ============================================
        frm.events.apply_workflow_rules(frm);
        frm.events.set_department_software_options(frm);
        frm.events.validate_workflow_transition(frm);
        frm.recaptcha_verified = false;
        setTimeout(() => {
            $(".form-message-container:contains('This form is not editable due to a Workflow.')").hide();
        }, 300);

        frm.fields_dict.image_preview_id.$wrapper.empty();

        // Check if image is attached
        if (frm.doc.image_attachment) {
            let image_url = frm.doc.image_attachment.startsWith('/')
                ? frm.doc.image_attachment
                : '/' + frm.doc.image_attachment;

            // Build preview
            frm.fields_dict.image_preview_id.$wrapper.html(`
                <div style="margin-top: 8px;">
                    <a href="${image_url}" target="_blank">
                        <img src="${image_url}" 
                             style="max-width: 250px; border: 1px solid #ddd; border-radius: 6px; padding: 3px;">
                    </a>
                </div>
            `);
        } else {
            frm.fields_dict.image_preview_id.$wrapper.html(
                `<span style="color: gray;">No image attached</span>`
            );
        }

        if (!frm.is_new()) {
            // Make sure fields remain read-only after save
            const fields = [
                "personal_number",
                "full_name",
                "phone_number",
                "email",
                "mobile_no",
                "department",
                "directorate",
                "location",
                "designation"
            ];

            fields.forEach(fieldname => {
                frm.set_df_property(fieldname, "read_only", 1);
                frm.set_df_property(fieldname, "hidden", 0);
            });
            frm.refresh_fields(fields);
        }
        if (frm.doc.workflow_state === "Awaiting Approval" && frm.doc._last_workflow_action === "Send for Approval" && frappe.user_roles.includes("Requester")) {
            // window.location.href = "/app/ict-ticket";
            frappe.set_route("/app/ict-ticket");
        }
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

        // frm.refresh_fields();
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
        // TODO: Add more fields
        const finance_issues = ["IFMIS", "IB", "Windows","Antivirus"];
        const hr_issues = ["Windows", "Excel", "Office","Antivirus"];
        const health_issues = ["SHA Portal", "Windows", "Office"];
        const revenue_issues = ["iTax", "Windows", "Office"];

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
            frm.set_df_property("software_issue_type", "options", ["Windows", "Office"].join("\n"));
        }

        frm.refresh_field("software_issue_type");
    },

// ======================================== AUTO POPULATING PERSONAL NUMBER ===========================================================================
    // personal_number: function(frm){
    //     if(!frm.doc.personal_number) return;

    //     frappe.call({
    //         method: "ict_helpdesk.api.get_user_data.ticket_personal_number",
    //         // TODO: Auto fetch from user info instead of manual entry
    //         // args: {personal_number: frm.doc.personal_number},
    //         callback: function(r){ 
    //             const full_name = r.message.first_name+ " " + r.message.middle_name + " " + r.message.last_name;
    //             frm.set_value("full_name", full_name);
    //             frm.set_df_property("full_name", "hidden", 0);
    //             frm.refresh_field("full_name");
    //             const fields = [
    //                 "phone_number", "email", "mobile_no","department", "directorate", "location", "designation"
    //             ]
    //             fields.forEach(function(fieldname) {
    //                 if(r.message[fieldname]){
    //                     frm.set_value(fieldname, r.message[fieldname]);
    //                     frm.set_df_property(fieldname, "hidden", 0);
    //                     frm.refresh_field(fieldname);
    //                 }
    //             });
    //         }
    //     });
    // },
    //  p_num: function(frm){
    //     if(!frm.doc.personal_number) return;

    //     frappe.call({
    //         method: "ict_helpdesk.api.get_user_data.ticket_personal_number",
    //         // TODO: Auto fetch from user info instead of manual entry
    //         // args: {personal_number: frm.doc.personal_number},
    //         callback: function(r){ 
    //             console.log(r.message)
    //             const full_name = r.message.first_name+ " " + r.message.middle_name + " " + r.message.last_name;
    //             frm.set_value("full_name", full_name);
    //             frm.set_df_property("full_name", "hidden", 0);
    //             frm.refresh_field("full_name");
    //             const fields = [
    //                 "phone_number", "email", "mobile_no","department", "directorate", "location", "designation"
    //             ]
    //             fields.forEach(function(fieldname) {
    //                 if(r.message[fieldname]){
    //                     frm.set_value(fieldname, r.message[fieldname]);
    //                     frm.set_df_property(fieldname, "hidden", 0);
    //                     frm.refresh_field(fieldname);
    //                 }
    //             });
    //         }
    //     });
    // },
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
                    if(r.message.device_name == "All in One" || r.message.device_name == "Laptop" || r.message.device_name == "System Unit" || r.message.device_name == "phone" || r.message.device_name == "Tablet" || r.message.device_name == "Server"){
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
                        frm.set_df_property(fieldname, "read", 1);
                        frm.refresh_field(fieldname);
                    }
                });
                if(r.message.device_name == "All in One" || r.message.device_name == "Laptop" || r.message.device_name == "System Unit"){
                    specific_fields.forEach(function(fieldname){
                        if(r.message[fieldname]){
                            frm.set_value(fieldname, r.message[fieldname]);
                            frm.set_df_property(fieldname, "hidden", 0);
                            frm.set_df_property(fieldname, "read", 1);
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
                "county_device_check","personal_device", "tag_number", "serial_number", "device_name", "device_model", "device_ram","device_storage",
                "device_department", "device_directorate", "device_office", "officer_in_charge", "device_status"
            ]
            hardware_section.forEach(function(fieldname){
                frm.set_value(fieldname, "");
                frm.refresh_field(fieldname);
            });
            frm.refresh_field(["county_device_check","personal_device", "tag_number", "serial_number", "device_name", "device_model", "device_ram","device_storage",
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
                if (r.message && r.message.designation != "ICT Director") {
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
            grecaptcha.execute('6LcVAm4sAAAAANQ6bh6pGBGqdaiaZ0OQqEb-9Y6B', { action: 'submit_ticket' })
                .then(function(token) {
                    frappe.call({
                        method: "ict_helpdesk.api.recaptcha.verify_recaptcha",
                        args: { token: token },
                        callback: function(r) {
                            if (r.message === true) {
                                frm.recaptcha_verified = true;
                                frappe.validated = true;
                                frm.save();
                            } else {
                                frappe.msgprint(__('reCAPTCHA verification failed. Please try again.'));
                            }
                        }
                    });
                });
        });
    }
});
