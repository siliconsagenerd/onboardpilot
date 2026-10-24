<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-4 flex-wrap pb-2 border-b border-[var(--color-line)]">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-[var(--color-ink)]">{{ t('public_demo') }}</h1>
        <p class="text-xs text-[var(--color-ink-soft)] mt-0.5 font-mono">{{ t('public_demo_desc') }}</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="status-badge bg-[var(--color-accent-soft)] text-[var(--color-accent)] border border-[var(--color-accent)]/20">READ-ONLY TELEMETRY</span>
      </div>
    </div>

    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[var(--color-ink-soft)]">{{ t('loading') }}</div>
    <div v-else-if="error" class="panel p-4 text-xs font-mono text-[var(--color-rose)] bg-[var(--color-rose-soft)] border-[var(--color-rose)]/30" role="alert">{{ error }}</div>
    <div v-else class="space-y-4">
      <!-- Public Hero Panel -->
      <div class="panel p-5">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[var(--color-muted)] font-mono text-xs">#{{ data?.case?.id?.slice(0, 8) }}</span>
              <h2 class="text-lg font-semibold text-[var(--color-ink)]">{{ data?.case?.employee_name }}</h2>
            </div>
            <p class="text-xs text-[var(--color-ink-soft)] mt-1 font-mono">
              {{ data?.case?.role_template }} · {{ data?.case?.department }} · {{ data?.case?.start_date }}
            </p>
          </div>
          <span class="status-badge" :class="statusBadge(data?.case?.status || '')">
            <span class="h-1.5 w-1.5 rounded-full" :class="statusDot(data?.case?.status || '')"></span>
            {{ t(data?.case?.status || '') || data?.case?.status }}
          </span>
        </div>
      </div>

      <!-- Split Sections -->
      <div class="grid md:grid-cols-2 gap-4">
        <!-- Checklist items -->
        <section class="panel p-4">
          <div class="flex items-center justify-between pb-3 mb-3 border-b border-[var(--color-line)]">
            <h3 class="text-xs font-semibold uppercase tracking-wider font-mono text-[var(--color-ink-soft)]">{{ t('checklist') }}</h3>
            <span class="kbd">{{ data?.checklist?.length ?? 0 }}</span>
          </div>
          <div class="space-y-2">
            <div v-for="it in data?.checklist" :key="it.id"
              class="p-2.5 rounded border border-[var(--color-line-subtle)] bg-[var(--color-canvas-subtle)] flex items-center justify-between gap-2 text-xs">
              <span class="font-medium text-[var(--color-ink)]">{{ lang==='de'?it.title_de:it.title_en }}</span>
              <span class="status-badge" :class="statusBadge(it.status)">
                <span class="h-1 w-1 rounded-full" :class="statusDot(it.status)"></span>
                {{ t(it.status) || it.status }}
              </span>
            </div>
          </div>
        </section>

        <!-- Hardware & Access -->
        <div class="space-y-4">
          <section class="panel p-4">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-[var(--color-line)]">
              <h3 class="text-xs font-semibold uppercase tracking-wider font-mono text-[var(--color-ink-soft)]">{{ t('hardware') }}</h3>
              <span class="kbd">{{ data?.hardware?.length ?? 0 }}</span>
            </div>
            <div class="space-y-2">
              <div v-for="h in data?.hardware" :key="h.id"
                class="p-2.5 rounded border border-[var(--color-line-subtle)] bg-[var(--color-canvas-subtle)] flex items-center justify-between gap-2 text-xs">
                <div>
                  <div class="font-medium text-[var(--color-ink)]">{{ h.asset_type }}</div>
                  <div class="text-[10px] text-[var(--color-muted)] font-mono">{{ h.brand_model || '-' }}</div>
                </div>
                <span class="status-badge"
                  :class="h.handover_date ? 'bg-[var(--color-emerald-soft)] text-[var(--color-emerald)] border border-[var(--color-emerald)]/30' : 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] border border-[var(--color-line)]'">
                  {{ h.handover_date ? t('handed_over') : t('pending') }}
                </span>
              </div>
            </div>
          </section>

          <section class="panel p-4">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-[var(--color-line)]">
              <h3 class="text-xs font-semibold uppercase tracking-wider font-mono text-[var(--color-ink-soft)]">{{ t('access') }}</h3>
              <span class="kbd">{{ data?.access?.length ?? 0 }}</span>
            </div>
            <div class="space-y-2">
              <div v-for="a in data?.access" :key="a.id"
                class="p-2.5 rounded border border-[var(--color-line-subtle)] bg-[var(--color-canvas-subtle)] flex items-center justify-between gap-2 text-xs">
                <span class="font-medium text-[var(--color-ink)]">{{ a.access_type }}</span>
                <span class="status-badge" :class="statusBadge(a.status)">
                  <span class="h-1 w-1 rounded-full" :class="statusDot(a.status)"></span>
                  {{ t(a.status) || a.status }}
                </span>
              </div>
            </div>
          </section>
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

function statusBadge(s: string) {
  if (s === 'completed' || s === 'verified') return 'bg-[var(--color-emerald-soft)] text-[var(--color-emerald)] border border-[var(--color-emerald)]/30'
  if (s === 'in_progress' || s === 'provisioned') return 'bg-[var(--color-accent-soft)] text-[var(--color-accent)] border border-[var(--color-accent)]/30'
  return 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] border border-[var(--color-line)]'
}

function statusDot(s: string) {
  if (s === 'completed' || s === 'verified') return 'bg-[var(--color-emerald)]'
  if (s === 'in_progress' || s === 'provisioned') return 'bg-[var(--color-accent)]'
  return 'bg-[var(--color-muted)]'
}

onMounted(async () => {
  try {
    const r = await api.get('/api/public/demo')
    data.value = r.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('failed_load')
  } finally {
    loading.value = false
  }
})
</script>
