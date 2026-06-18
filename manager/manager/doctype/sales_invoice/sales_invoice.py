import frappe
from frappe.model.document import Document

class SalesInvoice(Document):
    def before_save(self):
        self.calculate_amounts()
        self.set_status()

    def calculate_amounts(self):
        total = 0
        for item in self.get("items", []):
            item.amount = (item.quantity or 0) * (item.rate or 0)
            total += item.amount
        self.invoice_amount = total
        self.balance_due = total

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            if self.balance_due and self.balance_due > 0:
                self.status = "Submitted"
            else:
                self.status = "Paid"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def on_submit(self):
        self.set_status()
        self.update_customer_balance()

    def on_cancel(self):
        self.status = "Cancelled"
        self.update_customer_balance(reverse=True)

    def update_customer_balance(self, reverse=False):
        if self.customer:
            customer = frappe.get_doc("Customer", self.customer)
            amount = self.invoice_amount or 0
            if reverse:
                amount = -amount
            customer.db_set("accounts_receivable", (customer.accounts_receivable or 0) + amount)
