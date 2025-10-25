# In your_ap_name/api.py
import frappe
from frappe.utils import nowdate


@frappe.whitelist()
def approve_and_create_invoice(booking_name):
	"""
	Called when the 'Approve' button is clicked.
	Sets status to 'Pending Payment' and creates a draft Sales Invoice.
	"""
	booking = frappe.get_doc("Consultation Session Booking", booking_name)

	# Prevent running if not in the correct state
	if booking.status != "Pending Approval":
		frappe.throw("This booking has already been approved.")
		return

	# Create the Sales Invoice
	si = frappe.new_doc("Sales Invoice")
	si.customer = booking.client
	si.due_date = nowdate()  # Or set based on your payment terms
	si.append(
		"items",
		{
			"item_code": booking.service,
			"qty": 1,
			# Rate and accounts should be fetched from the Item master
		},
	)
	# Set accounting dimensions
	# si.project = booking.project
	si.consultation_session_booking = booking.name
	si.save(ignore_permissions=True)  # Save as a draft

	# Update the booking
	booking.status = "Pending Payment"
	booking.sales_invoice = si.name
	booking.save(ignore_permissions=True)

	frappe.db.commit()
	return {"sales_invoice_name": si.name}


# Return the updated doc to the client script


@frappe.whitelist()
def check_payment_and_confirm(booking_name):
	"""
	Called when 'Check Payment' button is clicked.
	Checks the linked invoice; if paid, it confirms (submits) the booking.
	"""
	booking = frappe.get_doc("Consultation Session Booking", booking_name)
	invoice = frappe.get_last_doc("Sales Invoice", filters={"consultation_session_booking": booking_name})

	if not invoice:
		frappe.throw("No Sales Invoice is linked to this booking.")
		return

	invoice_status = invoice.status

	if invoice_status == "Paid":
		booking.status = "Confirmed"
		booking.submit()  # The final confirmation action!
		return "Payment verified. Booking has been confirmed."
	else:
		# We don't throw an error, just inform the user.
		return f"Payment not cleared yet. The invoice status is currently: '{invoice_status}'."
