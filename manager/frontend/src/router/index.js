import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
  { path: '/sales/invoices', name: 'SalesInvoices', component: () => import('@/pages/SalesInvoices.vue') },
  { path: '/sales/orders', name: 'SalesOrders', component: () => import('@/pages/SalesOrders.vue') },
  { path: '/sales/customers', name: 'Customers', component: () => import('@/pages/Customers.vue') },
  { path: '/purchases/invoices', name: 'PurchaseInvoices', component: () => import('@/pages/PurchaseInvoices.vue') },
  { path: '/purchases/orders', name: 'PurchaseOrders', component: () => import('@/pages/PurchaseOrders.vue') },
  { path: '/purchases/suppliers', name: 'Suppliers', component: () => import('@/pages/Suppliers.vue') },
  { path: '/banking/receipts', name: 'Receipts', component: () => import('@/pages/Receipts.vue') },
  { path: '/banking/payments', name: 'Payments', component: () => import('@/pages/Payments.vue') },
  { path: '/banking/transfers', name: 'AccountTransfers', component: () => import('@/pages/AccountTransfers.vue') },
  { path: '/inventory/items', name: 'Items', component: () => import('@/pages/Items.vue') },
  { path: '/inventory/delivery-notes', name: 'DeliveryNotes', component: () => import('@/pages/DeliveryNotes.vue') },
  { path: '/fixed-assets', name: 'FixedAssets', component: () => import('@/pages/FixedAssets.vue') },
  { path: '/accounting/accounts', name: 'Accounts', component: () => import('@/pages/Accounts.vue') },
  { path: '/accounting/journal-entries', name: 'JournalEntries', component: () => import('@/pages/JournalEntries.vue') },
  { path: '/payroll/employees', name: 'Employees', component: () => import('@/pages/Employees.vue') },
]

const router = createRouter({
  history: createWebHistory('/manager/'),
  routes,
})

export default router
