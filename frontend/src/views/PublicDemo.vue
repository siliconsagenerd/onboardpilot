<template>
  <div>
    <h1 class="text-2xl font-bold mb-2">{{ t('public_demo') }}</h1>
    <p class="text-slate-500 mb-4">Read-only synthetic demo case.</p>
    <div v-if="loading" class="text-slate-500">Loading...</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else>
      <div class="bg-white p-4 rounded shadow mb-4">
        <h2 class="font-semibold">{{ data.case.employee_name }}</h2>
        <p class="text-sm text-slate-500">{{ data.case.role_template }} · {{ data.case.department }} · {{ data.case.start_date }}</p>
      </div>
      <h3 class="font-semibold mb-2">Checklist</h3>
      <div class="space-y-2 mb-4">
        <div v-for="it in data.checklist" :key="it.id" class="bg-white p-3 rounded shadow flex justify-between">
          <span>{{ lang==='de'?it.title_de:it.title_en }}</span>
          <span class="text-xs px-2 py-1 rounded bg-slate-100">{{ it.status }}</span>
        </div>
      </div>
      <h3 class="font-semibold mb-2">Hardware</h3>
      <div class="space-y-2 mb-4">
        <div v-for="h in data.hardware" :key="h.id" class="bg-white p-3 rounded shadow text-sm">
          {{ h.asset_type }} — {{ h.brand_model }} ({{ h.handover_date || 'not handed over' }})
        </div>
      </div>
      <h3 class="font-semibold mb-2">Access</h3>
      <div class="space-y-2 mb-4">
        <div v-for="a in data.access" :key="a.id" class="bg-white p-3 rounded shadow text-sm">
          {{ a.access_type }} — {{ a.status }}
        </div>
      </div>
      <h3 class="font-semibold mb-2">Guides</h3>
      <div class="space-y-2">
        <div v-for="g in data.guides" :key="g.id" class="bg-white p-3 rounded shadow text-sm">
          {{ lang==='de'?g.title_de:g.title_en }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '../api/client'

const { t, locale } = useI18n()
const lang = computed(() => locale.value)
const data = ref<any>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const r = await api.get('/public/demo')
    data.value = r.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed'
  } finally {
    loading.value = false
  }
})
</script>
