
import frappe
from frappe import _


# ── Permission Helpers ──────────────────────────────────────────

def get_current_manager_user():
    """Return the Manager User doc for the currently logged-in Frappe user."""
    frappe_user = frappe.session.user
    if not frappe_user or frappe_user == 'Guest':
        return None
    mus = frappe.get_all("Manager User",
        filters={"user_id": frappe_user},
        fields=["name", "full_name", "role", "is_active"],
        limit=1)
    if mus:
        return mus[0]
    # If no Manager User exists, treat as Administrator (for now)
    return {"name": None, "full_name": "Administrator", "role": "Administrator", "is_active": 1}

def get_user_role():
    mu = get_current_manager_user()
    return mu.get("role", "Administrator") if mu else "Administrator"

@frappe.whitelist()
def get_user_businesses():
    """Return all businesses the current user has access to.
    Administrator returns all businesses. Other roles return their assigned businesses."""
    frappe_user = frappe.session.user
    if not frappe_user or frappe_user == 'Guest':
        return []
    role = get_user_role()
    if role == "Administrator":
        return frappe.get_all("Business", filters={"is_active": 1}, fields=["name", "business_name", "currency"])
    mus = frappe.get_all("Manager User",
        filters={"user_id": frappe_user},
        fields=["name"],
        limit=1)
    if not mus:
        return []
    businesses = frappe.get_all("Manager User Business",
        filters={"parent": mus[0].name},
        fields=["business"])
    bs = [b.business for b in businesses if b.business]
    if not bs:
        return frappe.get_all("Business", filters={"is_active": 1}, fields=["name", "business_name", "currency"])
    return frappe.get_all("Business", filters={"name": ["in", bs], "is_active": 1}, fields=["name", "business_name", "currency"])

