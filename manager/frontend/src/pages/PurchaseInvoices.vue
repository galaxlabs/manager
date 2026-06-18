<template>
  <ListPage title="Purchase Invoices" singular="Invoice" :columns="columns" :rows="invoices" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'name', label: '#' },
  { key: 'supplier', label: 'Supplier' },
  { key: 'posting_date', label: 'Date', format: 'date' },
  { key: 'grand_total', label: 'Total', format: 'currency' },
  { key: 'outstanding_amount', label: 'Outstanding', format: 'currency' },
  { key: 'status', label: 'Status' },
]
const invoices = ref([])

onMounted(async () => {
  invoices.value = await getList('Purchase Invoice', {}, ['name', 'supplier', 'posting_date', 'grand_total', 'outstanding_amount', 'status'])
})
</script>
