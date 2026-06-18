<template>
  <ListPage title="Customers" singular="Customer" :columns="columns" :rows="customers" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'customer_name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'mobile', label: 'Phone' },
  { key: 'status', label: 'Status' },
]
const customers = ref([])

onMounted(async () => {
  customers.value = await getList('Customer', {}, ['name', 'customer_name', 'email', 'mobile', 'status'])
})
</script>
