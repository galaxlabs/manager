import frappe
from frappe.model.document import Document

class Payment(Document):
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
        if self.payee and self.amount:
            supplier = frappe.get_doc("Supplier", self.payee)
            balance = (supplier.accounts_payable or 0) - self.amount
            supplier.db_set("accounts_payable", max(balance, 0))

    def on_cancel(self):
        self.status = "Cancelled"
