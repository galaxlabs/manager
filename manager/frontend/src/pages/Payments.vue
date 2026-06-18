<template>
  <ListPage title="Payments" singular="Payment" :columns="columns" :rows="payments" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'name', label: '#' },
  { key: 'party', label: 'Supplier' },
  { key: 'posting_date', label: 'Date', format: 'date' },
  { key: 'paid_amount', label: 'Amount', format: 'currency' },
  { key: 'mode_of_payment', label: 'Mode' },
  { key: 'status', label: 'Status' },
]
const payments = ref([])

onMounted(async () => {
  payments.value = await getList('Payment', {}, ['name', 'party', 'posting_date', 'paid_amount', 'mode_of_payment', 'status'])
})
</script>
