import frappe, json

def create_manager_workspace():
    """Create Manager workspace with full sidebar navigation"""

    if frappe.db.exists('Workspace', 'manager'):
        frappe.delete_doc('Workspace', 'manager', force=1)
        frappe.db.commit()

    workspace = frappe.get_doc({
        'doctype': 'Workspace',
        'name': 'manager',
        'module': 'Manager',
        'title': 'Manager',
        'label': 'Manager',
        'icon': 'fa fa-building',
        'is_default': 1,
        'public': 1,
        'hide_custom': 0,
        'content': json.dumps({
            'type': 'workspace_links',
            'col1': [
                {
                    'label': 'Summary',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Dashboard', 'link_to': '/app/workspace/manager', 'link_type': 'URL', 'icon': 'fa fa-presentation'},
                    ]
                },
                {
                    'label': 'Banking',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Accounts', 'link_to': '/app/account', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-money-check-edit'},
                        {'type': 'link', 'label': 'Receipts', 'link_to': '/app/receipt', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-arrow-alt-to-right'},
                        {'type': 'link', 'label': 'Payments', 'link_to': '/app/payment', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-arrow-alt-to-right'},
                        {'type': 'link', 'label': 'Account Transfers', 'link_to': '/app/account-transfer', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-exchange'},
                    ]
                },
                {
                    'label': 'Sales',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Customers', 'link_to': '/app/customer', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-people-group'},
                        {'type': 'link', 'label': 'Sales Orders', 'link_to': '/app/sales-order', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-shopping-cart'},
                        {'type': 'link', 'label': 'Sales Invoices', 'link_to': '/app/sales-invoice', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-file-invoice'},
                        {'type': 'link', 'label': 'Delivery Notes', 'link_to': '/app/delivery-note', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-truck'},
                    ]
                },
                {
                    'label': 'Purchases',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Suppliers', 'link_to': '/app/supplier', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-people-group'},
                        {'type': 'link', 'label': 'Purchase Orders', 'link_to': '/app/purchase-order', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-shopping-basket'},
                        {'type': 'link', 'label': 'Purchase Invoices', 'link_to': '/app/purchase-invoice', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-file-invoice'},
                    ]
                },
            ],
            'col2': [
                {
                    'label': 'Inventory',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Items', 'link_to': '/app/item', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-inventory'},
                        {'type': 'link', 'label': 'Production Orders', 'link_to': '/app/sales-order', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-mask'},
                    ]
                },
                {
                    'label': 'Payroll',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Employees', 'link_to': '/app/employee', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-id-card'},
                    ]
                },
                {
                    'label': 'Fixed Assets',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Fixed Assets', 'link_to': '/app/fixed-asset', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-car-building'},
                    ]
                },
                {
                    'label': 'Accounting',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Journal Entries', 'link_to': '/app/journal-entry', 'link_type': 'DocType', 'doc_view': 'List', 'icon': 'fa fa-mask'},
                    ]
                },
                {
                    'label': 'Reports',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'Profit & Loss', 'link_to': '#', 'link_type': 'URL', 'icon': 'fa fa-presentation'},
                        {'type': 'link', 'label': 'Balance Sheet', 'link_to': '#', 'link_type': 'URL', 'icon': 'fa fa-balance-scale'},
                        {'type': 'link', 'label': 'Trial Balance', 'link_to': '#', 'link_type': 'URL', 'icon': 'fa fa-file-invoice'},
                    ]
                },
                {
                    'label': 'Settings',
                    'type': 'card',
                    'links': [
                        {'type': 'link', 'label': 'General Settings', 'link_to': '#', 'link_type': 'URL', 'icon': 'fa fa-cog'},
                    ]
                },
            ]
        })
    })

    workspace.insert(ignore_permissions=True)
    frappe.db.commit()
    print('Workspace created: Manager')

create_manager_workspace()
