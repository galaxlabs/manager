import frappe
from frappe.model.document import Document

def update_account_balance(account_name, debit=0, credit=0):
    """Update account balance respecting debit/credit normal balance convention.
    Asset/Expense types: normal debit balance (debit increases, credit decreases)
    Liability/Equity/Income types: normal credit balance (credit increases, debit decreases)
    """
    if not account_name:
        return
    ac = frappe.get_doc("Account", account_name)
    if ac.account_type in (
        "Asset", "Expense", "Bank", "Cash", "Receivable",
        "Fixed Asset", "Stock", "Depreciation", "Cost of Goods Sold"
    ):
        new_balance = (ac.balance or 0) + (debit or 0) - (credit or 0)
    else:
        new_balance = (ac.balance or 0) + (credit or 0) - (debit or 0)
    ac.db_set("balance", new_balance)

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
        self.post_double_entry()

    def on_cancel(self):
        if self.payee and self.amount:
            supplier = frappe.get_doc("Supplier", self.payee)
            supplier.db_set("accounts_payable", (supplier.accounts_payable or 0) + self.amount)
        self.status = "Cancelled"
        self.post_double_entry(reverse=True)

    def post_double_entry(self, reverse=False):
        settings = frappe.get_single("Manager Settings")
        ap_account = settings.get("default_ap_account")
        cash_account = settings.get("default_cash_account")
        amount = self.amount or 0
        if reverse:
            amount = -amount
        if amount > 0:
            if ap_account:
                update_account_balance(ap_account, debit=amount)
            if cash_account:
                update_account_balance(cash_account, credit=amount)
