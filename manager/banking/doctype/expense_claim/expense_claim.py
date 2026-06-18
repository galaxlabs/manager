import frappe
from frappe.model.document import Document

class ExpenseClaim(Document):
    def on_submit(self):
        from manager.api import update_account_balance
        if self.expense_account and self.amount:
            update_account_balance(self.expense_account, debit=self.amount)
        # Credit clearing/employee payable account
        settings = frappe.get_single("Manager Settings")
        cash = settings.get("default_cash_account")
        if cash and self.amount:
            update_account_balance(cash, credit=self.amount)
    
    def on_cancel(self):
        from manager.api import update_account_balance
        if self.expense_account and self.amount:
            update_account_balance(self.expense_account, credit=self.amount)
        settings = frappe.get_single("Manager Settings")
        cash = settings.get("default_cash_account")
        if cash and self.amount:
            update_account_balance(cash, debit=self.amount)
