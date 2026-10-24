<template>
  <div>
    <div class="flex items-end justify-between mb-6 gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">{{ t('cases') }}</h1>
        <p class="text-sm text-muted mt-1">{{ filtered.length }} {{ t('cases').toLowerCase() }}</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <input v-model="q" :placeholder="t('search')"
          class="rounded-md border border-line bg-surface px-3 py-1.5 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none w-48 sm:w-64" />
        <select v-model="status"
          class="rounded-md border border-line bg-surface px-3 py-1.5 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none">
          <option value="">{{ t('all') }}</option>
          <option value="not_started">{{ t('not_started') }}</option>
          <option value="in_progress">{{ t('in_progress') }}</option>
          <option value="completed">{{ t('completed') }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="card p-6 text-muted">{{ t('loading') }}</div>
    <div v-else-if="error" class="card p-6 text-danger" role="alert">{{ error }}</div>
    <div v-else-if="!filtered.length" class="card p-8 text-center text-muted">{{ t('no_cases') }}</div>
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-2 border-b border-line text-left text-xs uppercase tracking-wider text-muted">
            <tr>
              <th scope="col" class="p-3.5 font-medium">{{ t('employee') }}</th>
              <th scope="col" class="p-3.5 font-medium">{{ t('role') }}</th>
              <th scope="col" class="p-3.5 font-medium">{{ t('department') }}</th>
              <th scope="col" class="p-3.5 font-medium">{{ t('start_date') }}</th>
              <th scope="col" class="p-3.5 font-medium">{{ t('status') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-line">
            <tr v-for="c in filtered" :key="c.id"
              class="hover:bg-surface-2 cursor-pointer transition-colors"
              @click="go(c.id)" tabindex="0" @keydown.enter="go(c.id)">
              <td class="p-3.5 font-medium text-ink">
                <span class="text-accent hover:underline">{{ c.employee_name }}</span>
              </td>
              <td class="p-3.5 text-ink-soft">{{ c.role_template }}</td>
              <td class="p-3.5 text-ink-soft">{{ c.department }}</td>
              <td class="p-3.5 mono text-xs text-muted">{{ c.start_date }}</td>
              <td class="p-3.5">
                <span class="text-xs px-2.5 py-1 rounded-md font-medium border"
                  :class="statusBadge(c.status)">
                  {{ t(c.status) || c.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useI18n } from 'vue-i18n'
import type { Case } from '../types'

const { t } = useI18n()
const router = useRouter()
const cases = ref<Case[]>([])
const loading = ref(true)
const error = ref('')
const q = ref('')
const status = ref('')

const filtered = computed(() => cases.value.filter(c => {
  if (status.value && c.status !== status.value) return false
  if (q.value && !c.employee_name.toLowerCase().includes(q.value.toLowerCase())) return false
  return true
}))

function statusBadge(s: string) {
  if (s === 'completed') return 'bg-accent-soft text-accent-ink border-accent/20'
  if (s === 'in_progress') return 'bg-info-soft text-info border-info/20'
  return 'bg-surface-2 text-ink-soft border-line'
}

onMounted(async () => {
  try {
    const r = await api.get('/api/cases')
    cases.value = r.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('failed_load')
  } finally {
    loading.value = false
  }
})

function go(id: string) { router.push(`/cases/${id}`) }
</script>
