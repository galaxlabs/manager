import frappe
from frappe.model.document import Document

class Receipt(Document):
    def before_save(self):
        self.set_status()

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            self.status = "Submitted"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        if self.paid_by and self.amount:
            customer = frappe.get_doc("Customer", self.paid_by)
            balance = (customer.accounts_receivable or 0) - self.amount
            customer.db_set("accounts_receivable", max(balance, 0))
