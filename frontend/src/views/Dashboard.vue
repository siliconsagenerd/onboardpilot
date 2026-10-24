<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">{{ t('dashboard') }}</h1>
    <div v-if="loading" class="text-slate-500">Loading...</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white p-4 rounded shadow">
          <div class="text-sm text-slate-500">Total cases</div>
          <div class="text-2xl font-bold">{{ summary?.total_cases }}</div>
        </div>
        <div class="bg-white p-4 rounded shadow">
          <div class="text-sm text-slate-500">Incomplete</div>
          <div class="text-2xl font-bold">{{ summary?.incomplete_cases }}</div>
        </div>
        <div class="bg-white p-4 rounded shadow">
          <div class="text-sm text-slate-500">Overdue items</div>
          <div class="text-2xl font-bold text-red-600">{{ summary?.overdue_items_count }}</div>
        </div>
        <div class="bg-white p-4 rounded shadow">
          <div class="text-sm text-slate-500">Blocked access</div>
          <div class="text-2xl font-bold text-amber-600">{{ summary?.blocked_access_count }}</div>
        </div>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <div class="bg-white p-4 rounded shadow">
          <h2 class="font-semibold mb-3">Monday starters</h2>
          <div v-if="!summary?.upcoming_starters?.length" class="text-slate-400 text-sm">None</div>
          <ul v-else class="space-y-2">
            <li v-for="s in summary.upcoming_starters" :key="s.id" class="text-sm">
              {{ s.employee_name }} — {{ s.start_date }}
            </li>
          </ul>
        </div>
        <div class="bg-white p-4 rounded shadow">
          <h2 class="font-semibold mb-3">Incomplete cases</h2>
          <div v-if="!incomplete.length" class="text-slate-400 text-sm">None</div>
          <ul v-else class="space-y-2">
            <li v-for="c in incomplete" :key="c.id" class="text-sm flex justify-between">
              <router-link :to="`/cases/${c.id}`" class="text-blue-600">{{ c.employee_name }}</router-link>
              <span>{{ c.status }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
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
    error.value = e.response?.data?.detail || 'Failed to load'
  } finally {
    loading.value = false
  }
})
</script>
