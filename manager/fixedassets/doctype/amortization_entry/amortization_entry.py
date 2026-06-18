import frappe
from frappe.model.document import Document
from manager.api import update_account_balance

class AmortizationEntry(Document):
    def on_submit(self):
        if self.amount:
            if self.amortization_expense_account and self.accumulated_amortization_account:
                update_account_balance(self.amortization_expense_account, debit=self.amount)
                update_account_balance(self.accumulated_amortization_account, credit=self.amount)
    
    def on_cancel(self):
        if self.amount:
            if self.amortization_expense_account and self.accumulated_amortization_account:
                update_account_balance(self.amortization_expense_account, credit=self.amount)
                update_account_balance(self.accumulated_amortization_account, debit=self.amount)
