<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-4 flex-wrap pb-2 border-b border-white/[0.08]">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-[#f7f8f8]">{{ t('public_demo') }}</h1>
        <p class="text-xs text-[#8a8f98] mt-0.5 font-mono">{{ t('public_demo_desc') }}</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="status-badge bg-[#5e6ad2]/10 text-[#5e6ad2] border border-[#5e6ad2]/20">READ-ONLY TELEMETRY</span>
      </div>
    </div>

    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[#8a8f98]">{{ t('loading') }}</div>
    <div v-else-if="error" class="panel p-4 text-xs font-mono text-[#f43f5e] bg-[#f43f5e]/10 border-[#f43f5e]/30" role="alert">{{ error }}</div>
    <div v-else class="space-y-4">
      <!-- Public Hero Panel -->
      <div class="panel p-5">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[#62666d] font-mono text-xs">#{{ data?.case?.id?.slice(0, 8) }}</span>
              <h2 class="text-lg font-semibold text-[#f7f8f8]">{{ data?.case?.employee_name }}</h2>
            </div>
            <p class="text-xs text-[#8a8f98] mt-1 font-mono">
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
          <div class="flex items-center justify-between pb-3 mb-3 border-b border-white/[0.08]">
            <h3 class="text-xs font-semibold uppercase tracking-wider font-mono text-[#8a8f98]">{{ t('checklist') }}</h3>
            <span class="kbd">{{ data?.checklist?.length ?? 0 }}</span>
          </div>
          <div class="space-y-2">
            <div v-for="it in data?.checklist" :key="it.id"
              class="p-2.5 rounded border border-white/[0.04] bg-white/[0.02] flex items-center justify-between gap-2 text-xs">
              <span class="font-medium text-[#f7f8f8]">{{ lang==='de'?it.title_de:it.title_en }}</span>
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
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-white/[0.08]">
              <h3 class="text-xs font-semibold uppercase tracking-wider font-mono text-[#8a8f98]">{{ t('hardware') }}</h3>
              <span class="kbd">{{ data?.hardware?.length ?? 0 }}</span>
            </div>
            <div class="space-y-2">
              <div v-for="h in data?.hardware" :key="h.id"
                class="p-2.5 rounded border border-white/[0.04] bg-white/[0.02] flex items-center justify-between gap-2 text-xs">
                <div>
                  <div class="font-medium text-[#f7f8f8]">{{ h.asset_type }}</div>
                  <div class="text-[10px] text-[#62666d] font-mono">{{ h.brand_model || '-' }}</div>
                </div>
                <span class="status-badge"
                  :class="h.handover_date ? 'bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20' : 'bg-white/[0.04] text-[#8a8f98] border border-white/[0.08]'">
                  {{ h.handover_date ? t('handed_over') : t('pending') }}
                </span>
              </div>
            </div>
          </section>

          <section class="panel p-4">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-white/[0.08]">
              <h3 class="text-xs font-semibold uppercase tracking-wider font-mono text-[#8a8f98]">{{ t('access') }}</h3>
              <span class="kbd">{{ data?.access?.length ?? 0 }}</span>
            </div>
            <div class="space-y-2">
              <div v-for="a in data?.access" :key="a.id"
                class="p-2.5 rounded border border-white/[0.04] bg-white/[0.02] flex items-center justify-between gap-2 text-xs">
                <span class="font-medium text-[#f7f8f8]">{{ a.access_type }}</span>
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
  if (s === 'completed' || s === 'verified') return 'bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/20'
  if (s === 'in_progress' || s === 'provisioned') return 'bg-[#5e6ad2]/10 text-[#5e6ad2] border border-[#5e6ad2]/20'
  return 'bg-white/[0.04] text-[#8a8f98] border border-white/[0.08]'
}

function statusDot(s: string) {
  if (s === 'completed' || s === 'verified') return 'bg-[#10b981]'
  if (s === 'in_progress' || s === 'provisioned') return 'bg-[#5e6ad2]'
  return 'bg-[#8a8f98]'
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
