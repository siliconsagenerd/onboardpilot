<template>
  <div>
    <div class="flex items-end justify-between mb-6 gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">{{ t('dashboard') }}</h1>
        <p class="text-sm text-muted mt-1">{{ t('app') }}</p>
      </div>
    </div>

    <div v-if="loading" class="card p-6 text-muted">{{ t('loading') }}</div>
    <div v-else-if="error" class="card p-6 text-danger" role="alert">{{ error }}</div>
    <template v-else>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="card p-5">
          <div class="text-xs text-muted uppercase tracking-wide">{{ t('total_cases') }}</div>
          <div class="mt-2 text-3xl font-semibold mono">{{ summary?.total_cases ?? 0 }}</div>
        </div>
        <div class="card p-5">
          <div class="text-xs text-muted uppercase tracking-wide">{{ t('incomplete') }}</div>
          <div class="mt-2 text-3xl font-semibold mono">{{ summary?.incomplete_cases ?? 0 }}</div>
        </div>
        <div class="card p-5">
          <div class="text-xs text-muted uppercase tracking-wide">{{ t('overdue_items') }}</div>
          <div class="mt-2 text-3xl font-semibold mono text-danger">{{ summary?.overdue_items_count ?? 0 }}</div>
        </div>
        <div class="card p-5">
          <div class="text-xs text-muted uppercase tracking-wide">{{ t('blocked_access') }}</div>
          <div class="mt-2 text-3xl font-semibold mono text-warn">{{ summary?.blocked_access_count ?? 0 }}</div>
        </div>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <section class="card p-5">
          <h2 class="font-semibold mb-3">{{ t('monday_starters') }}</h2>
          <div v-if="!summary?.upcoming_starters?.length" class="text-sm text-muted">{{ t('none') }}</div>
          <ul v-else class="divide-y divide-line">
            <li v-for="s in summary.upcoming_starters" :key="s.id" class="py-2 flex items-center justify-between text-sm">
              <span class="font-medium">{{ s.employee_name }}</span>
              <span class="text-muted mono text-xs">{{ s.start_date }}</span>
            </li>
          </ul>
        </section>
        <section class="card p-5">
          <h2 class="font-semibold mb-3">{{ t('incomplete_cases') }}</h2>
          <div v-if="!incomplete.length" class="text-sm text-muted">{{ t('none') }}</div>
          <ul v-else class="divide-y divide-line">
            <li v-for="c in incomplete" :key="c.id" class="py-2 flex items-center justify-between text-sm">
              <router-link :to="`/cases/${c.id}`" class="text-accent hover:underline font-medium">{{ c.employee_name }}</router-link>
              <span class="text-xs px-2 py-0.5 rounded bg-surface-2 border border-line text-ink-soft">{{ t(c.status) || c.status }}</span>
            </li>
          </ul>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api/client'
import { useI18n } from 'vue-i18n'
import type { DashboardSummary, Case } from '../types'

const { t } = useI18n()
const summary = ref<DashboardSummary | null>(null)
const incomplete = ref<Case[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const r = await api.get('/api/dashboard/summary')
    summary.value = r.data
    const cases = await api.get('/api/cases')
    incomplete.value = (cases.data as Case[]).filter(c => c.status !== 'completed')
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('failed_load')
  } finally {
    loading.value = false
  }
})
</script>
