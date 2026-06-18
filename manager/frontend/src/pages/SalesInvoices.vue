<template>
  <ListPage title="Sales Invoices" singular="Invoice" :columns="columns" :rows="invoices" @create="createNew" @row-click="(r) => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'name', label: '#' },
  { key: 'customer', label: 'Customer' },
  { key: 'posting_date', label: 'Date', format: 'date' },
  { key: 'grand_total', label: 'Total', format: 'currency' },
  { key: 'outstanding_amount', label: 'Outstanding', format: 'currency' },
  { key: 'status', label: 'Status' },
]
const invoices = ref([])

function createNew() {}

onMounted(async () => {
  invoices.value = await getList('Sales Invoice', {}, ['name', 'customer', 'posting_date', 'grand_total', 'outstanding_amount', 'status'])
})
</script>
