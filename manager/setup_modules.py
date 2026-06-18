import frappe, json

MODULE_MAP = {
    "Sales": ["Customer", "Sales Order", "Sales Invoice", "Delivery Note"],
    "Purchases": ["Supplier", "Purchase Order", "Purchase Invoice"],
    "Banking": ["Account", "Receipt", "Payment", "Account Transfer"],
    "Inventory": ["Item", "Invoice Item"],
    "Accounting": ["Journal Entry", "Journal Entry Account"],
    "Payroll": ["Employee"],
    "FixedAssets": ["Fixed Asset"],
}

def create_modules():
    for module_name in MODULE_MAP:
        if not frappe.db.exists("Module Def", module_name):
            m = frappe.get_doc({
                "doctype": "Module Def",
                "module_name": module_name,
                "app_name": "manager",
            })
            m.insert(ignore_permissions=True)
            print(f"  Created Module Def: {module_name}")

def move_doctypes():
    for module_name, doctypes in MODULE_MAP.items():
        for dt in doctypes:
            if frappe.db.exists("DocType", dt):
                frappe.db.set_value("DocType", dt, "module", module_name)
                print(f"  Moved {dt} -> {module_name}")

    # Also move Manager Settings
    if frappe.db.exists("DocType", "Manager Settings"):
        frappe.db.set_value("DocType", "Manager Settings", "module", "Accounting")

    frappe.db.commit()

def create_workspaces():
    workspace_configs = [
        {
            "name": "manager-sales",
            "title": "Sales",
            "icon": "fa fa-shopping-cart",
            "module": "Sales",
            "links": [
                {"label": "Customers", "icon": "fa fa-people-group", "doctype": "Customer"},
                {"label": "Sales Orders", "icon": "fa fa-cart-plus", "doctype": "Sales Order"},
                {"label": "Sales Invoices", "icon": "fa fa-file-invoice", "doctype": "Sales Invoice"},
                {"label": "Delivery Notes", "icon": "fa fa-truck", "doctype": "Delivery Note"},
            ]
        },
        {
            "name": "manager-purchases",
            "title": "Purchases",
            "icon": "fa fa-shopping-basket",
            "module": "Purchases",
            "links": [
                {"label": "Suppliers", "icon": "fa fa-people-group", "doctype": "Supplier"},
                {"label": "Purchase Orders", "icon": "fa fa-cart-arrow-down", "doctype": "Purchase Order"},
                {"label": "Purchase Invoices", "icon": "fa fa-file-invoice", "doctype": "Purchase Invoice"},
            ]
        },
        {
            "name": "manager-banking",
            "title": "Banking",
            "icon": "fa fa-money-check",
            "module": "Banking",
            "links": [
                {"label": "Chart of Accounts", "icon": "fa fa-book", "doctype": "Account"},
                {"label": "Receipts", "icon": "fa fa-arrow-right", "doctype": "Receipt"},
                {"label": "Payments", "icon": "fa fa-arrow-left", "doctype": "Payment"},
                {"label": "Account Transfers", "icon": "fa fa-exchange", "doctype": "Account Transfer"},
            ]
        },
        {
            "name": "manager-inventory",
            "title": "Inventory",
            "icon": "fa fa-warehouse",
            "module": "Inventory",
            "links": [
                {"label": "Items", "icon": "fa fa-cube", "doctype": "Item"},
            ]
        },
        {
            "name": "manager-accounting",
            "title": "Accounting",
            "icon": "fa fa-calculator",
            "module": "Accounting",
            "links": [
                {"label": "Journal Entries", "icon": "fa fa-book", "doctype": "Journal Entry"},
                {"label": "Manager Settings", "icon": "fa fa-cog", "doctype": "Manager Settings"},
            ]
        },
        {
            "name": "manager-payroll",
            "title": "Payroll",
            "icon": "fa fa-id-card",
            "module": "Payroll",
            "links": [
                {"label": "Employees", "icon": "fa fa-users", "doctype": "Employee"},
            ]
        },
        {
            "name": "manager-fixed-assets",
            "title": "Fixed Assets",
            "icon": "fa fa-building",
            "module": "FixedAssets",
            "links": [
                {"label": "Fixed Assets", "icon": "fa fa-car", "doctype": "Fixed Asset"},
            ]
        },
    ]

    for cfg in workspace_configs:
        name = cfg["name"]
        if frappe.db.exists("Workspace", name):
            frappe.delete_doc("Workspace", name, force=1)
            frappe.db.commit()

        content_blocks = []
        col1 = []
        col2 = []
        mid = len(cfg["links"]) // 2 + len(cfg["links"]) % 2
        for i, link in enumerate(cfg["links"]):
            card = {
                "label": link["label"],
                "type": "card",
                "links": [
                    {
                        "type": "link",
                        "label": link["label"],
                        "link_to": f"/app/{link['doctype'].lower().replace(' ', '-')}",
                        "link_type": "DocType",
                        "doc_view": "List",
                        "icon": link["icon"],
                    }
                ]
            }
            if i < mid:
                col1.append(card)
            else:
                col2.append(card)

        ws = frappe.get_doc({
            "doctype": "Workspace",
            "name": name,
            "module": cfg["module"],
            "title": cfg["title"],
            "label": cfg["title"],
            "icon": cfg["icon"],
            "public": 1,
            "hide_custom": 0,
            "content": json.dumps({
                "type": "workspace_links",
                "col1": col1,
                "col2": col2,
            })
        })
        ws.insert(ignore_permissions=True)
        print(f"  Created Workspace: {cfg['title']}")

    frappe.db.commit()

if __name__ == "__main__":
    print("Creating modules...")
    create_modules()
    print("Moving doctypes...")
    move_doctypes()
    print("Creating workspaces...")
    create_workspaces()
    print("Done!")
