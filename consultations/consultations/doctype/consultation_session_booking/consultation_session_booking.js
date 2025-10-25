// Copyright (c) 2025, elattar.systems and contributors
// For license information, please see license.txt

frappe.ui.form.on("Consultation Session Booking", {
	refresh(frm) {
        // frm.remove_custom_button();
        if (frm.doc.docstatus === 0 && frm.doc.status === 'Pending Approval') {
            frm.add_custom_button(__('Approve Session'), function() {
                frm.set_value('status', 'Pending Payment'); // Optimistic update
                frappe.call({
                    method: 'consultations.consultations.doctype.consultation_session_booking.api.approve_and_create_invoice', // UPDATE THIS PATH
                    args: {
                        booking_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message && r.message.sales_invoice_name) {
                            
                            let invoice_name = r.message.sales_invoice_name;
                            let invoice_url = `/app/sales-invoice/${invoice_name}`;
                            let message = `Booking Approved. Draft Sales Invoice <a href="${invoice_url}"><b>${invoice_name}</b></a> created.`;
                            frappe.msgprint({
                                title: __('Success'),
                                indicator: 'green',
                                message: message
                            });

                            frm.reload_doc();
                        }
                    }
                });
            }).addClass('btn-primary');
        }
        if (frm.doc.docstatus === 0 && frm.doc.status === 'Pending Payment') {
            frm.add_custom_button(__('Check Payment Status'), function() {
                frappe.call({
                    method: 'consultations.consultations.doctype.consultation_session_booking.api.check_payment_and_confirm', // UPDATE THIS PATH
                    args: {
                        booking_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                            frm.reload_doc();
                        }
                    }
                });
            }).addClass('btn-primary');
        }


	},
});
