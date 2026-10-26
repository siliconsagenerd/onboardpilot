<template>
  <div class="space-y-4">
    <!-- Header with quick controls -->
    <div class="flex items-center justify-between gap-4 flex-wrap pb-4 border-b border-[var(--color-line)]">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-[var(--color-ink)] display-heading">{{ t('cases') }}</h1>
        <p class="text-xs text-[var(--color-ink-soft)] mt-0.5 font-mono">{{ filtered.length }} {{ t('cases').toLowerCase() }} total</p>
      </div>
      <div class="flex items-center gap-2 flex-wrap">
        <div class="relative">
          <input v-model="q" :placeholder="t('search')"
            class="linear-input text-xs px-3 py-1.5 w-48 sm:w-64 placeholder-[var(--color-muted)]" />
          <span class="absolute right-2.5 top-1.5 kbd">/</span>
        </div>
        <select v-model="status"
          class="linear-input text-xs px-2.5 py-1.5 font-mono">
          <option value="">{{ t('all') }}</option>
          <option value="pre_boarding">{{ t('pre_boarding') }}</option>
          <option value="hardware_ready">{{ t('hardware_ready') }}</option>
          <option value="accounts_provisioned">{{ t('accounts_provisioned') }}</option>
          <option value="orientation_complete">{{ t('orientation_complete') }}</option>
          <option value="first_week_support">{{ t('first_week_support') }}</option>
          <option value="completed">{{ t('completed') }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[var(--color-ink-soft)]">{{ t('loading') }}</div>
    <div v-else-if="error" class="panel p-4 text-xs font-mono text-[var(--color-rose)] bg-[var(--color-rose-soft)] border-[var(--color-rose)]/30" role="alert">{{ error }}</div>
    <div v-else-if="!filtered.length" class="panel p-12 text-center text-xs font-mono text-[var(--color-muted)]">{{ t('no_cases') }}</div>
    <div v-else class="panel overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="bg-[var(--color-canvas-subtle)] border-b border-[var(--color-line)] text-left text-xs font-mono text-[var(--color-ink-soft)]">
            <tr>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('employee') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('role') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('department') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('start_date') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('status') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--color-line-subtle)]">
            <tr v-for="c in filtered" :key="c.id"
              class="hover:bg-[var(--color-canvas-subtle)] cursor-pointer transition-colors group"
              @click="go(c.id)" tabindex="0" @keydown.enter="go(c.id)">
              <td class="py-3 px-4 font-medium text-[var(--color-ink)]">
                <div class="flex items-center gap-2">
                  <span class="text-[var(--color-muted)] font-mono text-[10px] group-hover:text-[var(--color-accent)] transition-colors">#{{ c.id.slice(0, 4) }}</span>
                  <span class="group-hover:text-[var(--color-accent)] transition-colors">{{ c.employee_name }}</span>
                </div>
              </td>
              <td class="py-3 px-4 text-[var(--color-ink-soft)]">{{ c.role_template }}</td>
              <td class="py-3 px-4 text-[var(--color-ink-soft)]">{{ c.department }}</td>
              <td class="py-3 px-4 font-mono text-xs text-[var(--color-muted)]">{{ c.start_date }}</td>
              <td class="py-3 px-4">
                <span class="status-badge" :class="statusBadge(c.status)">
                  <span class="h-1.5 w-1.5 rounded-full" :class="statusDot(c.status)"></span>
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
  if (s === 'completed') return 'bg-[var(--color-emerald-soft)] text-[var(--color-emerald)] border border-[var(--color-emerald)]/30'
  if (s === 'in_progress') return 'bg-[var(--color-accent-soft)] text-[var(--color-accent)] border border-[var(--color-accent)]/30'
  return 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] border border-[var(--color-line)]'
}

function statusDot(s: string) {
  if (s === 'completed') return 'bg-[var(--color-emerald)]'
  if (s === 'in_progress') return 'bg-[var(--color-accent)]'
  return 'bg-[var(--color-muted)]'
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
