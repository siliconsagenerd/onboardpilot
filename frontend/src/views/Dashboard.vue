<template>
  <div class="space-y-0">
    <!-- Hero editorial block -->
    <section class="dashboard-section relative overflow-hidden pb-12 pt-2">
      <div class="flex items-start justify-between gap-8 flex-wrap">
        <div class="flex-1 min-w-0">
          <p class="text-[10px] font-mono uppercase tracking-[0.3em] text-[var(--color-muted)] mb-3">IT Operations Console · Employee Onboarding</p>
          <h1 class="display-heading text-6xl sm:text-7xl lg:text-8xl text-[var(--color-ink)] leading-[0.9] mb-4">
            Onboard<br/><span class="text-[var(--color-accent)]">Pilot</span>
          </h1>
          <p class="text-sm text-[var(--color-ink-soft)] leading-relaxed max-w-xl">
            Starter registrieren, Onboarding-Schritte verfolgen, Hardware und Zugriffe verwalten,
            Übergabeprotokolle erstellen. Alles in einer Konsole.
          </p>
        </div>
        <div class="flex flex-col items-end gap-3 shrink-0">
          <div class="text-right">
            <div class="text-[10px] font-mono uppercase tracking-wider text-[var(--color-muted)]">Live Status</div>
            <div class="display-heading text-4xl text-[var(--color-accent)] mt-1">{{ summary?.total_cases ?? '—' }}</div>
            <div class="text-[10px] font-mono text-[var(--color-muted)]">total cases</div>
          </div>
          <button @click="refresh" :disabled="loading"
            class="px-4 py-2 text-xs font-medium rounded border border-[var(--color-line)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] transition-colors disabled:opacity-50">
            {{ loading ? '...' : '↻ Refresh' }}
          </button>
        </div>
      </div>
      <div class="mt-8 h-px bg-gradient-to-r from-[var(--color-accent)] via-[var(--color-line)] to-transparent"></div>
    </section>

    <div v-if="error" class="panel p-4 text-xs font-mono text-[var(--color-rose)] bg-[var(--color-rose-soft)] border-[var(--color-rose)]/30 mb-8" role="alert">{{ error }}</div>

    <!-- Bento KPI grid -->
    <section class="dashboard-section mb-12">
      <div class="flex items-baseline justify-between mb-4">
        <h2 class="display-heading text-2xl text-[var(--color-ink)]">Kennzahlen</h2>
        <span class="text-[10px] font-mono uppercase tracking-wider text-[var(--color-muted)]">Live · auto-refresh 30s</span>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button v-for="k in kpis" :key="k.label" @click="k.action"
          class="group text-left p-5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-line)] hover:border-[var(--color-accent-border)] transition-all duration-200 hover:-translate-y-0.5">
          <div class="text-[10px] font-mono uppercase tracking-wider text-[var(--color-muted)] mb-3">{{ k.label }}</div>
          <div class="display-heading text-4xl text-[var(--color-ink)] group-hover:text-[var(--color-accent)] transition-colors">{{ k.value }}</div>
          <div class="text-[10px] font-mono text-[var(--color-muted)] mt-2">{{ k.hint }}</div>
        </button>
      </div>
    </section>

    <!-- Two-column: workflow + safety -->
    <section class="dashboard-section grid grid-cols-1 lg:grid-cols-5 gap-8 mb-12">
      <div class="lg:col-span-3">
        <h2 class="display-heading text-2xl text-[var(--color-ink)] mb-4">Workflow</h2>
        <div class="space-y-0">
          <div v-for="(step, i) in workflow" :key="step" class="flex items-start gap-4 py-3 border-b border-[var(--color-line)] last:border-0">
            <span class="font-mono text-xs text-[var(--color-accent)] w-6 shrink-0 mt-0.5">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="text-sm text-[var(--color-ink)]">{{ step }}</span>
          </div>
        </div>
      </div>
      <div class="lg:col-span-2">
        <h2 class="display-heading text-2xl text-[var(--color-ink)] mb-4">Grenzen</h2>
        <div class="p-5 rounded-lg bg-[var(--color-accent-soft)] border border-[var(--color-accent-border)]">
          <p class="text-xs font-mono text-[var(--color-ink-soft)] leading-relaxed mb-3">
            OnboardPilot ist eine IT-Operations-Konsole für Onboarding-Workflows.
          </p>
          <ul class="space-y-1.5 text-xs font-mono text-[var(--color-ink-soft)]">
            <li v-for="b in boundaries" :key="b" class="flex gap-2">
              <span class="text-[var(--color-accent)]">—</span>{{ b }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Incomplete cases -->
    <section class="dashboard-section mb-12">
      <div class="flex items-baseline justify-between mb-4">
        <h2 class="display-heading text-2xl text-[var(--color-ink)]">Offene Fälle</h2>
        <router-link to="/cases" class="text-xs font-mono text-[var(--color-accent)] hover:underline">Alle anzeigen →</router-link>
      </div>
      <div v-if="!incomplete.length" class="p-8 text-center text-xs font-mono text-[var(--color-muted)] rounded-lg border border-[var(--color-line)]">
        Keine offenen Fälle.
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <router-link v-for="c in incomplete.slice(0, 6)" :key="c.id" :to="`/cases/${c.id}`"
          class="group flex items-center justify-between gap-3 p-4 rounded-lg bg-[var(--color-surface)] border border-[var(--color-line)] hover:border-[var(--color-accent-border)] transition-all">
          <div class="min-w-0">
            <div class="text-sm text-[var(--color-ink)] group-hover:text-[var(--color-accent)] transition-colors truncate">{{ c.employee_name }}</div>
            <div class="text-[10px] font-mono text-[var(--color-muted)] mt-0.5">{{ c.role_template }} · {{ c.department }}</div>
          </div>
          <span class="status-badge shrink-0" :class="statusBadge(c.status)">{{ t(c.status) || c.status }}</span>
        </router-link>
      </div>
    </section>

    <!-- Capabilities bento -->
    <section class="dashboard-section mb-12">
      <h2 class="display-heading text-2xl text-[var(--color-ink)] mb-4">Fähigkeiten</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div v-for="cap in capabilities" :key="cap.title"
          class="p-4 rounded-lg bg-[var(--color-surface)] border border-[var(--color-line)] hover:border-[var(--color-accent-border)] transition-colors">
          <div class="text-xs font-semibold text-[var(--color-ink)] mb-1">{{ cap.title }}</div>
          <div class="text-[10px] font-mono text-[var(--color-muted)] leading-relaxed">{{ cap.desc }}</div>
        </div>
      </div>
    </section>

    <!-- Provenienz footer -->
    <footer class="pt-8 border-t border-[var(--color-line)] text-[10px] font-mono text-[var(--color-muted)] flex flex-wrap gap-x-4 gap-y-1">
      <span>OnboardPilot</span>
      <span>·</span>
      <span>EUROKEY Software GmbH · Saarbrücken</span>
      <span>·</span>
      <span>FastAPI · Vue 3 · SQLite · OpenAI/Laya</span>
      <span>·</span>
      <span>Vishrut Pandey · OnboardPilot</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { gsap } from 'gsap'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '../api/client'
import type { Case, DashboardSummary } from '../types'

const { t } = useI18n()
const router = useRouter()
const summary = ref<DashboardSummary | null>(null)
const incomplete = ref<Case[]>([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
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
}

function refresh() { load() }

const kpis = computed(() => [
  { label: 'Gesamt', value: summary.value?.total_cases ?? '—', hint: 'alle Fälle', action: () => router.push('/cases') },
  { label: 'Unvollständig', value: summary.value?.incomplete_cases ?? '—', hint: 'in Bearbeitung', action: () => router.push('/cases') },
  { label: 'Überfällig', value: summary.value?.overdue_items_count ?? '—', hint: 'offene Punkte', action: () => router.push('/cases') },
  { label: 'Blockiert', value: summary.value?.blocked_access_count ?? '—', hint: 'gestoppt', action: () => router.push('/cases') },
])

const workflow = [
  'Starter registrieren (oder aus CSV importieren)',
  'Onboarding-Fall anlegen (Rolle, Abteilung, Startdatum)',
  'Checkliste, Hardware, Zugriffe automatisch generieren',
  'Schritte abhaken, Hardware/Zugriffe verwalten',
  'Offene Punkte klären, Übergabeprotokoll erstellen',
  'Fall abschließen',
]

const boundaries = [
  'Keine Authentifizierung / kein SSO',
  'Keine E-Mail-Versand-Integration',
  'Keine Echtzeit-Collaboration',
  'Keine mobile App',
]

const capabilities = [
  { title: 'Starter', desc: 'Registrierung, CSV-Import, Status-Tracking' },
  { title: 'Onboarding-Fälle', desc: 'Rollen-Templates, Checklisten, Hardware, Zugriffe' },
  { title: 'Open Items', desc: 'Follow-ups, Fälligkeiten, Auflösung' },
  { title: 'Übergabe-PDF', desc: 'Automatisches Protokoll mit Unterschrift' },
  { title: 'Audit Trail', desc: 'Vollständige Historie aller Aktionen' },
  { title: 'Wissensbasis', desc: '8 Anleitungen, durchsuchbar' },
  { title: 'Dashboard', desc: 'Kennzahlen, offene Fälle, Status' },
  { title: 'Öffentliche Demo', desc: 'Read-only Telemetrie-Ansicht' },
]

function statusBadge(s: string) {
  const map: Record<string, string> = {
    completed: 'bg-[var(--color-emerald-soft)] text-[var(--color-emerald)]',
    in_progress: 'bg-[var(--color-amber-soft)] text-[var(--color-amber)]',
    blocked: 'bg-[var(--color-rose-soft)] text-[var(--color-rose)]',
    not_started: 'bg-[var(--color-canvas-subtle)] text-[var(--color-muted)]',
  }
  return map[s] || 'bg-[var(--color-canvas-subtle)] text-[var(--color-muted)]'
}

onMounted(() => {
  load()
  setInterval(load, 30000)
  // Staggered entrance animation
  gsap.from('.dashboard-section', { opacity: 0, y: 20, duration: 0.6, stagger: 0.1, ease: 'power2.out', delay: 0.2 })
})
</script>