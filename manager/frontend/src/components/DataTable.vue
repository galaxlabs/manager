<template>
  <div class="data-table-wrapper">
    <table class="data-table">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" @click="col.sortable !== false && toggleSort(col.key)">
            <span>{{ col.label }}</span>
            <span v-if="col.sortable !== false" class="sort-icon">
              {{ sortKey === col.key ? (sortDir === 'asc' ? ' ▲' : ' ▼') : '' }}
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!rows.length">
          <td :colspan="columns.length" class="empty-state">No records found</td>
        </tr>
        <tr v-for="(row, i) in sortedRows" :key="row.name || i" @click="$emit('row-click', row)" class="data-row">
          <td v-for="col in columns" :key="col.key">
            <span v-if="col.format === 'currency'">{{ formatCurrency(row[col.key]) }}</span>
            <span v-else-if="col.format === 'date'">{{ formatDate(row[col.key]) }}</span>
            <span v-else>{{ row[col.key] }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
})

defineEmits(['row-click'])

const sortKey = ref('')
const sortDir = ref('asc')

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const sortedRows = computed(() => {
  if (!sortKey.value) return props.rows
  const rows = [...props.rows]
  rows.sort((a, b) => {
    const va = a[sortKey.value]
    const vb = b[sortKey.value]
    if (va == null) return 1
    if (vb == null) return -1
    const cmp = typeof va === 'number' ? va - vb : String(va).localeCompare(String(vb))
    return sortDir.value === 'asc' ? cmp : -cmp
  })
  return rows
})

function formatCurrency(v) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v || 0)
}

function formatDate(v) {
  if (!v) return ''
  return new Date(v).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>
