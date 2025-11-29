# Copyright (c) 2025, elattar.systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ConsultationSessionBooking(Document):
    def validate(self):
        # Only auto-create/link customers for guest users submitting via web form
        # Skip this logic when creating bookings from desk (logged-in users)
        is_guest = frappe.session.user == "Guest"
        
        if is_guest and not self.client and self.client_name and self.client_email:
            self.set_client()

    def set_client(self):
        # 1. Check if a customer exists with this email
        existing_customer_name = frappe.db.get_value("Customer", 
            {"email_id": self.client_email}, "name")

        if existing_customer_name:
            # Link existing customer
            self.client = existing_customer_name
        else:
            # 2. Create a new customer
            new_customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": self.client_name,
                "customer_type": "Individual",
                "customer_group": "All Customer Groups", 
                "territory": "All Territories",
                "email_id": self.client_email,
                "mobile_no": self.client_phone
            })
            
            # Insert with ignore_permissions (Guests don't have permission to create Customers)
            new_customer.flags.ignore_permissions = True
            new_customer.insert()
            
            # 3. Link the new customer
            self.client = new_customer.name
