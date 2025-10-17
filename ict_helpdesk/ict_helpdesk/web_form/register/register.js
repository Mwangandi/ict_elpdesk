frappe.ready(function() {
	 $('[data-fieldname="personal_number"] input').on('blur', function() {
        let personal_number = $(this).val();

        if(personal_number) {
            frappe.call({
                method: "ict_helpdesk.api.get_user_data.get_user_details",
                args: { personal_number: personal_number },
                callback: function(r) {
                    if(r.message) {
                        console.log(r.message)
                        const inputs = [
                            "first_name", "middle_name", "last_name", "email", "mobile_no", "department", "directorate", "location", "gender", "date_of_birth"
                        ]
                        inputs.forEach(function (fieldname){
                            if(r.message[fieldname]){
                                frappe.web_form.set_value(fieldname,  r.message[fieldname]);
                                frappe.web_form.set_df_property(fieldname, "read_only", 1);
                            }
                        })
                    }
                }
            });
            frappe.call({
                method: "ict_helpdesk.api.user_signup.create_requester_user",
                args: {
                    personal_number: document.getElementById("personal_number").value,
                    first_name: document.getElementById("first_name").value,
                    middle_name: document.getElementById("middle_name").value,
                    last_name: document.getElementById("last_name").value,
                    mobile_no: document.getElementById("mobile_no").value,
                    department: document.getElementById("department").value,
                    directorate: document.getElementById("directorate").value,
                    email: document.getElementById("email").value,
                    location: document.getElementById("location").value,
                    gender: document.getElementById("gender").value
                },
                callback: function(r) {
                    if (r.message.status === "success") {
                        frappe.msgprint("Account created successfully. You can now log in using the default password: default123");
                    } else if (r.message.status === "exists") {
                        frappe.msgprint("User already exists. Please log in instead.");
                    } else {
                        frappe.msgprint("Something went wrong while creating your account.");
                    }
                }
            });

        }
    });
})

// frappe.web_form.after_load = () => {
//     const personalField = frappe.web_form.get_field("personal_number");

//     // Debounce utility — waits until user stops typing
//     const debounce = (func, delay) => {
//         let timer;
//         return (...args) => {
//             clearTimeout(timer);
//             timer = setTimeout(() => func.apply(this, args), delay);
//         };
//     };

//     // Function to fetch user data silently
//     const fetchUserData = () => {
//         const personal_number = personalField.get_value()?.trim();

//         // Only fetch if personal number looks complete (adjust min length if needed)
//         if (!personal_number) return;

//         frappe.call({
//             method: "ict_helpdesk.api.get_user_data.get_user_details",
//             args:{ personal_number: personal_number },
//             callback: function(r) {
//                 console.log(r.message)
//                 // If no record found, allow manual entry — no message shown
//                 if (!r.message) return;

//                 // If record found, auto-fill and lock fields
//                 const fields = [
//                     "first_name", "middle_name", "last_name",
//                     "email", "mobile_no", "department",
//                     "directorate", "location", "gender", "date_of_birth"
//                 ];

//                 fields.forEach(fieldname => {
//                     if (r.message[fieldname]) {
//                         frappe.web_form.set_value(fieldname, r.message[fieldname]);
//                         frappe.web_form.set_df_property(fieldname, "read_only", 1);
//                     } else {
//                         // Ensure missing fields remain editable
//                         frappe.web_form.set_df_property(fieldname, "read_only", 0);
//                     }
//                 });
//             }
//         });
//     };

//     // Attach debounced input listener
//     $(personalField.$input).on("input", debounce(fetchUserData, 800));
// };