def _get_role_permissions(role):
    """Define what each role can do. Returns dict of doctype -> actions."""
    all_doctypes = ["Payment Term", "Payment Schedule", "Account", "Account Transfer", "Bank Reconciliation", "Expense Claim", "Payment", "Receipt",
        "Customer", "Sales Quote", "Sales Order", "Sales Invoice", "Credit Note", "Delivery Note",
        "Late Payment Fee", "Billable Time", "Withholding Tax Receipt",
        "Supplier", "Purchase Quote", "Purchase Order", "Purchase Invoice", "Debit Note", "Goods Receipt",
        "Item", "Inventory Transfer", "Inventory Write-off", "Production Order",
        "Employee", "Payslip", "Fixed Asset", "Depreciation Entry", "Intangible Asset",
        "Amortization Entry", "Investment",
        "Journal Entry", "Folder", "Recurring Transaction", "Budget", "Budget Account",
        "Division", "Currency", "Exchange Rate", "Manager Settings", "Tax Code", "Custom Field Def",
        "Project", "Manager User"]
    if role == "Administrator":
        return {dt: {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1} for dt in all_doctypes}
    sales = ["Customer", "Sales Quote", "Sales Order", "Sales Invoice", "Credit Note", "Delivery Note",
        "Late Payment Fee", "Billable Time", "Withholding Tax Receipt"]
    purchases = ["Supplier", "Purchase Quote", "Purchase Order", "Purchase Invoice", "Debit Note", "Goods Receipt"]
    banking = ["Account", "Account Transfer", "Bank Reconciliation", "Expense Claim", "Payment", "Receipt"]
    inventory = ["Item", "Inventory Transfer", "Inventory Write-off", "Production Order"]
    payroll = ["Employee", "Payslip"]
    fixed = ["Fixed Asset", "Depreciation Entry", "Intangible Asset", "Amortization Entry", "Investment"]
    accounting = ["Journal Entry", "Folder", "Recurring Transaction", "Budget", "Budget Account",
        "Division", "Currency", "Exchange Rate", "Payment Term", "Payment Schedule", "Project"]
    settings = ["Manager Settings", "Tax Code", "Custom Field Def", "Manager User"]
    
    rw = {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0}
    rws = {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0}
    ro = {"read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0}
    full_sales = {dt: {**rws} for dt in sales}
    full_purchases = {dt: {**rws} for dt in purchases}
    
    if role == "Manager":
        perms = {}
        for dt in all_doctypes:
            if dt in sales:
                perms[dt] = {**rws}
            elif dt in purchases:
                perms[dt] = {**rws}
            elif dt in banking:
                perms[dt] = {**rws}
            elif dt in (inventory + payroll + fixed + accounting + settings):
                perms[dt] = {**rw}
            else:
                perms[dt] = {**ro}
        return perms
    elif role == "Accountant":
        perms = {}
        for dt in banking + accounting + ["Sales Invoice", "Purchase Invoice"]:
            perms[dt] = {**rws}
        for dt in all_doctypes:
            if dt not in perms and dt not in settings:
                perms[dt] = {**ro}
        perms["Report"] = {"read": 1}
        return perms
    elif role == "Sales":
        perms = {}
        for dt in sales:
            perms[dt] = {**rws}
        for dt in all_doctypes:
            if dt not in perms:
                perms[dt] = {**ro}
        return perms
    elif role == "Purchases":
        perms = {}
        for dt in purchases:
            perms[dt] = {**rws}
        for dt in all_doctypes:
            if dt not in perms:
                perms[dt] = {**ro}
        return perms
    else:  # View Only
        return {dt: {**ro} for dt in all_doctypes}

def _check_permission(doctype, action="read"):
    """Check if current user has permission for action on doctype. Raises if not."""
    role = get_user_role()
    perms = _get_role_permissions(role)
    p = perms.get(doctype, {"read": 0, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0})
    if not p.get(action, 0):
        frappe.throw(f"{role} does not have {action} permission on {doctype}.", frappe.PermissionError)

def _apply_business_filter(doctype=None):
    """Return a business filter dict based on user role/businesses."""
    businesses = get_user_businesses()
    if not businesses:
        return {}  # All businesses
    return {"business": ["in", businesses]}


def update_account_balance(account_name, debit=0, credit=0):
    if not account_name:
        return
    ac = frappe.get_doc("Account", account_name)
    if ac.account_type in ("Asset", "Expense", "Bank", "Cash", "Receivable", "Fixed Asset", "Stock", "Depreciation", "Cost of Goods Sold"):
        new_bal = (ac.balance or 0) + (debit or 0) - (credit or 0)
    else:
        new_bal = (ac.balance or 0) + (credit or 0) - (debit or 0)
    ac.db_set("balance", new_bal)

@frappe.whitelist()
def trial_balance():
    """Return all accounts with their current balance, type, and group info."""
    accounts = frappe.get_all("Account",
        fields=["name", "account_name", "account_type", "parent_account", "is_group", "balance"],
        order_by="name")
    return accounts

@frappe.whitelist()
def profit_and_loss(from_date=None, to_date=None):
    """Return income and expense accounts for P&L.
    Reads Account.balance which is updated by double-entry posting."""
    import frappe.utils
    accounts = frappe.get_all("Account",
        fields=["name", "account_name", "account_type", "parent_account", "balance"],
        filters=[
            ["account_type", "in", ["Income", "Expense", "Cost of Goods Sold", "Depreciation"]],
            ["is_group", "=", 0]
        ],
        order_by="name")
    total_income = 0
    total_expense = 0
    for a in accounts:
        bal = a.balance or 0
        if a.account_type in ("Income",):
            total_income += bal
        else:
            total_expense += bal
    net_profit = total_income - total_expense
    return {
        "accounts": accounts,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_profit": net_profit,
    }

@frappe.whitelist()
def balance_sheet():
    """Return Balance Sheet data from Account balances."""
    accounts = frappe.get_all("Account",
        fields=["name", "account_name", "account_type", "parent_account", "is_group", "balance"],
        order_by="name")
    total_assets = 0
    total_liabilities = 0
    total_equity = 0
    for a in accounts:
        if a.is_group:
            continue
        bal = a.balance or 0
        if a.account_type in ("Asset", "Bank", "Cash", "Receivable", "Fixed Asset", "Stock", "Accumulated Depreciation"):
            total_assets += bal
        elif a.account_type in ("Liability", "Payable"):
            total_liabilities += bal
        elif a.account_type in ("Equity",):
            total_equity += bal
    return {
        "accounts": accounts,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
    }



@frappe.whitelist()
def get_settings():
    return frappe.get_single("Manager Settings").as_dict()

@frappe.whitelist()
def save_settings(**kwargs):
    import json
    doc = frappe.get_single("Manager Settings")
    meta = frappe.get_meta("Manager Settings")
    valid = {f.fieldname for f in meta.fields if f.fieldtype not in ("Section Break", "Column Break", "Tab Break")}
    filtered = {k: v for k, v in kwargs.items() if k in valid}

    # Process extension toggles
    ext_results = []
    if "extensions" in filtered:
        from . import extension_registry
        new_ext = json.loads(filtered["extensions"]) if isinstance(filtered["extensions"], str) else (filtered["extensions"] or {})
        old_ext_raw = doc.get("extensions", "{}")
        old_ext = json.loads(old_ext_raw) if isinstance(old_ext_raw, str) else (old_ext_raw or {})
        for key, val in new_ext.items():
            is_active = val.get("is_active") if isinstance(val, dict) else bool(val)
            was_active = old_ext.get(key, {}).get("is_active") if isinstance(old_ext.get(key, {}), dict) else bool(old_ext.get(key, False))
            if is_active and not was_active:
                tax_codes = val.get("tax_codes", []) if isinstance(val, dict) else None
                r = extension_registry.process_extension_toggle(key, True, tax_codes)
                ext_results.append(r)

    doc.update(filtered)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok", "settings": doc.as_dict(), "extension_results": ext_results}

@frappe.whitelist()
def import_chart_of_accounts():
    _check_permission("Manager Settings", "write")
    doc = frappe.get_single("Manager Settings")
    if doc.chart_of_accounts_imported:
        return {"status": "already_imported"}

    scraped_coa = [
        {"name": "Assets", "parent": "", "account_type": "Asset", "is_group": True},
        {"name": "Accounts Receivable", "parent": "Assets", "account_type": "Asset"},
        {"name": "Advance Salary Receivable", "parent": "Assets", "account_type": "Asset"},
        {"name": "Billable Expenses", "parent": "Assets", "account_type": "Asset"},
        {"name": "Cash", "parent": "Assets", "account_type": "Bank"},
        {"name": "Fixed Assets, At Cost", "parent": "Assets", "account_type": "Asset"},
        {"name": "Fixed Assets, Accumulated Depreciation", "parent": "Assets", "account_type": "Asset"},
        {"name": "Inventory On Hand", "parent": "Assets", "account_type": "Asset"},
        {"name": "Negative Inventory Clearing", "parent": "Assets", "account_type": "Asset"},
        {"name": "Liabilities", "parent": "", "account_type": "Liability", "is_group": True},
        {"name": "Accounts Payable", "parent": "Liabilities", "account_type": "Liability"},
        {"name": "Employee Clearing Account", "parent": "Liabilities", "account_type": "Liability"},
        {"name": "Interdivisional Loan", "parent": "Liabilities", "account_type": "Liability"},
        {"name": "Provident Fund Payable", "parent": "Liabilities", "account_type": "Liability"},
        {"name": "Tax Payable", "parent": "Liabilities", "account_type": "Liability"},
        {"name": "Equity", "parent": "", "account_type": "Equity", "is_group": True},
        {"name": "Capital", "parent": "Equity", "account_type": "Equity"},
        {"name": "Capital Accounts", "parent": "Equity", "account_type": "Equity"},
        {"name": "Inter Account Transfers", "parent": "Equity", "account_type": "Equity"},
        {"name": "Retained Earnings", "parent": "Equity", "account_type": "Equity"},
        {"name": "Income", "parent": "", "account_type": "Income", "is_group": True},
        {"name": "Billable Expenses - Invoiced", "parent": "Income", "account_type": "Income"},
        {"name": "Interest Received", "parent": "Income", "account_type": "Income"},
        {"name": "Inventory - Sales", "parent": "Income", "account_type": "Income"},
        {"name": "Sales", "parent": "Income", "account_type": "Income"},
        {"name": "Less: Expenses", "parent": "", "account_type": "Expense", "is_group": True},
        {"name": "Accounting Fees", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Advertising and Promotion", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Bank Charges", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Billable Expenses - Cost", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Cartage", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Commission Charges", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Computer Equipment", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Conveyance Exp", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Donations", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Electricity", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Entertainment", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Fabrication Work", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Fixed Assets - Depreciation", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Furniture and Fixture", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Inventory - Cost", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Legal Fees", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Motor Vehicle Expenses", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Plant Exp", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Plumber Fitting", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Printing and Stationery", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Refreshment Exp", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Renovation Exp", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Rent", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Repairs and Maintenance", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Salary Exp", "parent": "Less: Expenses", "account_type": "Expense"},
        {"name": "Salary Exp Advance", "parent": "Less: Expenses", "account_type": "Expense"},
    ]

    created = []
    for acc in scraped_coa:
        try:
            a = frappe.get_doc({
                "doctype": "Account",
                "account_name": acc["name"],
                "parent_account": acc.get("parent") or None,
                "account_type": acc.get("account_type", "Asset"),
                "is_group": acc.get("is_group", False),
            })
            a.insert()
            created.append(acc["name"])
        except Exception as e:
            frappe.log_error(f"Failed to create account {acc['name']}: {e}")

    doc.chart_of_accounts_imported = 1
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok", "created": created, "count": len(created)}

@frappe.whitelist()
def get_meta(doctype):
    """Return doctype field definitions for dynamic form generation"""
    meta = frappe.get_meta(doctype)
    fields = []
    for f in meta.fields:
        if f.fieldname in ("name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "amended_from", "status", "naming_series", "reference"):
            continue
        fields.append({
            "fieldname": f.fieldname,
            "label": f.label or f.fieldname,
            "fieldtype": f.fieldtype,
            "options": f.options,
            "reqd": f.reqd,
            "description": f.description,
        })
    # Include custom field definitions
    try:
        cfs = frappe.get_all("Custom Field Def",
            filters={"target_doctype": doctype, "is_active": 1},
            fields=["field_label", "field_name", "field_type", "options"],
            order_by="sort_order asc, field_label asc")
        for cf in cfs:
            fields.append({
                "fieldname": cf.field_name,
                "label": cf.field_label,
                "fieldtype": cf.field_type,
                "options": cf.options,
                "reqd": 0,
                "is_custom": 1,
            })
    except:
        pass
    return {"fields": fields, "doctype": doctype, "is_submittable": meta.is_submittable}

@frappe.whitelist()
def create_doc(doctype, **kwargs):
    _check_permission(doctype, "create")
    doc = frappe.get_doc({"doctype": doctype, **kwargs})
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

@frappe.whitelist()
def update_doc(doctype, name, **kwargs):
    _check_permission(doctype, "write")
    doc = frappe.get_doc(doctype, name)
    doc.update(kwargs)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

@frappe.whitelist()
def get_doc(doctype, name):
    _check_permission(doctype, "read")
    doc = frappe.get_doc(doctype, name)
    return doc.as_dict()


@frappe.whitelist()
def submit_doc(doctype, name):
    _check_permission(doctype, "submit")
    doc = frappe.get_doc(doctype, name)
    doc.submit()
    frappe.db.commit()
    return {"name": doc.name, "status": "submitted", "data": doc.as_dict()}

@frappe.whitelist()
def cancel_doc(doctype, name):
    _check_permission(doctype, "cancel")
    doc = frappe.get_doc(doctype, name)
    doc.cancel()
    frappe.db.commit()
    return {"name": doc.name, "status": "cancelled", "data": doc.as_dict()}

@frappe.whitelist()
def get_child_meta(doctype):
    """Return fields for a child table doctype"""
    meta = frappe.get_meta(doctype)
    fields = []
    for f in meta.fields:
        if f.fieldname in ("name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "parent", "parentfield", "parenttype"):
            continue
        fields.append({
            "fieldname": f.fieldname,
            "label": f.label or f.fieldname,
            "fieldtype": f.fieldtype,
            "options": f.options,
            "reqd": f.reqd,
        })
    return {"fields": fields, "doctype": doctype}

@frappe.whitelist()
def get_extensions():
    """Return available extensions with metadata"""
    from . import extension_registry
    return extension_registry.get_available_extensions()

@frappe.whitelist()
def process_extension_toggle(ext_key, enable=True, tax_codes=None):
    """Toggle an extension on/off"""
    from . import extension_registry
    import json
    tc_list = json.loads(tax_codes) if isinstance(tax_codes, str) else (tax_codes or [])
    return extension_registry.process_extension_toggle(ext_key, enable, tc_list)

@frappe.whitelist()
def get_list_filtered(doctype, fields='["*"]', filters=None, limit=100, limit_start=0, search=None):
    import json
    _check_permission(doctype, "read")
    if isinstance(fields, str):
        fields = json.loads(fields)
    if isinstance(filters, str):
        filters = json.loads(filters) if filters else {}
    if not filters:
        filters = {}
    
    # Apply business filter based on Manager User role
    role = get_user_role()
    if role != "Administrator":
        businesses = get_user_businesses()
        if businesses:
            biz_names = [b.get("name") if isinstance(b, dict) else b for b in businesses]
            filters["business"] = ["in", biz_names]
    
    # Search filter: search across text fields
    if search:
        meta = frappe.get_meta(doctype)
        text_fields = [f.fieldname for f in meta.fields if f.fieldtype in ("Data", "Small Text", "Text", "Long Text")]
        if text_fields:
            or_filters = [[doctype, f, "like", f"%{search}%"] for f in text_fields[:5]]
        else:
            or_filters = []
    else:
        or_filters = None
    
    total = frappe.db.count(doctype, filters=filters)
    data = frappe.get_list(doctype, fields=fields, filters=filters, or_filters=or_filters, limit=limit, limit_start=limit_start)
    return {"data": data, "total": total, "limit": limit, "limit_start": limit_start}

@frappe.whitelist()
def get_user_business():
    user = frappe.session.user
    if user == "Administrator":
        biz = frappe.get_all("Business", filters={"is_active": 1}, limit=1, fields=["name", "business_name", "currency", "tax_id"])
        return biz[0] if biz else None
    sql = "SELECT b.name, b.business_name, b.currency, b.tax_id "
    sql += "FROM tabBusiness b "
    sql += "JOIN `tabBusiness User` bu ON bu.parent = b.name "
    sql += "WHERE bu.user = %s AND bu.is_active = 1 AND b.is_active = 1 "
    sql += "LIMIT 1"
    biz = frappe.db.sql(sql, user, as_dict=True)
    return biz[0] if biz else None

@frappe.whitelist()
def get_user_info():
    user = frappe.session.user
    business = get_user_business()
    return {"user": user, "business": business, "is_admin": user == "Administrator"}

@frappe.whitelist(allow_guest=True)
def login_with_api_key(usr, pwd):
    from frappe.auth import LoginManager
    try:
        lm = LoginManager()
        lm.authenticate(usr, pwd)
        lm.post_login()
    except:
        frappe.throw("Invalid credentials", frappe.AuthenticationError)
    user = frappe.get_doc("User", frappe.session.user)
    has_keys = bool(user.get("api_key"))
    if not has_keys:
        key = frappe.generate_hash(length=15)
        secret = frappe.generate_hash(length=15)
        user.api_key = key
        user.api_secret = secret
        user.save(ignore_permissions=True)
    else:
        key = user.api_key
        secret = None
    return {
        "api_key": key,
        "api_secret": secret,
        "has_keys": has_keys,
        "user": frappe.session.user,
        "business": get_user_business(),
    }

@frappe.whitelist()
def recalculate_balances():
    frappe.db.sql("UPDATE tabAccount SET balance = 0")
    def post(account, debit=0, credit=0):
        if not account:
            return
        ac = frappe.get_doc("Account", account)
        if ac.account_type in ("Asset", "Expense", "Bank", "Cash", "Receivable", "Fixed Asset", "Stock", "Depreciation", "Cost of Goods Sold"):
            new_bal = (ac.balance or 0) + (debit or 0) - (credit or 0)
        else:
            new_bal = (ac.balance or 0) + (credit or 0) - (debit or 0)
        ac.db_set("balance", new_bal)
    settings = frappe.get_single("Manager Settings")
    ar = settings.get("default_ar_account")
    ap = settings.get("default_ap_account")
    sales = settings.get("default_sales_account")
    purchase = settings.get("default_purchase_account")
    cash = settings.get("default_cash_account")
    if not ar:
        accts = frappe.get_all("Account", filters={"account_type": "Receivable"}, limit=1, pluck="name")
        if accts: ar = accts[0]
    if not ap:
        accts = frappe.get_all("Account", filters={"account_type": "Payable"}, limit=1, pluck="name")
        if accts: ap = accts[0]
    if not sales:
        accts = frappe.get_all("Account", filters={"account_type": "Income"}, limit=1, pluck="name")
        if accts: sales = accts[0]
    if not purchase:
        accts = frappe.get_all("Account", filters={"account_type": "Expense"}, limit=1, pluck="name")
        if accts: purchase = accts[0]
    if not cash:
        accts = frappe.get_all("Account", filters={"account_type": "Bank"}, limit=1, pluck="name")
        if accts: cash = accts[0]
    for je in frappe.get_all("Journal Entry", filters={}):
        doc = frappe.get_doc("Journal Entry", je.name)
        for row in doc.accounts:
            post(row.account, row.debit, row.credit)
    for si in frappe.get_all("Sales Invoice", filters={}):
        doc = frappe.get_doc("Sales Invoice", si.name)
        amt = doc.invoice_amount or 0
        if ar: post(ar, debit=amt)
        if sales: post(sales, credit=amt)
    for pi in frappe.get_all("Purchase Invoice", filters={}):
        doc = frappe.get_doc("Purchase Invoice", pi.name)
        amt = doc.invoice_amount or 0
        if ap: post(ap, credit=amt)
        if purchase: post(purchase, debit=amt)
    for rcp in frappe.get_all("Receipt", filters={}):
        doc = frappe.get_doc("Receipt", rcp.name)
        amt = doc.amount or 0
        if cash: post(cash, debit=amt)
        if ar: post(ar, credit=amt)
    for pmt in frappe.get_all("Payment", filters={}):
        doc = frappe.get_doc("Payment", pmt.name)
        amt = doc.amount or 0
        if cash: post(cash, credit=amt)
        if ap: post(ap, debit=amt)
    frappe.db.commit()
    return {"status": "ok", "message": "Balances recalculated"}

@frappe.whitelist()
def check_lock_date(date_str):
    from frappe.utils import getdate
    settings = frappe.get_single("Manager Settings")
    lock = settings.get("lock_date")
    if lock and date_str:
        if getdate(date_str) <= getdate(lock):
            frappe.throw("Cannot modify records on or before " + str(lock) + ". This period is locked.")
    return {"status": "ok"}

@frappe.whitelist()
def recalculate_stock_valuation():
    """Recompute average cost for all items from Goods Receipts and Purchase Invoices"""
    items = frappe.get_all("Item")
    for item_name in items:
        item = frappe.get_doc("Item", item_name.name)
        total_qty = 0
        total_cost = 0
        # Scan Goods Receipts for this item
        gr_list = frappe.get_all("Goods Receipt", filters={})
        for gr_name in gr_list:
            gr = frappe.get_doc("Goods Receipt", gr_name.name)
            if not gr.items: continue
            for row in gr.items:
                if row.item == item_name.name:
                    qty = row.quantity or 0
                    rate = row.rate or 0
                    total_qty += qty
                    total_cost += qty * rate
        # Scan Purchase Invoices
        pi_list = frappe.get_all("Purchase Invoice", filters={})
        for pi_name in pi_list:
            pi = frappe.get_doc("Purchase Invoice", pi_name.name)
            if not pi.items: continue
            for row in pi.items:
                if row.item == item_name.name:
                    qty = row.quantity or 0
                    rate = row.rate or 0
                    total_qty += qty
                    total_cost += qty * rate
        if total_qty > 0:
            avg_cost = total_cost / total_qty
            item.db_set("valuation_rate", avg_cost)
            item.db_set("stock_value", total_cost)
    frappe.db.commit()
    return {"status": "ok", "message": "Stock valuation recalculated"}

@frappe.whitelist()
def generate_depreciation_schedule(fixed_asset):
    """Generate depreciation entries for a fixed asset (straight-line)"""
    fa = frappe.get_doc("Fixed Asset", fixed_asset)
    cost = fa.acquisition_cost or 0
    current_dep = fa.depreciation or 0
    book_value = fa.book_value or cost
    # Find accumulated depreciation and expense accounts
    acc_dep = frappe.db.get_value("Account", {"account_name": ["like", "%Accumulated Depreciation%"]}, "name")
    dep_exp = frappe.db.get_value("Account", {"account_name": ["like", "%Depreciation%"], "account_type": "Expense"}, "name")
    if not acc_dep or not dep_exp:
        frappe.throw("Please create Accumulated Depreciation and Depreciation Expense accounts first")
    # Straight-line: assume 5 year life, monthly entries
    useful_life_months = 60
    monthly_dep = cost / useful_life_months if useful_life_months > 0 else 0
    if monthly_dep <= 0:
        return {"status": "error", "message": "Asset cost is zero, cannot depreciate"}
    created = 0
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    base_date = datetime.now().replace(day=1)
    for i in range(12):
        entry_date = base_date + relativedelta(months=i)
        title = f"DEP-{fa.name}-{entry_date.strftime('%Y-%m')}"
        if frappe.db.exists("Depreciation Entry", title):
            continue
        doc = frappe.get_doc({
            "doctype": "Depreciation Entry",
            "title": title,
            "fixed_asset": fa.name,
            "date": entry_date.strftime("%Y-%m-%d"),
            "amount": monthly_dep,
            "depreciation_expense_account": dep_exp,
            "accumulated_depreciation_account": acc_dep,
        })
        doc.insert(ignore_permissions=True)
        doc.submit()
        created += 1
    return {"status": "ok", "entries_created": created}

@frappe.whitelist()
def generate_payslip(employee, start_date, end_date):
    """Generate a payslip from an employee's salary structure"""
    emp = frappe.get_doc("Employee", employee)
    basic = emp.basic_salary or 0
    allowances = {}
    try:
        if emp.allowances:
            allowances = json.loads(emp.allowances) if isinstance(emp.allowances, str) else (emp.allowances or {})
    except:
        allowances = {}
    deductions = {}
    try:
        if emp.deductions_json:
            deductions = json.loads(emp.deductions_json) if isinstance(emp.deductions_json, str) else (emp.deductions_json or {})
    except:
        deductions = {}
    total_allowances = sum(float(v) for v in allowances.values()) if allowances else 0
    total_deductions = sum(float(v) for v in deductions.values()) if deductions else 0
    gross = basic + total_allowances
    net = gross - total_deductions
    title = f"PS-{emp.name}-{start_date[:7]}"
    if frappe.db.exists("Payslip", title):
        return {"status": "exists", "name": title}
    doc = frappe.get_doc({
        "doctype": "Payslip",
        "title": title,
        "employee": emp.name,
        "date": end_date,
        "start_date": start_date,
        "end_date": end_date,
        "gross_pay": gross,
        "deductions": total_deductions,
        "net_pay": net,
    })
    doc.insert(ignore_permissions=True)
    return {"status": "ok", "name": title, "gross": gross, "net": net}

@frappe.whitelist()
def calculate_invoice_taxes(doctype, name):
    """Calculate and post taxes for an invoice based on item tax codes"""
    doc = frappe.get_doc(doctype, name)
    if not hasattr(doc, "items") or not doc.items:
        return {"status": "ok", "tax_total": 0}
    total_tax = 0
    for row in doc.items:
        if row.tax_code:
            tc = frappe.get_doc("Tax Code", row.tax_code)
            rate = tc.rate or 0
            taxable = row.amount or 0
            tax = round(taxable * rate / 100, 2)
            row.tax_amount = tax
            row.total_amount_with_tax = taxable + tax
            total_tax += tax
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    # Post tax to account if tax account is configured
    if total_tax > 0:
        # Find the first tax code's account or a generic tax payable
        tax_acct = None
        for row in doc.items:
            if row.tax_code:
                tc = frappe.get_doc("Tax Code", row.tax_code)
                if tc.account:
                    tax_acct = tc.account
                    break
        if not tax_acct:
            tax_acct = frappe.db.get_value("Account", {"account_name": ["like", "%Tax Payable%"]}, "name")
        if tax_acct:
            if doctype == "Sales Invoice":
                update_account_balance(tax_acct, credit=total_tax)
            else:
                update_account_balance(tax_acct, debit=total_tax)
    return {"status": "ok", "tax_total": total_tax}



@frappe.whitelist()
def get_doc_versions(doctype, name):
    """Return version history for a document"""
    versions = frappe.get_all("Version",
        filters={"ref_doctype": doctype, "docname": name},
        fields=["name", "data", "modified", "owner", "creation"],
        order_by="creation desc",
        limit=50
    )
    result = []
    for v in versions:
        changes = []
        if v.data:
            try:
                import json
                data = json.loads(v.data)
                changed = data.get("changed", {})
                for field, old, new in changed:
                    changes.append({"field": field, "from": old, "to": new})
            except:
                pass
        result.append({
            "modified": v.modified,
            "owner": v.owner,
            "changes": changes[:5],
        })
    return result

@frappe.whitelist()
def send_document_email(doctype, name, to_email, subject=None, message=None):
    """Send a document as email with PDF attachment"""
    doc = frappe.get_doc(doctype, name)
    subject = subject or f"{doctype} {name}"
    message = message or f"Please find attached {doctype} {name}"
    # Generate PDF
    from frappe.utils.print_format import download_pdf
    try:
        pdf_data = frappe.get_print(doctype, name, as_pdf=True)
        frappe.sendmail(
            recipients=to_email,
            subject=subject,
            message=message,
            attachments=[{"fname": f"{name}.pdf", "fcontent": pdf_data}],
            reference_doctype=doctype,
            reference_name=name,
        )
        return {"status": "ok", "message": f"Email sent to {to_email}"}
    except Exception as e:
        frappe.throw(str(e))

@frappe.whitelist()
def upload_attachment(doctype, name):
    """Upload and attach a file to a document (POST multipart with file field)"""
    import json
    if "file" in frappe.request.files:
        file = frappe.request.files["file"]
        content = file.read()
        f = frappe.get_doc({
            "doctype": "File",
            "file_name": file.filename or "unnamed",
            "content": content,
            "attached_to_doctype": doctype,
            "attached_to_name": name,
        })
        f.insert(ignore_permissions=True)
        return {"status": "ok", "file": f.name, "file_name": f.file_name}
    frappe.throw("No file provided")

@frappe.whitelist()
def get_attachments(doctype, name):
    """Return file attachments for a document"""
    files = frappe.get_all("File",
        filters={"attached_to_doctype": doctype, "attached_to_name": name},
        fields=["name", "file_name", "file_url", "file_size", "creation"]
    )
    return files

@frappe.whitelist()
@frappe.whitelist()
def get_dashboard_data():
    """Return all dashboard metrics, charts, and summaries"""
    settings = frappe.get_single("Manager Settings")
    base_currency = settings.get("currency") or "USD"
    from datetime import datetime
    
    def get_balance_by_type(atype):
        accts = frappe.get_all("Account", filters={"account_type": atype}, fields=["balance"])
        return sum((a.balance or 0) for a in accts)
    
    total_assets = get_balance_by_type("Asset") + get_balance_by_type("Bank") + get_balance_by_type("Cash") + get_balance_by_type("Receivable") + get_balance_by_type("Stock")
    total_liabilities = get_balance_by_type("Liability") + get_balance_by_type("Payable")
    total_equity = get_balance_by_type("Equity")
    total_income = get_balance_by_type("Income")
    total_expenses = get_balance_by_type("Expense") + get_balance_by_type("Cost of Goods Sold")
    net_profit = total_income - total_expenses
    
    entity_counts = {}
    for dt in ["Customer", "Supplier", "Item", "Employee", "Fixed Asset",
               "Sales Invoice", "Purchase Invoice", "Receipt", "Payment",
               "Sales Order", "Purchase Order", "Delivery Note",
               "Journal Entry", "Production Order", "Payslip"]:
        try: entity_counts[dt] = frappe.db.count(dt)
        except: entity_counts[dt] = 0
    
    monthly_data = []
    now = frappe.utils.now_datetime()
    for i in range(11, -1, -1):
        m = now.month - i
        y = now.year
        if m <= 0: m += 12; y -= 1
        month_label = datetime(y, m, 1).strftime("%b %y")
        monthly_data.append({"month": month_label, "income": 0, "expense": 0})
    
    for si in frappe.get_all("Sales Invoice", fields=["issue_date", "invoice_amount"]):
        if si.issue_date and si.invoice_amount:
            try:
                d = frappe.utils.getdate(si.issue_date)
                key = d.strftime("%b %y")
                for item in monthly_data:
                    if item["month"] == key: item["income"] += si.invoice_amount
            except: pass
    
    for pi in frappe.get_all("Purchase Invoice", fields=["issue_date", "invoice_amount"]):
        if pi.issue_date and pi.invoice_amount:
            try:
                d = frappe.utils.getdate(pi.issue_date)
                key = d.strftime("%b %y")
                for item in monthly_data:
                    if item["month"] == key: item["expense"] += pi.invoice_amount
            except: pass
    
    recent = []
    for dt in ["Sales Invoice", "Receipt", "Payment", "Purchase Invoice"]:
        docs = frappe.get_all(dt, fields=["name", "creation", "owner"], limit=5, order_by="creation desc")
        for d in docs:
            recent.append({"doctype": dt, "name": d.name, "date": str(d.creation or ""), "user": d.owner})
    recent.sort(key=lambda x: x["date"], reverse=True)
    recent = recent[:10]
    
    ar_total = 0
    ar_overdue = 0
    for si in frappe.get_all("Sales Invoice", fields=["balance_due", "status"]):
        if si.balance_due:
            ar_total += si.balance_due
            if si.status in ("Overdue", "DueTomorrow"):
                ar_overdue += si.balance_due
    
    customer_revenue = {}
    for si in frappe.get_all("Sales Invoice", fields=["customer", "invoice_amount"]):
        if si.customer and si.invoice_amount:
            customer_revenue[si.customer] = customer_revenue.get(si.customer, 0) + si.invoice_amount
    top_customers = sorted(customer_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
    
    ap_total_val = 0
    for pi in frappe.get_all("Purchase Invoice", fields=["balance_due"]):
        if pi.balance_due:
            ap_total_val += pi.balance_due
    
    return {
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "entity_counts": entity_counts,
        "monthly_data": monthly_data,
        "recent_transactions": recent,
        "ar_total": ar_total,
        "ar_overdue": ar_overdue,
        "ap_total": ap_total_val,
        "top_customers": [{"customer": c, "revenue": r} for c, r in top_customers],
        "currency": base_currency,
    }


@frappe.whitelist()
def aging_report(doctype="Sales Invoice"):
    """AR/AP aging report with 30/60/90/90+ buckets"""
    from frappe.utils import getdate
    from datetime import datetime, timedelta
    today = datetime.now()
    buckets = {"0-30": 0, "31-60": 0, "61-90": 0, "90+": 0, "total": 0}
    details = []
    filters = {"docstatus": ["!=", 2]}
    if doctype == "Sales Invoice":
        filters["balance_due"] = [">", 0]
    else:
        filters["balance_due"] = [">", 0]
    docs = frappe.get_all(doctype, fields=["name", "customer" if doctype=="Sales Invoice" else "supplier", "issue_date", "invoice_amount", "balance_due", "status"], filters=filters)
    for d in docs:
        date = d.issue_date or d.creation
        if not date: continue
        diff = (today - getdate(str(date)).date()).days if hasattr(getdate(str(date)), "date") else 0
        bal = d.balance_due or 0
        bucket = "0-30" if diff <= 30 else ("31-60" if diff <= 60 else ("61-90" if diff <= 90 else "90+"))
        buckets[bucket] += bal
        buckets["total"] += bal
        details.append({"name": d.name, "party": d.get("customer") or d.get("supplier"), "date": str(date), "amount": d.invoice_amount, "balance": bal, "bucket": bucket, "status": d.status})
    return {"buckets": buckets, "details": details}

@frappe.whitelist()
def cash_flow(from_date=None, to_date=None):
    """Cash flow statement: operating, investing, financing"""
    import frappe.utils
    from datetime import datetime
    if not from_date:
        from_date = datetime.now().replace(month=1, day=1).strftime("%Y-%m-%d")
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    def total_for_account(atype, debit=True):
        accts = frappe.get_all("Account", filters={"account_type": atype}, pluck="name")
        total = 0
        for acct in accts:
            a = frappe.get_doc("Account", acct)
            total += a.balance or 0
        return total
    net_income = total_for_account("Income") - total_for_account("Expense") - total_for_account("Cost of Goods Sold")
    ar_change = total_for_account("Receivable") - total_for_account("Payable")
    operating = net_income + ar_change
    fa = total_for_account("Fixed Asset")
    investing = -fa if fa else 0
    bank = total_for_account("Bank") + total_for_account("Cash")
    equity = total_for_account("Equity")
    financing = equity
    net_change = operating + investing + financing
    return {
        "operating": {"net_income": net_income, "ar_ap_change": ar_change, "total": operating},
        "investing": {"fixed_assets": -fa, "total": investing},
        "financing": {"equity": equity, "total": financing},
        "net_change": net_change,
        "opening_cash": 0,
        "closing_cash": bank,
    }

@frappe.whitelist()
def get_recurring_transactions():
    return frappe.get_all("Recurring Transaction", fields=["*"])

@frappe.whitelist()
def get_custom_fields(doctype):
    fields = frappe.get_all("Custom Field Def",
        filters={"target_doctype": doctype, "is_active": 1},
        fields=["name", "field_label", "field_name", "field_type", "options", "sort_order"],
        order_by="sort_order asc, field_label asc")
    return fields

@frappe.whitelist()
def save_custom_field_values(doctype, name, custom_fields):
    import json
    if isinstance(custom_fields, str):
        custom_fields = json.loads(custom_fields)
    doc = frappe.get_doc(doctype, name)
    doc.custom_fields_json = json.dumps(custom_fields)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def convert_sales_order_to_invoice(sales_order):
    so = frappe.get_doc("Sales Order", sales_order)
    if so.docstatus != 1:
        frappe.throw("Sales Order must be submitted first")
    settings = frappe.get_single("Manager Settings")
    ar_acct = settings.default_ar_account or frappe.db.get_value("Account", {"account_type": "Receivable"}, "name")
    sales_acct = settings.default_sales_account or frappe.db.get_value("Account", {"account_type": "Income"}, "name")
    invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": so.customer,
        "issue_date": frappe.utils.today(),
        "invoice_amount": so.total_amount or 0,
        "balance_due": so.total_amount or 0,
        "status": "Unpaid",
        "sales_order": so.name,
        "division": so.division,
        "business": so.business,
    })
    if so.items:
        invoice.set("items", [])
        for item in so.items:
            invoice.append("items", {
                "item": item.item,
                "description": item.description,
                "quantity": item.quantity,
                "rate": item.rate,
                "amount": item.amount,
                "tax_code": item.tax_code,
                "tax_amount": item.tax_amount or 0,
                "total_amount_with_tax": item.total_amount_with_tax or item.amount or 0,
            })
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    frappe.db.commit()
    return {"status": "ok", "invoice": invoice.name, "invoice_amount": invoice.invoice_amount}

@frappe.whitelist()
def convert_purchase_order_to_invoice(purchase_order):
    po = frappe.get_doc("Purchase Order", purchase_order)
    if po.docstatus != 1:
        frappe.throw("Purchase Order must be submitted first")
    invoice = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "supplier": po.supplier,
        "issue_date": frappe.utils.today(),
        "invoice_amount": po.total_amount or 0,
        "balance_due": po.total_amount or 0,
        "status": "Unpaid",
        "purchase_order": po.name,
        "division": po.division,
        "business": po.business,
    })
    if po.items:
        invoice.set("items", [])
        for item in po.items:
            invoice.append("items", {
                "item": item.item,
                "description": item.description,
                "quantity": item.quantity,
                "rate": item.rate,
                "amount": item.amount,
                "tax_code": item.tax_code,
                "tax_amount": item.tax_amount or 0,
                "total_amount_with_tax": item.total_amount_with_tax or item.amount or 0,
            })
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    frappe.db.commit()
    return {"status": "ok", "invoice": invoice.name, "invoice_amount": invoice.invoice_amount}

