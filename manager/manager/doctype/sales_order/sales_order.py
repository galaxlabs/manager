import frappe
from frappe.model.document import Document

class SalesOrder(Document):
    def before_save(self):
        self.calculate_amounts()
        self.set_status()

    def calculate_amounts(self):
        total = 0
        for item in self.get("items", []):
            item.amount = (item.quantity or 0) * (item.rate or 0)
            total += item.amount
        self.order_amount = total

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            self.status = "Submitted"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        self.qty_reserved = sum((item.quantity or 0) for item in self.get("items", []))
        self.invoice_status = "Pending"
        self.delivery_status = "Pending"

    def on_cancel(self):
        self.status = "Cancelled"
