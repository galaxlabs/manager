import frappe
from frappe.model.document import Document
from manager.api import update_account_balance

class Payslip(Document):
    def on_submit(self):
        if self.net_pay:
            # Debit salary expense, credit salary payable
            expense_accts = frappe.get_all("Account", filters={"account_type": "Expense", "account_name": ["like", "%Salary%"]}, limit=1)
            expense = expense_accts[0].name if expense_accts else None
            liab_accts = frappe.get_all("Account", filters={"account_type": "Liability", "account_name": ["like", "%Salary%"]}, limit=1)
            liab = liab_accts[0].name if liab_accts else None
            if expense:
                update_account_balance(expense, debit=self.net_pay)
            if liab:
                update_account_balance(liab, credit=self.net_pay)
            elif not expense:
                settings = frappe.get_single("Manager Settings")
                cash = settings.get("default_cash_account")
                if cash:
                    update_account_balance(cash, credit=self.net_pay)
    
    def on_cancel(self):
        if self.net_pay:
            expense_accts = frappe.get_all("Account", filters={"account_type": "Expense", "account_name": ["like", "%Salary%"]}, limit=1)
            expense = expense_accts[0].name if expense_accts else None
            liab_accts = frappe.get_all("Account", filters={"account_type": "Liability", "account_name": ["like", "%Salary%"]}, limit=1)
            liab = liab_accts[0].name if liab_accts else None
            if expense:
                update_account_balance(expense, credit=self.net_pay)
            if liab:
                update_account_balance(liab, debit=self.net_pay)
            elif not expense:
                settings = frappe.get_single("Manager Settings")
                cash = settings.get("default_cash_account")
                if cash:
                    update_account_balance(cash, debit=self.net_pay)
