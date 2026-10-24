<template>
  <div>
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <h1 class="text-2xl font-bold">{{ t('cases') }}</h1>
      <div class="flex gap-2">
        <input v-model="q" :placeholder="t('search')" class="border rounded px-3 py-2" />
        <select v-model="status" class="border rounded px-3 py-2">
          <option value="">{{ t('all') }}</option>
          <option value="not_started">{{ t('not_started') }}</option>
          <option value="in_progress">{{ t('in_progress') }}</option>
          <option value="completed">{{ t('completed') }}</option>
        </select>
      </div>
    </div>
    <div v-if="loading" class="text-slate-500">Loading...</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else-if="!filtered.length" class="text-slate-400">No cases</div>
    <div v-else class="bg-white rounded shadow overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-100">
          <tr>
            <th class="text-left p-3">{{ t('employee') }}</th>
            <th class="text-left p-3">{{ t('role') }}</th>
            <th class="text-left p-3">{{ t('department') }}</th>
            <th class="text-left p-3">{{ t('start_date') }}</th>
            <th class="text-left p-3">{{ t('status') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in filtered" :key="c.id" class="border-t hover:bg-slate-50 cursor-pointer" @click="go(c.id)">
            <td class="p-3 text-blue-600">{{ c.employee_name }}</td>
            <td class="p-3">{{ c.role_template }}</td>
            <td class="p-3">{{ c.department }}</td>
            <td class="p-3">{{ c.start_date }}</td>
            <td class="p-3"><span class="px-2 py-1 rounded text-xs bg-slate-100">{{ t(c.status) || c.status }}</span></td>
          </tr>
        </tbody>
      </table>
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

onMounted(async () => {
  try {
    const r = await api.get('/api/cases')
    cases.value = r.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed'
  } finally {
    loading.value = false
  }
})

function go(id: string) { router.push(`/cases/${id}`) }
</script>
