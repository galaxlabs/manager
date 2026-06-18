<template>
  <ListPage title="Account Transfers" singular="Transfer" :columns="columns" :rows="transfers" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'name', label: '#' },
  { key: 'from_account', label: 'From Account' },
  { key: 'to_account', label: 'To Account' },
  { key: 'posting_date', label: 'Date', format: 'date' },
  { key: 'amount', label: 'Amount', format: 'currency' },
]
const transfers = ref([])

onMounted(async () => {
  transfers.value = await getList('Account Transfer', {}, ['name', 'from_account', 'to_account', 'posting_date', 'amount'])
})
</script>
