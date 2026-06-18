<template>
  <ListPage title="Sales Orders" singular="Order" :columns="columns" :rows="orders" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'name', label: '#' },
  { key: 'customer', label: 'Customer' },
  { key: 'transaction_date', label: 'Date', format: 'date' },
  { key: 'grand_total', label: 'Total', format: 'currency' },
  { key: 'status', label: 'Status' },
]
const orders = ref([])

onMounted(async () => {
  orders.value = await getList('Sales Order', {}, ['name', 'customer', 'transaction_date', 'grand_total', 'status'])
})
</script>
