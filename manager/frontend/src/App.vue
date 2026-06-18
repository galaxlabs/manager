<template>
  <div class="app-layout">
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="2" width="20" height="20" rx="4" />
            <path d="M8 8h8M8 12h8M8 16h5" />
          </svg>
          <span v-if="!sidebarCollapsed">Manager</span>
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path v-if="!sidebarCollapsed" d="M15 18l-6-6 6-6" />
            <path v-else d="M9 18l6-6-6-6" />
          </svg>
        </button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" exact-active-class="active">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
          </svg>
          <span v-if="!sidebarCollapsed">Dashboard</span>
        </router-link>

        <div class="nav-section">
          <div class="nav-section-title" v-if="!sidebarCollapsed">Sales</div>
          <router-link to="/sales/invoices" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <span v-if="!sidebarCollapsed">Invoices</span>
          </router-link>
          <router-link to="/sales/orders" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <span v-if="!sidebarCollapsed">Orders</span>
          </router-link>
          <router-link to="/sales/customers" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
            </svg>
            <span v-if="!sidebarCollapsed">Customers</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title" v-if="!sidebarCollapsed">Purchases</div>
          <router-link to="/purchases/invoices" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <span v-if="!sidebarCollapsed">Invoices</span>
          </router-link>
          <router-link to="/purchases/orders" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <span v-if="!sidebarCollapsed">Orders</span>
          </router-link>
          <router-link to="/purchases/suppliers" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
            </svg>
            <span v-if="!sidebarCollapsed">Suppliers</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title" v-if="!sidebarCollapsed">Banking</div>
          <router-link to="/banking/receipts" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" />
            </svg>
            <span v-if="!sidebarCollapsed">Receipts</span>
          </router-link>
          <router-link to="/banking/payments" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 18 13.5 8.5 8.5 13.5 1 6" /><polyline points="17 18 23 18 23 12" />
            </svg>
            <span v-if="!sidebarCollapsed">Payments</span>
          </router-link>
          <router-link to="/banking/transfers" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="17 1 21 5 17 9" /><path d="M3 11V9a4 4 0 014-4h14" />
              <polyline points="7 23 3 19 7 15" /><path d="M21 13v2a4 4 0 01-4 4H3" />
            </svg>
            <span v-if="!sidebarCollapsed">Transfers</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title" v-if="!sidebarCollapsed">Inventory</div>
          <router-link to="/inventory/items" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
              <polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" y1="22.08" x2="12" y2="12" />
            </svg>
            <span v-if="!sidebarCollapsed">Items</span>
          </router-link>
          <router-link to="/inventory/delivery-notes" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="1" y="3" width="15" height="13" /><polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
              <circle cx="5.5" cy="18.5" r="2.5" /><circle cx="18.5" cy="18.5" r="2.5" />
            </svg>
            <span v-if="!sidebarCollapsed">Delivery Notes</span>
          </router-link>
        </div>

        <div class="nav-section">
          <div class="nav-section-title" v-if="!sidebarCollapsed">Accounting</div>
          <router-link to="/accounting/accounts" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" /><line x1="8" y1="21" x2="16" y2="21" />
              <line x1="12" y1="17" x2="12" y2="21" />
            </svg>
            <span v-if="!sidebarCollapsed">Chart of Accounts</span>
          </router-link>
          <router-link to="/accounting/journal-entries" class="nav-item" active-class="active">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
              <line x1="8" y1="13" x2="16" y2="13" /><line x1="8" y1="17" x2="16" y2="17" />
            </svg>
            <span v-if="!sidebarCollapsed">Journal Entries</span>
          </router-link>
        </div>

        <router-link to="/fixed-assets" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="4" y="4" width="16" height="16" rx="2" /><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 15h3M1 9h3M1 15h3" />
          </svg>
          <span v-if="!sidebarCollapsed">Fixed Assets</span>
        </router-link>

        <router-link to="/payroll/employees" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
          </svg>
          <span v-if="!sidebarCollapsed">Employees</span>
        </router-link>
      </nav>
    </aside>

    <main class="main-content">
      <TopBar :sidebar-collapsed="sidebarCollapsed" @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopBar from '@/components/TopBar.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const sidebarCollapsed = ref(false)

onMounted(async () => {
  const loggedIn = await auth.checkSession()
  if (!loggedIn) {
    window.location.href = '/login?redirect-to=%2Fmanager'
  }
})
</script>
