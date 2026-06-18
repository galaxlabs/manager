<template>
  <ListPage title="Employees" singular="Employee" :columns="columns" :rows="employees" @create="() => {}" @row-click="() => {}" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListPage from '@/components/ListPage.vue'
import { getList } from '@/api/frappe'

const columns = [
  { key: 'employee_name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'mobile', label: 'Phone' },
  { key: 'department', label: 'Department' },
  { key: 'designation', label: 'Designation' },
  { key: 'status', label: 'Status' },
]
const employees = ref([])

onMounted(async () => {
  employees.value = await getList('Employee', {}, ['name', 'employee_name', 'email', 'mobile', 'department', 'designation', 'status'])
})
</script>
