<template>
  <div class="page dashboard">
    <div class="page-header">
      <h1>Dashboard</h1>
      <div class="date-range">
        <select v-model="period" class="input">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
          <option value="year">This Year</option>
        </select>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Sales Revenue</div>
        <div class="kpi-value">{{ formatCurrency(totalSales) }}</div>
        <div class="kpi-trend" :class="salesTrend >= 0 ? 'up' : 'down'">
          {{ salesTrend >= 0 ? '+' : '' }}{{ salesTrend }}% vs last period
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Purchases</div>
        <div class="kpi-value">{{ formatCurrency(totalPurchases) }}</div>
        <div class="kpi-trend" :class="purchaseTrend >= 0 ? 'up' : 'down'">
          {{ purchaseTrend >= 0 ? '+' : '' }}{{ purchaseTrend }}% vs last period
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Bank Balance</div>
        <div class="kpi-value">{{ formatCurrency(bankBalance) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Outstanding</div>
        <div class="kpi-value">{{ formatCurrency(outstanding) }}</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="card">
        <div class="card-header"><h2>Recent Invoices</h2></div>
        <DataTable :columns="recentColumns" :rows="recentInvoices" />
      </div>
      <div class="card">
        <div class="card-header"><h2>Quick Actions</h2></div>
        <div class="quick-actions">
          <router-link v-for="action in quickActions" :key="action.label" :to="action.to" class="action-btn">
            {{ action.label }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from '@/components/DataTable.vue'
import { getList, frappeCall } from '@/api/frappe'

const period = ref('month')
const totalSales = ref(0)
const totalPurchases = ref(0)
const bankBalance = ref(0)
const outstanding = ref(0)
const salesTrend = ref(5)
const purchaseTrend = ref(-2)
const recentInvoices = ref([])
const recentColumns = [
  { key: 'name', label: '#' },
  { key: 'customer', label: 'Customer' },
  { key: 'grand_total', label: 'Amount', format: 'currency' },
  { key: 'status', label: 'Status' },
  { key: 'posting_date', label: 'Date' },
]
const quickActions = [
  { label: 'New Invoice', to: '/sales/invoices' },
  { label: 'New Receipt', to: '/banking/receipts' },
  { label: 'New Payment', to: '/banking/payments' },
  { label: 'New Customer', to: '/sales/customers' },
  { label: 'New Item', to: '/inventory/items' },
]

function formatCurrency(v) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v || 0)
}

onMounted(async () => {
  try {
    recentInvoices.value = await getList('Sales Invoice', {}, ['name', 'customer', 'grand_total', 'status', 'posting_date'], 5)
    const sales = await getList('Sales Invoice', {}, ['grand_total'])
    totalSales.value = sales.reduce((s, i) => s + (i.grand_total || 0), 0)
    const purchases = await getList('Purchase Invoice', {}, ['grand_total'])
    totalPurchases.value = purchases.reduce((s, i) => s + (i.grand_total || 0), 0)
  } catch (e) {
    console.error('Dashboard load error:', e)
  }
})
</script>