@frappe.whitelist()
def list_currencies():
    return frappe.get_all("Currency", fields=["name", "currency_name", "currency_code", "symbol", "is_base", "is_active", "decimal_places"], order_by="currency_name")

@frappe.whitelist()
def save_currency(data):
    import json as _json
    if isinstance(data, str):
        data = _json.loads(data)
    name = data.get("name")
    if name and frappe.db.exists("Currency", name):
        doc = frappe.get_doc("Currency", name)
        for k, v in data.items():
            if k != "name":
                doc.set(k, v)
        doc.save()
    else:
        doc = frappe.get_doc({"doctype": "Currency", **{k:v for k,v in data.items() if k != "name"}})
        doc.insert()
    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

@frappe.whitelist()
def delete_currency(name):
    if not frappe.db.exists("Currency", name):
        frappe.throw("Currency not found")
    frappe.delete_doc("Currency", name)
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def list_exchange_rates(currency=None):
    filters = {}
    if currency:
        filters["currency"] = currency
    return frappe.get_all("Exchange Rate",
        fields=["name", "currency", "base_currency", "exchange_rate", "date", "buying_rate", "selling_rate"],
        filters=filters,
        order_by="date desc")

@frappe.whitelist()
def save_exchange_rate(data):
    import json as _json
    if isinstance(data, str):
        data = _json.loads(data)
    name = data.get("name")
    if name and frappe.db.exists("Exchange Rate", name):
        doc = frappe.get_doc("Exchange Rate", name)
        for k, v in data.items():
            if k != "name":
                doc.set(k, v)
        doc.save()
    else:
        doc = frappe.get_doc({"doctype": "Exchange Rate", **{k:v for k,v in data.items() if k != "name"}})
        doc.insert()
    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

