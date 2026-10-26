<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-4 flex-wrap pb-4 border-b border-[var(--color-line)]">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-[var(--color-ink)] display-heading">{{ t('guides') }}</h1>
        <p class="text-xs text-[var(--color-ink-soft)] mt-0.5 font-mono">{{ filtered.length }} {{ t('guides').toLowerCase() }} available · searchable knowledge base · click a category to filter</p>
      </div>
      <div class="relative">
        <input v-model="q" :placeholder="t('search')"
          class="linear-input text-xs px-3 py-1.5 w-full sm:w-64 placeholder-[var(--color-muted)]" />
        <span class="absolute right-2.5 top-1.5 kbd">/</span>
      </div>
    </div>

    <div class="flex flex-wrap gap-2">
      <button v-for="cat in categories" :key="cat"
        @click="activeCat = activeCat===cat ? '' : cat"
        class="px-2.5 py-1 text-xs rounded border transition-colors"
        :class="activeCat===cat ? 'bg-[var(--color-accent-soft)] text-[var(--color-accent)] border-[var(--color-accent)]/30' : 'border-[var(--color-line)] text-[var(--color-ink-soft)] hover:border-[var(--color-line-strong)]'">
        {{ cat }}
      </button>
    </div>

    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[var(--color-ink-soft)]">{{ t('loading') }}</div>
    <div v-else-if="!filtered.length" class="panel p-12 text-center text-xs font-mono text-[var(--color-muted)]">{{ t('no_guides') }}</div>
    <div v-else class="grid md:grid-cols-2 gap-3">
      <article v-for="g in filtered" :key="g.id" class="panel p-4 flex flex-col justify-between hover:border-[var(--color-line-strong)] transition-colors group">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-[var(--color-line-subtle)]">
            <span class="text-[10px] uppercase tracking-wider text-[var(--color-ink-soft)] font-mono">{{ g.category }}</span>
            <span class="text-[var(--color-muted)] font-mono text-[10px]">#{{ g.id.slice(0, 4) }}</span>
          </div>
          <h2 class="text-sm font-semibold tracking-tight text-[var(--color-ink)] group-hover:text-[var(--color-accent)] transition-colors mb-2">
            {{ lang==='de'?g.title_de:g.title_en }}
          </h2>
          <div class="text-xs text-[var(--color-ink-soft)] whitespace-pre-wrap leading-relaxed">
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
const activeCat = ref('')

const categories = computed(() => [...new Set(guides.value.map(g => g.category))])

const filtered = computed(() => guides.value.filter(g => {
  if (activeCat.value && g.category !== activeCat.value) return false
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