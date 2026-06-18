<template>
  <ListPage title="Fixed Assets" singular="Asset" :columns="columns" :rows="assets" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'asset_name', label: 'Name' },
  { key: 'asset_type', label: 'Type' },
  { key: 'purchase_date', label: 'Purchase Date', format: 'date' },
  { key: 'purchase_cost', label: 'Cost', format: 'currency' },
  { key: 'status', label: 'Status' },
]
const assets = ref([])

onMounted(async () => {
  assets.value = await getList('Fixed Asset', {}, ['name', 'asset_name', 'asset_type', 'purchase_date', 'purchase_cost', 'status'])
})
</script>