@frappe.whitelist()
def delete_exchange_rate(name):
    if not frappe.db.exists("Exchange Rate", name):
        frappe.throw("Exchange Rate not found")
    frappe.delete_doc("Exchange Rate", name)
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def calculate_base_amounts(doctype, docname):
    doc = frappe.get_doc(doctype, docname)
    rate = doc.get("exchange_rate") or 1.0
    if doc.get("items"):
        for item in doc.items:
            base = (item.amount or 0) * rate
            item.db_set("base_amount", base, update_modified=False)
    frappe.db.commit()
    return {"status": "ok", "exchange_rate": rate}

@frappe.whitelist()
def get_latest_exchange_rate(from_currency, to_currency=None):
    if not to_currency:
        settings = frappe.get_single("Manager Settings")
        to_currency = settings.currency
    if from_currency == to_currency:
        return {"exchange_rate": 1.0, "date": frappe.utils.today()}
    rates = frappe.get_all("Exchange Rate",
        fields=["exchange_rate", "date"],
        filters={"currency": from_currency, "base_currency": to_currency},
        order_by="date desc", limit=1)
    if rates:
        return {"exchange_rate": rates[0].exchange_rate, "date": rates[0].date}
    return {"exchange_rate": 1.0, "date": frappe.utils.today(), "note": "No rate found, using 1.0"}


