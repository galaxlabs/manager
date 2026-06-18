<template>
  <ListPage title="Chart of Accounts" singular="Account" :columns="columns" :rows="accounts" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'account_name', label: 'Account' },
  { key: 'account_type', label: 'Type' },
  { key: 'account_number', label: 'Number' },
  { key: 'root_type', label: 'Root Type' },
  { key: 'balance', label: 'Balance', format: 'currency' },
]
const accounts = ref([])

onMounted(async () => {
  accounts.value = await getList('Account', {}, ['name', 'account_name', 'account_type', 'account_number', 'root_type', 'balance'])
})
</script>
