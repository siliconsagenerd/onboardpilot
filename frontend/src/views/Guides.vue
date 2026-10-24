<template>
  <div>
    <div class="flex items-end justify-between mb-6 gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">{{ t('guides') }}</h1>
        <p class="text-sm text-muted mt-1">{{ filtered.length }} {{ t('guides').toLowerCase() }}</p>
      </div>
      <input v-model="q" :placeholder="t('search')"
        class="rounded-md border border-line bg-surface px-3 py-1.5 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none w-full sm:w-64" />
    </div>

    <div v-if="loading" class="card p-6 text-muted">{{ t('loading') }}</div>
    <div v-else-if="!filtered.length" class="card p-8 text-center text-muted">{{ t('no_guides') }}</div>
    <div v-else class="grid md:grid-cols-2 gap-4">
      <article v-for="g in filtered" :key="g.id" class="card p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <span class="text-xs uppercase tracking-wider text-muted font-mono">{{ g.category }}</span>
          </div>
          <h2 class="text-lg font-semibold tracking-tight text-ink mb-3">{{ lang==='de'?g.title_de:g.title_en }}</h2>
          <div class="text-sm text-ink-soft whitespace-pre-wrap leading-relaxed">{{ lang==='de'?g.content_de:g.content_en }}</div>
        </div>
      </article>
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