@frappe.whitelist()
def list_users():
    return frappe.get_all("Manager User",
        fields=["name", "full_name", "email", "role", "is_active", "can_login", "last_login"],
        order_by="full_name asc")

@frappe.whitelist()
def get_user(name):
    doc = frappe.get_doc("Manager User", name)
    return doc.as_dict()

@frappe.whitelist()
def save_user(data):
    import json as _json
    if isinstance(data, str):
        data = _json.loads(data)
    name = data.get("name")
    email = data.get("email", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "View Only")

    if name and frappe.db.exists("Manager User", name):
        doc = frappe.get_doc("Manager User", name)
        old_email = doc.email
        for k, v in data.items():
            if k not in ("name", "password", "doctype", "businesses"):
                doc.set(k, v)
        # Update child table
        if "businesses" in data and isinstance(data["businesses"], list):
            doc.set("businesses", [])
            for b in data["businesses"]:
                doc.append("businesses", {"business": b.get("business"), "is_default": b.get("is_default", 0)})
        doc.save()
        # Update Frappe User
        if email and email != old_email:
            _update_frappe_user(email, full_name, password, role, doc.name)
        elif password:
            _update_frappe_user(email, full_name, password, role, doc.name)
    else:
        doc = frappe.get_doc({
            "doctype": "Manager User",
            "full_name": full_name,
            "email": email,
            "role": role,
            "is_active": data.get("is_active", 1),
            "can_login": data.get("can_login", 1),
        })
        if "businesses" in data and isinstance(data["businesses"], list):
            for b in data["businesses"]:
                doc.append("businesses", {"business": b.get("business"), "is_default": b.get("is_default", 0)})
        doc.insert()
        _create_frappe_user(email, full_name, password, role, doc.name)

    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

