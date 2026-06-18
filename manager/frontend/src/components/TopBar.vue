<template>
  <header class="top-bar">
    <div class="top-bar-left">
      <button class="mobile-toggle" @click="$emit('toggle-sidebar')">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <div class="breadcrumb">
        <span class="breadcrumb-item" v-for="(crumb, i) in breadcrumbs" :key="i">
          <span v-if="i > 0" class="separator">/</span>
          {{ crumb }}
        </span>
      </div>
    </div>
    <div class="top-bar-right">
      <div class="user-menu">
        <span class="user-name">{{ auth.fullName }}</span>
        <div class="avatar">{{ auth.fullName.charAt(0).toUpperCase() }}</div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({ sidebarCollapsed: Boolean })
defineEmits(['toggle-sidebar'])

const route = useRoute()
const auth = useAuthStore()

const breadcrumbs = computed(() => {
  const parts = route.path.split('/').filter(Boolean)
  return parts.map((p) => p.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()))
})
</script>
