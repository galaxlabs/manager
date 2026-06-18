import frappe
from frappe.model.document import Document

class CreditNote(Document):
    def on_submit(self):
        if self.sales_invoice:
            # Reverse AR and Sales by crediting the original amounts
            si = frappe.get_doc("Sales Invoice", self.sales_invoice)
            if si.balance_due and self.total_amount:
                from manager.api import update_account_balance
                settings = frappe.get_single("Manager Settings")
                ar = settings.get("default_ar_account")
                sales = settings.get("default_sales_account")
                amt = min(self.total_amount, si.balance_due)
                if ar: update_account_balance(ar, credit=amt)
                if sales: update_account_balance(sales, debit=amt)
    
    def on_cancel(self):
        if self.sales_invoice:
            si = frappe.get_doc("Sales Invoice", self.sales_invoice)
            if si.balance_due and self.total_amount:
                from manager.api import update_account_balance
                settings = frappe.get_single("Manager Settings")
                ar = settings.get("default_ar_account")
                sales = settings.get("default_sales_account")
                amt = min(self.total_amount, si.balance_due)
                if ar: update_account_balance(ar, debit=amt)
                if sales: update_account_balance(sales, credit=amt)
