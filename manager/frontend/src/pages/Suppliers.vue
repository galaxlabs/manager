<template>
  <ListPage title="Suppliers" singular="Supplier" :columns="columns" :rows="suppliers" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'supplier_name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'mobile', label: 'Phone' },
]
const suppliers = ref([])

onMounted(async () => {
  suppliers.value = await getList('Supplier', {}, ['name', 'supplier_name', 'email', 'mobile'])
})
</script>
