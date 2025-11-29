import frappe

def get_context(context):
    pass

def validate(doc):
    """
    Runs on Web Form submission. 
    1. Reads guest input from 'client_name', 'client_email', 'client_phone'.
    2. Finds or creates a Customer.
    3. Sets the mandatory 'client' link field to satisfy DocType validation.
    """

    # 1. Safety Check: If Client is already set (e.g. by internal staff), stop.
    if doc.client:
        return

    # 2. READ DATA: Access the specific fields defined in your JSON
    name_input = doc.client_name
    email_input = doc.client_email
    phone_input = doc.client_phone

    # 3. VALIDATE: Ensure we have enough info to make a customer
    if not name_input or not email_input:
        frappe.throw("Name and Email are required to book a consultation.")

    # 4. FIND CUSTOMER: Check if a customer exists with this email
    existing_customer_name = frappe.db.get_value("Customer", 
        {"email_id": email_input}, "name")

    if existing_customer_name:
        # Link existing customer
        doc.client = existing_customer_name
    else:
        # 5. CREATE CUSTOMER: If not found, create a new one
        new_customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": name_input,
            "customer_type": "Individual",
            "customer_group": "All Customer Groups", 
            "territory": "All Territories",
            "email_id": email_input,
            "mobile_no": phone_input
        })
        
        # Insert with ignore_permissions (Guests don't have permission to create Customers)
        new_customer.flags.ignore_permissions = True
        new_customer.insert()
        
        # 6. LINK: Set the hidden 'client' field to the new Customer's name
        doc.client = new_customer.name