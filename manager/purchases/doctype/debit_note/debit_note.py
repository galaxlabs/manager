import frappe
from frappe.model.document import Document

class DebitNote(Document):
    def on_submit(self):
        if self.purchase_invoice:
            pi = frappe.get_doc("Purchase Invoice", self.purchase_invoice)
            if pi.balance_due and self.total_amount:
                from manager.api import update_account_balance
                settings = frappe.get_single("Manager Settings")
                ap = settings.get("default_ap_account")
                purchase = settings.get("default_purchase_account")
                amt = min(self.total_amount, pi.balance_due)
                if ap: update_account_balance(ap, debit=amt)
                if purchase: update_account_balance(purchase, credit=amt)
    
    def on_cancel(self):
        if self.purchase_invoice:
            pi = frappe.get_doc("Purchase Invoice", self.purchase_invoice)
            if pi.balance_due and self.total_amount:
                from manager.api import update_account_balance
                settings = frappe.get_single("Manager Settings")
                ap = settings.get("default_ap_account")
                purchase = settings.get("default_purchase_account")
                amt = min(self.total_amount, pi.balance_due)
                if ap: update_account_balance(ap, credit=amt)
                if purchase: update_account_balance(purchase, debit=amt)
