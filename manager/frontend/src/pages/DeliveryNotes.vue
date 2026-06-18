<template>
  <ListPage title="Delivery Notes" singular="Delivery Note" :columns="columns" :rows="notes" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'name', label: '#' },
  { key: 'customer', label: 'Customer' },
  { key: 'posting_date', label: 'Date', format: 'date' },
  { key: 'total_amount', label: 'Total', format: 'currency' },
  { key: 'status', label: 'Status' },
]
const notes = ref([])

onMounted(async () => {
  notes.value = await getList('Delivery Note', {}, ['name', 'customer', 'posting_date', 'total_amount', 'status'])
})
</script>
