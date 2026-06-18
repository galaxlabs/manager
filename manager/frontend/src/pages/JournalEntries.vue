<template>
  <ListPage title="Journal Entries" singular="Entry" :columns="columns" :rows="entries" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'name', label: '#' },
  { key: 'posting_date', label: 'Date', format: 'date' },
  { key: 'total_debit', label: 'Total Debit', format: 'currency' },
  { key: 'total_credit', label: 'Total Credit', format: 'currency' },
  { key: 'status', label: 'Status' },
]
const entries = ref([])

onMounted(async () => {
  entries.value = await getList('Journal Entry', {}, ['name', 'posting_date', 'total_debit', 'total_credit', 'status'])
})
</script>