def _create_frappe_user(email, full_name, password, role, manager_user_name):
    if not email or frappe.db.exists("User", email):
        return
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name or email.split("@")[0],
        "send_welcome_email": 0,
    })
    user.flags.ignore_password_policy = True
    user.insert(ignore_permissions=True)
    if password:
        user.new_password = password
    user.save(ignore_permissions=True)
    frappe_role = _map_role(role)
    if frappe_role:
        user.add_roles(frappe_role)
    user.save(ignore_permissions=True)
    frappe.db.commit()

def _update_frappe_user(email, full_name, password, role, manager_user_name):
    if not email or not frappe.db.exists("User", email):
        _create_frappe_user(email, full_name, password, role, manager_user_name)
        return
    user = frappe.get_doc("User", email)
    if full_name:
        user.first_name = full_name.split(" ")[0]
        if len(full_name.split(" ")) > 1:
            user.last_name = " ".join(full_name.split(" ")[1:])
    if password:
        user.flags.ignore_password_policy = True
        user.new_password = password
    frappe_role = _map_role(role)
    if frappe_role:
        user.add_roles(frappe_role)
    user.save(ignore_permissions=True)

def _map_role(role):
    mapping = {
        "Administrator": "System Manager",
        "Manager": "Manager",
        "Accountant": "Accounts User",
        "Sales": "Sales User",
        "Purchases": "Purchase User",
        "View Only": "Blogger",
    }
    frappe_role = mapping.get(role)
    # Ensure role exists
    if frappe_role and not frappe.db.exists("Role", frappe_role):
        r = frappe.get_doc({"doctype": "Role", "role_name": frappe_role})
        r.insert(ignore_permissions=True)
        frappe.db.commit()
    return frappe_role

@frappe.whitelist()
def delete_user(name):
    if not frappe.db.exists("Manager User", name):
        frappe.throw("User not found")
    doc = frappe.get_doc("Manager User", name)
    email = doc.email
    frappe.delete_doc("Manager User", name)
    # Optionally disable Frappe User too
    if email and frappe.db.exists("User", email):
        frappe.db.set_value("User", email, "enabled", 0)
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def reset_user_password(name, new_password):
    if not frappe.db.exists("Manager User", name):
        frappe.throw("User not found")
    doc = frappe.get_doc("Manager User", name)
    if doc.email and frappe.db.exists("User", doc.email):
        user = frappe.get_doc("User", doc.email)
        user.new_password = new_password
        user.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "ok"}
    frappe.throw("User email not found")


@frappe.whitelist()
def delete_doc(doctype, name):
    _check_permission(doctype, "delete")
    doc = frappe.get_doc(doctype, name)
    doc.delete()
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def get_user_permissions():
    """Return current user"s role and permissions for frontend enforcement"""
    mu = get_current_manager_user()
    role = mu.get("role", "Administrator") if mu else "Administrator"
    businesses = get_user_businesses()
    perms = _get_role_permissions(role)
    return {
        "role": role,
        "full_name": mu.get("full_name", "") if mu else "Administrator",
        "businesses": businesses,
        "permissions": {dt: p for dt, p in perms.items()}
    }


@frappe.whitelist()
def set_active_business(business):
    """Set the active business for the current session"""
    if not frappe.db.exists("Business", business):
        frappe.throw("Business not found")
    from frappe.cache_manager import clear_user_cache
    frappe.cache().set_value("active_business_" + frappe.session.user, business)
    return {"status": "ok", "business": business}


@frappe.whitelist()
def create_backup():
    from frappe.utils.backups import new_backup
    from frappe.utils import now_datetime
    backup = new_backup(ignore_files=False, ignore_conf=True, verbose=False)
    files = []
    backup_files = [
        backup.backup_path_db,
        backup.backup_path_files,
        backup.backup_path_private_files,
    ]
    import os
    for fp in backup_files:
        if fp and os.path.exists(fp):
            fname = os.path.basename(fp)
            fsize = os.path.getsize(fp)
            files.append({"filename": fname, "size": fsize, "path": fp})
    site = frappe.local.site
    return {
        "status": "ok",
        "timestamp": str(now_datetime()),
        "site": site,
        "files": files,
        "summary": backup.get_summary(),
    }

@frappe.whitelist()
def list_backups():
    import os
    from frappe.utils import get_datetime
    backup_dir = frappe.get_site_path("private", "backups")
    backups = []
    if os.path.exists(backup_dir):
        for fname in sorted(os.listdir(backup_dir), reverse=True):
            fpath = os.path.join(backup_dir, fname)
            if os.path.isfile(fpath):
                fsize = os.path.getsize(fpath)
                mtime = os.path.getmtime(fpath)
                backups.append({
                    "filename": fname,
                    "size": fsize,
                    "size_display": _format_size(fsize),
                    "modified": str(get_datetime(mtime)),
                    "is_db": fname.endswith(".sql.gz"),
                    "is_files": "files" in fname.lower(),
                    "is_config": "site_config" in fname.lower(),
                })
    return {"backups": backups, "backup_dir": backup_dir}

def _format_size(bytes_val):
    import math
    if bytes_val == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    i = int(math.floor(math.log(bytes_val, 1024))) if bytes_val > 0 else 0
    i = min(i, len(units) - 1)
    s = round(bytes_val / (1024 ** i), 2)
    return "{:.2f} {}".format(s, units[i])

