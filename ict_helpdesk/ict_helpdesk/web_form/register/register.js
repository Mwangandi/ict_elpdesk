frappe.ready(function() {
	 $('[data-fieldname="personal_number"] input').on('blur', function() {
        let personal_number = $(this).val();

        if(personal_number) {
            frappe.call({
                method: "ict_helpdesk.api.get_user_data.get_user_details",
                args: { personal_number: personal_number },
                callback: function(r) {
                    if(r.message) {
                        // console.log(r.message)
                        const inputs = [
                            "first_name", "middle_name", "last_name", "email", "mobile_no", "department", "directorate", "location", "gender", "date_of_birth"
                        ]
                        inputs.forEach(function (fieldname){
                            if(r.message[fieldname]){
                                frappe.web_form.set_value(fieldname,  r.message[fieldname]);
                                frappe.web_form.set_df_property(fieldname, "read_only", 1);
                            }
                        })
                    } else {
                        frappe.msgprint("No record found for this Personal Number");
                    }
                }
            });
        }
    });
})