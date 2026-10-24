<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-4 flex-wrap pb-2 border-b border-white/[0.08]">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-[#f7f8f8]">{{ t('guides') }}</h1>
        <p class="text-xs text-[#8a8f98] mt-0.5 font-mono">{{ filtered.length }} {{ t('guides').toLowerCase() }} available</p>
      </div>
      <div class="relative">
        <input v-model="q" :placeholder="t('search')"
          class="linear-input text-xs px-3 py-1.5 w-full sm:w-64 placeholder-[#62666d]" />
        <span class="absolute right-2.5 top-1.5 kbd">/</span>
      </div>
    </div>

    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[#8a8f98]">{{ t('loading') }}</div>
    <div v-else-if="!filtered.length" class="panel p-12 text-center text-xs font-mono text-[#62666d]">{{ t('no_guides') }}</div>
    <div v-else class="grid md:grid-cols-2 gap-3">
      <article v-for="g in filtered" :key="g.id" class="panel p-4 flex flex-col justify-between hover:border-white/[0.16] transition-colors group">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-white/[0.04]">
            <span class="text-[10px] uppercase tracking-wider text-[#8a8f98] font-mono">{{ g.category }}</span>
            <span class="text-[#62666d] font-mono text-[10px]">#{{ g.id.slice(0, 4) }}</span>
          </div>
          <h2 class="text-sm font-semibold tracking-tight text-[#f7f8f8] group-hover:text-white transition-colors mb-2">
            {{ lang==='de'?g.title_de:g.title_en }}
          </h2>
          <div class="text-xs text-[#8a8f98] whitespace-pre-wrap leading-relaxed">
            {{ lang==='de'?g.content_de:g.content_en }}
          </div>
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
  const query = q.value.toLowerCase()
  const title = (lang.value === 'de' ? g.title_de : g.title_en).toLowerCase()
  const content = (lang.value === 'de' ? g.content_de : g.content_en).toLowerCase()
  return title.includes(query) || content.includes(query) || g.category.toLowerCase().includes(query)
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