@frappe.whitelist()
def download_backup(filename):
    import os
    backup_dir = frappe.get_site_path("private", "backups")
    fpath = os.path.join(backup_dir, filename)
    if ".." in filename or "/" in filename:
        frappe.throw("Invalid filename")
    if not os.path.exists(fpath):
        frappe.throw("Backup file not found")
    with open(fpath, "rb") as f:
        content = f.read()
    frappe.local.response["filename"] = filename
    frappe.local.response["filecontent"] = content
    frappe.local.response["type"] = "binary"
    frappe.local.response["content_type"] = "application/gzip" if filename.endswith(".gz") else "application/octet-stream"

@frappe.whitelist()
def change_password(old_password, new_password):
    from frappe.auth import LoginManager
    user = frappe.session.user
    if user == "Administrator":
        frappe.throw("Administrator password cannot be changed here. Use the Frappe portal.")
    try:
        lm = LoginManager()
        lm.authenticate(user, old_password)
    except:
        frappe.throw("Current password is incorrect", frappe.AuthenticationError)
    doc = frappe.get_doc("User", user)
    doc.new_password = new_password
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok", "message": "Password changed successfully"}

@frappe.whitelist()
def list_price_lists():
    return frappe.get_all("Price List",
        fields=["name", "price_list_name", "is_active", "is_default", "currency"],
        order_by="price_list_name asc")

@frappe.whitelist()
def save_price_list(data):
    import json as _json
    if isinstance(data, str):
        data = _json.loads(data)
    name = data.get("name")
    if name and frappe.db.exists("Price List", name):
        doc = frappe.get_doc("Price List", name)
        for k, v in data.items():
            if k not in ("name", "doctype", "items"):
                doc.set(k, v)
        if "items" in data and isinstance(data["items"], list):
            doc.set("items", [])
            for item in data["items"]:
                doc.append("items", {
                    "item": item.get("item"),
                    "rate": item.get("rate"),
                    "effective_from": item.get("effective_from"),
                    "effective_to": item.get("effective_to"),
                })
        doc.save()
    else:
        doc = frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": data.get("price_list_name"),
            "is_active": data.get("is_active", 1),
            "is_default": data.get("is_default", 0),
            "currency": data.get("currency"),
        })
        if "items" in data and isinstance(data["items"], list):
            for item in data["items"]:
                doc.append("items", {
                    "item": item.get("item"),
                    "rate": item.get("rate"),
                    "effective_from": item.get("effective_from"),
                    "effective_to": item.get("effective_to"),
                })
        doc.insert()
    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

@frappe.whitelist()
def delete_price_list(name):
    if not frappe.db.exists("Price List", name):
        frappe.throw("Price List not found")
    frappe.delete_doc("Price List", name, force=True)
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def get_price_list_items(price_list):
    if not frappe.db.exists("Price List", price_list):
        frappe.throw("Price List not found")
    doc = frappe.get_doc("Price List", price_list)
    items = []
    for row in doc.items:
        items.append({
            "item": row.item,
            "item_name": row.item_name or row.item,
            "rate": row.rate,
            "effective_from": str(row.effective_from or ""),
            "effective_to": str(row.effective_to or ""),
        })
    return {"price_list": price_list, "items": items, "currency": doc.currency}

@frappe.whitelist()
def get_item_price_from_list(item, price_list=None, date=None):
    """Get the best price for an item from the default or specified price list.
    Returns the rate from the most specific price list entry."""
    if price_list:
        pl_names = [price_list]
    else:
        default_pl = frappe.get_all("Price List",
            filters={"is_default": 1, "is_active": 1},
            limit=1, pluck="name")
        pl_names = default_pl
    if not pl_names:
        return {"rate": None, "price_list": None, "message": "No active price list found"}
    for pl_name in pl_names:
        doc = frappe.get_doc("Price List", pl_name)
        for row in doc.items:
            if row.item == item:
                effective = True
                if row.effective_from:
                    from_date = str(row.effective_from)
                    if date and from_date > date:
                        effective = False
                if row.effective_to:
                    to_date = str(row.effective_to)
                    if date and to_date < date:
                        effective = False
                if effective:
                    return {"rate": row.rate, "price_list": pl_name, "item": item}
    return {"rate": None, "price_list": None, "message": f"No price found for item {item}"}

@frappe.whitelist()
def calculate_invoice_discounts(doctype, name):
    """Calculate discount amounts and net totals for an invoice"""
    doc = frappe.get_doc(doctype, name)
    if not hasattr(doc, "items") or not doc.items:
        return {"status": "ok", "subtotal": 0, "total_discount": 0, "net_total": 0}
    subtotal = 0
    total_discount = 0
    for row in doc.items:
        row_amount = row.amount or 0
        disc_pct = row.get("discount_percentage") or 0
        disc_amt = row.get("discount_amount") or 0
        if disc_pct > 0 and disc_amt == 0:
            disc_amt = round(row_amount * disc_pct / 100, 2)
        if disc_amt > row_amount:
            disc_amt = row_amount
        row.discount_amount = disc_amt
        net_amount = row_amount - disc_amt
        subtotal += row_amount
        total_discount += disc_amt
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {
        "status": "ok",
        "subtotal": subtotal,
        "total_discount": total_discount,
        "net_total": subtotal - total_discount,
    }

@frappe.whitelist()
def apply_price_list_to_invoice(doctype, name, price_list=None):
    """Apply price list rates to all items in an invoice, overriding item rates"""
    doc = frappe.get_doc(doctype, name)
    if not hasattr(doc, "items") or not doc.items:
        return {"status": "ok", "updated": 0}
    updated = 0
    for row in doc.items:
        if not row.item:
            continue
        result = get_item_price_from_list(row.item, price_list)
        if result.get("rate"):
            row.price_list_rate = row.rate
            row.rate = result["rate"]
            row.amount = round((row.rate or 0) * (row.quantity or 1), 2)
            updated += 1
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok", "updated": updated, "price_list": price_list}

# ── Delivery Notes ──

@frappe.whitelist()
def list_delivery_notes(filters=None, limit=100, limit_start=0):
    import json
    if isinstance(filters, str):
        filters = json.loads(filters) if filters else {}
    _check_permission("Delivery Note", "read")
    role = get_user_role()
    if role != "Administrator":
        businesses = get_user_businesses()
        if businesses:
            biz_names = [b.get("name") if isinstance(b, dict) else b for b in businesses]
            filters["business"] = ["in", biz_names]
    total = frappe.db.count("Delivery Note", filters=filters)
    data = frappe.get_list("Delivery Note", fields=["*"], filters=filters, limit=limit, limit_start=limit_start, order_by="modified desc")
    return {"data": data, "total": total}

@frappe.whitelist()
def get_delivery_note(name):
    _check_permission("Delivery Note", "read")
    doc = frappe.get_doc("Delivery Note", name)
    items = []
    for row in doc.items:
        items.append({
            "name": row.name,
            "item": row.item,
            "description": row.description,
            "quantity": row.quantity,
            "rate": row.rate,
            "amount": row.amount,
        })
    return {"data": doc.as_dict(), "items": items}

@frappe.whitelist()
def save_delivery_note(data):
    import json as _json
    if isinstance(data, str):
        data = _json.loads(data)
    _check_permission("Delivery Note", "write" if data.get("name") else "create")
    name = data.get("name")
    if name and frappe.db.exists("Delivery Note", name):
        doc = frappe.get_doc("Delivery Note", name)
        doc.issue_date = data.get("issue_date", doc.issue_date)
        doc.customer = data.get("customer", doc.customer)
        doc.delivery_address = data.get("delivery_address", doc.delivery_address)
        doc.description = data.get("description", doc.description)
        doc.sales_invoice = data.get("sales_invoice", doc.sales_invoice)
        doc.business = data.get("business", doc.business)
        doc.status = data.get("status", doc.status)
        doc.sales_executive = data.get("sales_executive", doc.sales_executive)
        doc.currency = data.get("currency", doc.currency)
        doc.exchange_rate = data.get("exchange_rate", doc.exchange_rate)
        total = 0
        doc.set("items", [])
        for item in data.get("items", []):
            amt = (item.get("rate") or 0) * (item.get("quantity") or 1)
            total += amt
            doc.append("items", {
                "item": item.get("item"),
                "description": item.get("description"),
                "quantity": item.get("quantity"),
                "rate": item.get("rate"),
                "amount": amt,
            })
        doc.total_amount = total
        doc.save()
    else:
        doc = frappe.get_doc({
            "doctype": "Delivery Note",
            "issue_date": data.get("issue_date"),
            "customer": data.get("customer"),
            "delivery_address": data.get("delivery_address"),
            "description": data.get("description"),
            "sales_invoice": data.get("sales_invoice"),
            "business": data.get("business"),
            "status": data.get("status", "Draft"),
            "sales_executive": data.get("sales_executive"),
            "currency": data.get("currency", "USD"),
            "exchange_rate": data.get("exchange_rate", 1.0),
        })
        total = 0
        for item in data.get("items", []):
            amt = (item.get("rate") or 0) * (item.get("quantity") or 1)
            total += amt
            doc.append("items", {
                "item": item.get("item"),
                "description": item.get("description"),
                "quantity": item.get("quantity"),
                "rate": item.get("rate"),
                "amount": amt,
            })
        doc.total_amount = total
        doc.insert()
    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

