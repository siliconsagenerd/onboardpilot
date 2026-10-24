<template>
  <div class="space-y-4">
    <!-- Header with quick controls -->
    <div class="flex items-center justify-between gap-4 flex-wrap pb-2 border-b border-white/[0.08]">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-[#f7f8f8]">{{ t('cases') }}</h1>
        <p class="text-xs text-[#8a8f98] mt-0.5 font-mono">{{ filtered.length }} {{ t('cases').toLowerCase() }} total</p>
      </div>
      <div class="flex items-center gap-2 flex-wrap">
        <div class="relative">
          <input v-model="q" :placeholder="t('search')"
            class="linear-input text-xs px-3 py-1.5 w-48 sm:w-64 placeholder-[#62666d]" />
          <span class="absolute right-2.5 top-1.5 kbd">/</span>
        </div>
        <select v-model="status"
          class="linear-input text-xs px-2.5 py-1.5 font-mono">
          <option value="">{{ t('all') }}</option>
          <option value="not_started">{{ t('not_started') }}</option>
          <option value="in_progress">{{ t('in_progress') }}</option>
          <option value="completed">{{ t('completed') }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[#8a8f98]">{{ t('loading') }}</div>
    <div v-else-if="error" class="panel p-4 text-xs font-mono text-[#f43f5e] bg-[#f43f5e]/10 border-[#f43f5e]/30" role="alert">{{ error }}</div>
    <div v-else-if="!filtered.length" class="panel p-12 text-center text-xs font-mono text-[#62666d]">{{ t('no_cases') }}</div>
    <div v-else class="panel overflow-hidden border border-white/[0.08]">
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="bg-[#121316] border-b border-white/[0.08] text-left text-[11px] font-mono text-[#8a8f98]">
            <tr>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('employee') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('role') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('department') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('start_date') }}</th>
              <th scope="col" class="py-2.5 px-4 font-medium">{{ t('status') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/[0.04]">
            <tr v-for="c in filtered" :key="c.id"
              class="hover:bg-white/[0.02] cursor-pointer transition-colors group"
              @click="go(c.id)" tabindex="0" @keydown.enter="go(c.id)">
              <td class="py-3 px-4 font-medium text-[#f7f8f8]">
                <div class="flex items-center gap-2">
                  <span class="text-[#62666d] font-mono text-[10px] group-hover:text-[#5e6ad2] transition-colors">#{{ c.id.slice(0, 4) }}</span>
                  <span class="group-hover:text-white transition-colors">{{ c.employee_name }}</span>
                </div>
              </td>
              <td class="py-3 px-4 text-[#8a8f98]">{{ c.role_template }}</td>
              <td class="py-3 px-4 text-[#8a8f98]">{{ c.department }}</td>
              <td class="py-3 px-4 font-mono text-[11px] text-[#62666d]">{{ c.start_date }}</td>
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
  if (s === 'completed') return 'bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20'
  if (s === 'in_progress') return 'bg-[#5e6ad2]/10 text-[#5e6ad2] border border-[#5e6ad2]/20'
  return 'bg-white/[0.04] text-[#8a8f98] border border-white/[0.08]'
}

function statusDot(s: string) {
  if (s === 'completed') return 'bg-[#10b981]'
  if (s === 'in_progress') return 'bg-[#5e6ad2]'
  return 'bg-[#8a8f98]'
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
