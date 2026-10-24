<template>
  <div class="space-y-6">
    <!-- Header with status pulse -->
    <div class="flex items-center justify-between gap-4 flex-wrap pb-2 border-b border-white/[0.08]">
      <div>
        <div class="flex items-center gap-2">
          <span class="inline-block h-2 w-2 rounded-full bg-[#10b981] animate-pulse"></span>
          <h1 class="text-xl font-semibold tracking-tight text-[#f7f8f8]">{{ t('dashboard') }}</h1>
          <span class="kbd ml-2">SYSTEM ACTIVE</span>
        </div>
        <p class="text-xs text-[#8a8f98] mt-1">{{ t('app') }} · Live Telemetry</p>
      </div>
      <div class="flex items-center gap-2">
        <router-link to="/cases" class="panel px-3 py-1.5 text-xs font-medium text-[#f7f8f8] hover:border-white/[0.2] transition-colors flex items-center gap-1.5">
          <span>{{ t('cases') }}</span>
          <span class="text-[#8a8f98] font-mono">→</span>
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[#8a8f98]">{{ t('loading') }}</div>
    <div v-else-if="error" class="panel p-4 text-xs font-mono text-[#f43f5e] bg-[#f43f5e]/10 border-[#f43f5e]/30" role="alert">{{ error }}</div>

    <template v-else>
      <!-- Metric Cards: High-density, hairline borders -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="panel-card p-4 relative overflow-hidden group">
          <div class="text-[11px] font-mono text-[#8a8f98] uppercase tracking-wider flex items-center justify-between">
            <span>{{ t('total_cases') }}</span>
            <span class="text-white/[0.2] group-hover:text-white/[0.4] transition-colors font-mono">#01</span>
          </div>
          <div class="mt-2 text-3xl font-semibold font-mono tracking-tight text-[#f7f8f8]">{{ summary?.total_cases ?? 0 }}</div>
          <div class="mt-2 text-[11px] text-[#62666d]">active records registered</div>
        </div>

        <div class="panel-card p-4 relative overflow-hidden group">
          <div class="text-[11px] font-mono text-[#8a8f98] uppercase tracking-wider flex items-center justify-between">
            <span>{{ t('incomplete') }}</span>
            <span class="text-white/[0.2] group-hover:text-white/[0.4] transition-colors font-mono">#02</span>
          </div>
          <div class="mt-2 text-3xl font-semibold font-mono tracking-tight text-[#f7f8f8]">{{ summary?.incomplete_cases ?? 0 }}</div>
          <div class="mt-2 text-[11px] text-[#0ea5e9]">in flight onboarding</div>
        </div>

        <div class="panel-card p-4 relative overflow-hidden group">
          <div class="text-[11px] font-mono text-[#8a8f98] uppercase tracking-wider flex items-center justify-between">
            <span>{{ t('overdue_items') }}</span>
            <span class="text-[#f43f5e]/40 font-mono">#03</span>
          </div>
          <div class="mt-2 text-3xl font-semibold font-mono tracking-tight" :class="(summary?.overdue_items_count ?? 0) > 0 ? 'text-[#f43f5e]' : 'text-[#8a8f98]'">
            {{ summary?.overdue_items_count ?? 0 }}
          </div>
          <div class="mt-2 text-[11px] text-[#62666d]">action required</div>
        </div>

        <div class="panel-card p-4 relative overflow-hidden group">
          <div class="text-[11px] font-mono text-[#8a8f98] uppercase tracking-wider flex items-center justify-between">
            <span>{{ t('blocked_access') }}</span>
            <span class="text-[#f59e0b]/40 font-mono">#04</span>
          </div>
          <div class="mt-2 text-3xl font-semibold font-mono tracking-tight" :class="(summary?.blocked_access_count ?? 0) > 0 ? 'text-[#f59e0b]' : 'text-[#8a8f98]'">
            {{ summary?.blocked_access_count ?? 0 }}
          </div>
          <div class="mt-2 text-[11px] text-[#62666d]">dependency gate</div>
        </div>
      </div>

      <!-- Linear split view -->
      <div class="grid md:grid-cols-2 gap-4">
        <!-- Upcoming Starters -->
        <section class="panel p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between pb-3 mb-2 border-b border-white/[0.08]">
              <h2 class="text-xs font-semibold uppercase tracking-wider font-mono text-[#8a8f98]">{{ t('monday_starters') }}</h2>
              <span class="kbd">{{ summary?.upcoming_starters?.length ?? 0 }}</span>
            </div>
            <div v-if="!summary?.upcoming_starters?.length" class="py-6 text-center text-xs text-[#62666d] font-mono">{{ t('none') }}</div>
            <ul v-else class="divide-y divide-white/[0.04]">
              <li v-for="s in summary.upcoming_starters" :key="s.id" class="py-2.5 flex items-center justify-between text-xs hover:bg-white/[0.02] px-1 rounded transition-colors">
                <div class="flex items-center gap-2">
                  <div class="h-1.5 w-1.5 rounded-full bg-[#5e6ad2]"></div>
                  <span class="font-medium text-[#f7f8f8]">{{ s.employee_name }}</span>
                </div>
                <span class="font-mono text-[#8a8f98] text-[11px]">{{ s.start_date }}</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- Incomplete Cases -->
        <section class="panel p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between pb-3 mb-2 border-b border-white/[0.08]">
              <h2 class="text-xs font-semibold uppercase tracking-wider font-mono text-[#8a8f98]">{{ t('incomplete_cases') }}</h2>
              <span class="kbd">{{ incomplete.length }}</span>
            </div>
            <div v-if="!incomplete.length" class="py-6 text-center text-xs text-[#62666d] font-mono">{{ t('none') }}</div>
            <ul v-else class="divide-y divide-white/[0.04]">
              <li v-for="c in incomplete" :key="c.id" class="py-2.5 flex items-center justify-between text-xs hover:bg-white/[0.02] px-1 rounded transition-colors">
                <router-link :to="`/cases/${c.id}`" class="text-[#f7f8f8] hover:text-[#5e6ad2] font-medium flex items-center gap-2 transition-colors">
                  <span class="text-[#62666d] font-mono text-[10px]">#{{ c.id.slice(0, 4) }}</span>
                  <span>{{ c.employee_name }}</span>
                </router-link>
                <span class="status-badge bg-white/[0.04] text-[#8a8f98] border border-white/[0.08]">
                  {{ t(c.status) || c.status }}
                </span>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api/client'
import { useI18n } from 'vue-i18n'
import type { DashboardSummary, Case } from '../types'

const { t } = useI18n()
const summary = ref<DashboardSummary | null>(null)
const incomplete = ref<Case[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const r = await api.get('/api/dashboard/summary')
    summary.value = r.data
    const cases = await api.get('/api/cases')
    incomplete.value = (cases.data as Case[]).filter(c => c.status !== 'completed')
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('failed_load')
  } finally {
    loading.value = false
  }
})
</script>
