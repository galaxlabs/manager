<template>
  <ListPage title="Items" singular="Item" :columns="columns" :rows="items" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'item_name', label: 'Name' },
  { key: 'item_type', label: 'Type' },
  { key: 'unit', label: 'Unit' },
  { key: 'rate', label: 'Rate', format: 'currency' },
  { key: 'opening_stock', label: 'Opening Stock' },
]
const items = ref([])

onMounted(async () => {
  items.value = await getList('Item', {}, ['name', 'item_name', 'item_type', 'unit', 'rate', 'opening_stock'])
})
</script>
