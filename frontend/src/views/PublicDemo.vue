<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-semibold tracking-tight">{{ t('public_demo') }}</h1>
      <p class="text-sm text-muted mt-1">{{ t('public_demo_desc') }}</p>
    </div>

    <div v-if="loading" class="card p-6 text-muted">{{ t('loading') }}</div>
    <div v-else-if="error" class="card p-6 text-danger" role="alert">{{ error }}</div>
    <div v-else class="space-y-6">
      <div class="card p-5">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h2 class="text-xl font-semibold text-ink">{{ data?.case?.employee_name }}</h2>
            <p class="text-sm text-muted mt-1">
              {{ data?.case?.role_template }} · {{ data?.case?.department }} · <span class="mono">{{ data?.case?.start_date }}</span>
            </p>
          </div>
          <span class="text-xs px-2.5 py-1 rounded-md font-medium border bg-surface-2 text-ink-soft border-line">
            {{ t(data?.case?.status) || data?.case?.status }}
          </span>
        </div>
      </div>

      <div class="grid md:grid-cols-2 gap-6">
        <section class="card p-5">
          <h3 class="text-sm font-semibold tracking-tight uppercase text-muted mb-3 font-mono">{{ t('checklist') }}</h3>
          <div class="space-y-2">
            <div v-for="it in data?.checklist" :key="it.id"
              class="p-3 rounded-md border border-line bg-surface-2 flex items-center justify-between gap-2 text-sm">
              <span class="font-medium text-ink">{{ lang==='de'?it.title_de:it.title_en }}</span>
              <span class="text-xs px-2 py-0.5 rounded border mono"
                :class="it.status==='completed'?'bg-accent-soft text-accent-ink border-accent/20':'bg-surface text-muted border-line'">
                {{ t(it.status) || it.status }}
              </span>
            </div>
          </div>
        </section>

        <section class="card p-5">
          <h3 class="text-sm font-semibold tracking-tight uppercase text-muted mb-3 font-mono">{{ t('hardware') }}</h3>
          <div class="space-y-2">
            <div v-for="h in data?.hardware" :key="h.id"
              class="p-3 rounded-md border border-line bg-surface-2 flex items-center justify-between gap-2 text-sm">
              <div>
                <span class="font-medium text-ink">{{ h.asset_type }}</span>
                <span class="text-xs text-muted block">{{ h.brand_model }}</span>
              </div>
              <span class="text-xs mono" :class="h.handover_date ? 'text-accent font-medium' : 'text-muted'">
                {{ h.handover_date ? (t('handover_date') + ': ' + h.handover_date) : t('not_handed_over') }}
              </span>
            </div>
          </div>
        </section>

        <section class="card p-5">
          <h3 class="text-sm font-semibold tracking-tight uppercase text-muted mb-3 font-mono">{{ t('access') }}</h3>
          <div class="space-y-2">
            <div v-for="a in data?.access" :key="a.id"
              class="p-3 rounded-md border border-line bg-surface-2 flex items-center justify-between gap-2 text-sm">
              <span class="font-medium text-ink">{{ a.access_type }}</span>
              <span class="text-xs px-2 py-0.5 rounded border mono bg-surface text-ink-soft border-line">
                {{ t(a.status) || a.status }}
              </span>
            </div>
          </div>
        </section>

        <section class="card p-5">
          <h3 class="text-sm font-semibold tracking-tight uppercase text-muted mb-3 font-mono">{{ t('guides') }}</h3>
          <div class="space-y-2">
            <div v-for="g in data?.guides" :key="g.id"
              class="p-3 rounded-md border border-line bg-surface-2 text-sm">
              <div class="font-medium text-ink">{{ lang==='de'?g.title_de:g.title_en }}</div>
              <div class="text-xs text-muted mono mt-0.5">{{ g.category }}</div>
            </div>
          </div>
        </section>
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
    error.value = e.response?.data?.detail || t('failed_load')
  } finally {
    loading.value = false
  }
})
</script>