@frappe.whitelist()
def delete_delivery_note(name):
    _check_permission("Delivery Note", "delete")
    if not frappe.db.exists("Delivery Note", name):
        frappe.throw("Delivery Note not found")
    frappe.delete_doc("Delivery Note", name, force=True)
    frappe.db.commit()
    return {"status": "ok"}
# ── Payment Terms ──

@frappe.whitelist()
def list_payment_terms():
    _check_permission("Payment Term", "read")
    data = frappe.get_all("Payment Term", fields=["*"], order_by="term_name asc")
    return {"data": data}

@frappe.whitelist()
def save_payment_term(data):
    import json as _json
    if isinstance(data, str):
        data = _json.loads(data)
    _check_permission("Payment Term", "write" if data.get("name") else "create")
    name = data.get("name")
    if name and frappe.db.exists("Payment Term", name):
        doc = frappe.get_doc("Payment Term", name)
        doc.term_name = data.get("term_name", doc.term_name)
        doc.due_days = data.get("due_days", doc.due_days)
        doc.discount_percentage = data.get("discount_percentage", doc.discount_percentage)
        doc.discount_days = data.get("discount_days", doc.discount_days)
        doc.is_default = data.get("is_default", doc.is_default)
        doc.save()
    else:
        doc = frappe.get_doc({
            "doctype": "Payment Term",
            "term_name": data.get("term_name"),
            "due_days": data.get("due_days", 30),
            "discount_percentage": data.get("discount_percentage", 0),
            "discount_days": data.get("discount_days", 0),
            "is_default": data.get("is_default", 0),
        })
        doc.insert()
    frappe.db.commit()
    return {"name": doc.name, "data": doc.as_dict()}

@frappe.whitelist()
def delete_payment_term(name):
    _check_permission("Payment Term", "delete")
    if not frappe.db.exists("Payment Term", name):
        frappe.throw("Payment Term not found")
    frappe.delete_doc("Payment Term", name, force=True)
    frappe.db.commit()
    return {"status": "ok"}
# ── Budget vs Actual ──

@frappe.whitelist()
def get_budget_vs_actual(name):
    _check_permission("Budget", "read")
    doc = frappe.get_doc("Budget", name)
    result = {
        "name": doc.name,
        "budget_name": doc.budget_name,
        "fiscal_year": doc.fiscal_year,
        "business": doc.business,
        "accounts": [],
        "total_budget": 0,
        "total_actual": 0,
    }
    for row in doc.accounts:
        account_name = row.account
        budget_amt = row.budget_amount or 0
        actual_amt = 0
        if account_name:
            acct = frappe.db.get_value("Account", account_name, "balance")
            actual_amt = abs(acct or 0)
        result["accounts"].append({
            "account": account_name,
            "budget_amount": budget_amt,
            "actual_amount": actual_amt,
            "variance": round(actual_amt - budget_amt, 2),
        })
        result["total_budget"] += budget_amt
        result["total_actual"] += actual_amt
    result["total_variance"] = round(result["total_actual"] - result["total_budget"], 2)
    return {"data": result}
# ── Recurring Transactions ──

@frappe.whitelist()
def toggle_recurring_transaction(name, enabled=0):
    _check_permission("Recurring Transaction", "write")
    doc = frappe.get_doc("Recurring Transaction", name)
    doc.enabled = 1 if enabled else 0
    doc.save()
    frappe.db.commit()
    return {"status": "ok", "enabled": doc.enabled}

@frappe.whitelist()
def run_recurring_transaction(name):
    _check_permission("Recurring Transaction", "write")
    doc = frappe.get_doc("Recurring Transaction", name)
    if not doc.enabled:
        frappe.throw("Recurring transaction is disabled")
    result = _create_from_template(doc)
    # Update next_date based on frequency
    from datetime import datetime, timedelta
    import json as _json
    from dateutil.relativedelta import relativedelta
    next_dt = doc.next_date
    if doc.frequency == "Daily":
        next_dt = next_dt + timedelta(days=1)
    elif doc.frequency == "Weekly":
        next_dt = next_dt + timedelta(weeks=1)
    elif doc.frequency == "Monthly":
        next_dt = next_dt + relativedelta(months=1)
    elif doc.frequency == "Quarterly":
        next_dt = next_dt + relativedelta(months=3)
    elif doc.frequency == "Yearly":
        next_dt = next_dt + relativedelta(years=1)
    doc.next_date = next_dt
    doc.save()
    frappe.db.commit()
    return {"status": "ok", "created": result}

@frappe.whitelist()
def process_due_recurring():
    _check_permission("Recurring Transaction", "write")
    from datetime import datetime
    due = frappe.get_all("Recurring Transaction",
        filters={"enabled": 1, "next_date": ["<=", datetime.now().strftime("%Y-%m-%d")]},
        fields=["name", "title", "next_date", "frequency"])
    results = []
    for r in due:
        try:
            doc = frappe.get_doc("Recurring Transaction", r.name)
            created = _create_from_template(doc)
            from datetime import timedelta
            from dateutil.relativedelta import relativedelta
            next_dt = doc.next_date
            if doc.frequency == "Daily":
                next_dt = next_dt + timedelta(days=1)
            elif doc.frequency == "Weekly":
                next_dt = next_dt + timedelta(weeks=1)
            elif doc.frequency == "Monthly":
                next_dt = next_dt + relativedelta(months=1)
            elif doc.frequency == "Quarterly":
                next_dt = next_dt + relativedelta(months=3)
            elif doc.frequency == "Yearly":
                next_dt = next_dt + relativedelta(years=1)
            doc.next_date = next_dt
            doc.save()
            results.append({"name": r.name, "title": r.title, "status": "ok", "created": created})
        except Exception as e:
            results.append({"name": r.name, "title": r.title, "status": "error", "error": str(e)})
    frappe.db.commit()
    return {"results": results, "total": len(results)}

def _create_from_template(doc):
    """Create a transaction from the recurring template"""
    import json as _json
    template = _json.loads(doc.template_data) if isinstance(doc.template_data, str) else (doc.template_data or {})
    if not template:
        frappe.throw("No template data configured")
    doctype = doc.reference_doctype
    data = dict(template)
    data["doctype"] = doctype
    data["business"] = data.get("business") or doc.business
    data["date"] = data.get("date") or str(doc.next_date)
    if "issue_date" not in data:
        data["issue_date"] = str(doc.next_date)
    new_doc = frappe.get_doc(data)
    new_doc.insert()
    return new_doc.name
# ── Stock Balance ──

@frappe.whitelist()
def get_stock_balance():
    _check_permission("Item", "read")
    items = frappe.get_all("Item", fields=["name", "item_name", "item_type", "opening_stock", "opening_value"])
    result = []
    for item in items:
        qty = item.opening_stock or 0
        val = item.opening_value or 0
        transfers_in = frappe.db.get_all("Inventory Transfer Item", filters={"item": item.name}, pluck="quantity")
        for tq in transfers_in:
            qty += tq or 0
        result.append({
            "name": item.name,
            "item_name": item.item_name or item.name,
            "item_type": item.item_type,
            "quantity": qty,
            "value": val,
        })
    return {"data": result}

# ── CSV Import ──

@frappe.whitelist()
def import_csv(doctype, data):
    import json as _json
    if isinstance(data, str):
        data = _json.loads(data)
    _check_permission(doctype, "create")
    created = 0
    errors = []
    for row in data:
        try:
            doc_data = {"doctype": doctype}
            doc_data.update(row)
            doc = frappe.get_doc(doc_data)
            doc.insert()
            created += 1
        except Exception as e:
            errors.append({"row": row, "error": str(e)})
    frappe.db.commit()
    return {"created": created, "errors": errors}
