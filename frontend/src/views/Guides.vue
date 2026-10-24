<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">{{ t('guides') }}</h1>
    <input v-model="q" :placeholder="t('search')" class="border rounded px-3 py-2 mb-4 w-full md:w-64" />
    <div v-if="loading" class="text-slate-500">Loading...</div>
    <div v-else-if="!filtered.length" class="text-slate-400">No guides</div>
    <div v-else class="grid md:grid-cols-2 gap-4">
      <div v-for="g in filtered" :key="g.id" class="bg-white p-4 rounded shadow">
        <h2 class="font-semibold">{{ lang==='de'?g.title_de:g.title_en }}</h2>
        <p class="text-xs text-slate-500 mb-2">{{ g.category }}</p>
        <div class="text-sm whitespace-pre-wrap">{{ lang==='de'?g.content_de:g.content_en }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '../api/client'
import type { Guide } from '../types'

const { t, locale } = useI18n()
const lang = computed(() => locale.value)
const guides = ref<Guide[]>([])
const loading = ref(true)
const q = ref('')

const filtered = computed(() => guides.value.filter(g => {
  if (!q.value) return true
  const title = lang.value === 'de' ? g.title_de : g.title_en
  return title.toLowerCase().includes(q.value.toLowerCase())
}))

onMounted(async () => {
  try {
    const r = await api.get('/api/guides')
    guides.value = r.data
  } finally {
    loading.value = false
  }
})
</script>
