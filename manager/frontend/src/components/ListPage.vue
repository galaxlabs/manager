<template>
  <div class="list-page">
    <div class="page-header">
      <h1>{{ title }}</h1>
      <button class="btn btn-primary" @click="$emit('create')">+ New {{ singular }}</button>
    </div>

    <div class="toolbar">
      <div class="search-box">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input v-model="search" type="text" :placeholder="'Search ' + title.toLowerCase() + '...'" class="input" />
      </div>
    </div>

    <div class="card">
      <DataTable :columns="columns" :rows="filteredRows" @row-click="(r) => $emit('row-click', r)" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import DataTable from '@/components/DataTable.vue'

const props = defineProps({
  title: String, singular: String, columns: Array, rows: { type: Array, default: () => [] }
})

defineEmits(['create', 'row-click'])

const search = ref('')

const filteredRows = computed(() => {
  if (!search.value) return props.rows
  const q = search.value.toLowerCase()
  return props.rows.filter((r) =>
    Object.values(r).some((v) => v != null && String(v).toLowerCase().includes(q))
  )
})
</script>
