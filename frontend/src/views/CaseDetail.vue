<template>
  <div>
    <div v-if="loading" class="panel p-8 text-center text-xs font-mono text-[var(--color-ink-soft)]">{{ t('loading') }}</div>
    <div v-else-if="error" class="panel p-4 text-xs font-mono text-[var(--color-rose)] bg-[var(--color-rose-soft)] border-[var(--color-rose)]/30" role="alert">{{ error }}</div>
    <div v-else class="space-y-4">
      <!-- Employee Banner -->
      <div class="panel p-5 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <div class="flex items-center gap-3 flex-wrap">
            <span class="text-[var(--color-muted)] font-mono text-xs">#{{ caseData?.id.slice(0, 8) }}</span>
            <h1 class="text-xl font-semibold tracking-tight text-[var(--color-ink)]">{{ caseData?.employee_name }}</h1>
            <span class="status-badge" :class="statusBadge(caseData?.status || '')">
              <span class="h-1.5 w-1.5 rounded-full" :class="statusDot(caseData?.status || '')"></span>
              {{ t(caseData?.status || '') || caseData?.status }}
            </span>
          </div>
          <p class="text-xs text-[var(--color-ink-soft)] mt-1 font-mono">
            {{ caseData?.role_template }} · {{ caseData?.department }} · {{ caseData?.start_date }}
          </p>
        </div>
        <button @click="downloadPdf"
          class="panel px-3.5 py-1.5 text-xs font-medium text-[var(--color-ink)] hover:border-[var(--color-line-strong)] hover:bg-[var(--color-canvas-subtle)] transition-colors flex items-center gap-2">
          <span class="font-mono text-[var(--color-ink-soft)]">PDF</span>
          <span>{{ t('handover_pdf') }}</span>
        </button>
      </div>

      <!-- Linear style tabs -->
      <div class="flex gap-1 border-b border-[var(--color-line)] pb-2 flex-wrap" role="tablist" :aria-label="t('cases')">
        <button v-for="tt in tabs" :key="tt" @click="tab=tt" role="tab" :aria-selected="tab===tt"
          :class="['px-3 py-1 text-xs font-mono rounded transition-colors', tab===tt ? 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink)] font-semibold border border-[var(--color-line)] shadow-xs' : 'text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] hover:bg-[var(--color-canvas-subtle)]']">
          {{ t(tt) }}
        </button>
      </div>

      <!-- Checklist -->
      <div v-if="tab==='checklist'" class="space-y-2">
        <div v-if="!checklist.length" class="panel p-8 text-center text-xs font-mono text-[var(--color-muted)]">{{ t('no_items') }}</div>
        <div v-for="it in checklist" :key="it.id" class="panel p-3.5 space-y-2">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div class="flex-1 min-w-[240px]">
              <div class="text-xs font-medium text-[var(--color-ink)]">{{ lang==='de'?it.title_de:it.title_en }}</div>
              <div class="text-[11px] text-[var(--color-ink-soft)] mt-0.5">{{ lang==='de'?it.description_de:it.description_en }}</div>
              <div v-if="it.depends_on?.length" class="text-[11px] text-[var(--color-amber)] mt-1 font-mono">
                {{ t('depends_on') }}: {{ getDepTitles(it.depends_on) }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="status-badge" :class="statusBadge(it.status)">
                <span class="h-1.5 w-1.5 rounded-full" :class="statusDot(it.status)"></span>
                {{ t(it.status) || it.status }}
              </span>
              <select v-if="canEditChecklist" @change="updateItem(it, $event)"
                class="linear-input text-[11px] px-2 py-0.5 font-mono"
                :aria-label="t('action')">
                <option value="">{{ t('action') }}</option>
                <option value="not_started">{{ t('not_started') }}</option>
                <option value="in_progress">{{ t('in_progress') }}</option>
                <option value="completed">{{ t('completed') }}</option>
              </select>
            </div>
          </div>
          <div v-if="it.status==='blocked'" class="border-l-2 border-[var(--color-rose)] bg-[var(--color-rose-soft)] p-2 text-xs font-mono text-[var(--color-rose)]" role="alert">
            <span class="font-semibold">{{ t('blocked') }}:</span> {{ blockedText(it) }}
          </div>
        </div>
      </div>

      <!-- Hardware -->
      <div v-if="tab==='hardware'" class="space-y-4">
        <div v-if="!hardware.length" class="panel p-8 text-center text-xs font-mono text-[var(--color-muted)]">{{ t('no_hardware') }}</div>
        <div v-for="h in hardware" :key="h.id" class="panel p-3.5 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div class="text-xs font-medium text-[var(--color-ink)]">{{ h.asset_type }} — {{ h.brand_model || '-' }}</div>
            <div class="text-[11px] text-[var(--color-ink-soft)] mt-1 font-mono">
              {{ t('serial_number') }}: {{ h.serial_number || '-' }} · {{ t('condition') }}: {{ t('cond_' + h.condition) || h.condition }}
              · {{ h.handover_date ? (t('handover_date') + ': ' + h.handover_date) : t('not_handed_over') }}
            </div>
            <div v-if="h.notes" class="text-[11px] text-[var(--color-muted)] mt-1">{{ h.notes }}</div>
          </div>
          <span class="status-badge"
            :class="h.handover_date ? 'bg-[var(--color-emerald-soft)] text-[var(--color-emerald)] border border-[var(--color-emerald)]/30' : 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] border border-[var(--color-line)]'">
            {{ h.handover_date ? t('handed_over') : t('pending') }}
          </span>
        </div>

        <form v-if="isAdmin" @submit.prevent="submitHandover" class="panel p-4 space-y-3" :aria-label="t('record_handover')">
          <h2 class="text-xs font-semibold uppercase tracking-wider font-mono text-[var(--color-ink-soft)]">{{ t('record_handover') }}</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label class="text-[11px] font-mono text-[var(--color-ink-soft)] flex flex-col gap-1">
              {{ t('asset') }}
              <select v-model="handover.asset_id" required
                class="linear-input text-xs px-2.5 py-1.5 font-sans">
                <option value="" disabled>{{ t('select_asset') }}</option>
                <option v-for="h in pendingAssets" :key="h.id" :value="h.id">
                  {{ h.asset_type }} — {{ h.brand_model || h.serial_number || h.id }}
                </option>
              </select>
            </label>
            <label class="text-[11px] font-mono text-[var(--color-ink-soft)] flex flex-col gap-1">
              {{ t('handover_date') }}
              <input v-model="handover.handover_date" type="date" required
                class="linear-input text-xs px-2.5 py-1.5 font-mono" />
            </label>
            <label class="text-[11px] font-mono text-[var(--color-ink-soft)] flex flex-col gap-1">
              {{ t('condition') }}
              <select v-model="handover.condition"
                class="linear-input text-xs px-2.5 py-1.5 font-sans">
                <option value="new">{{ t('cond_new') }}</option>
                <option value="good">{{ t('cond_good') }}</option>
                <option value="fair">{{ t('cond_fair') }}</option>
                <option value="needs_repair">{{ t('cond_needs_repair') }}</option>
              </select>
            </label>
            <label class="text-[11px] font-mono text-[var(--color-ink-soft)] flex flex-col gap-1">
              {{ t('notes') }}
              <input v-model="handover.notes" type="text"
                class="linear-input text-xs px-2.5 py-1.5 font-sans" />
            </label>
          </div>
          <div class="flex items-center gap-3 pt-1">
            <button type="submit" :disabled="handoverBusy"
              class="px-3.5 py-1.5 text-xs font-medium rounded bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white disabled:opacity-50 transition-colors shadow-xs cursor-pointer">
              {{ handoverBusy ? t('saving') : t('save') }}
            </button>
            <span v-if="handoverMsg" class="text-xs font-mono text-[var(--color-emerald)]" role="status">{{ handoverMsg }}</span>
            <span v-if="handoverErr" class="text-xs font-mono text-[var(--color-rose)]" role="alert">{{ handoverErr }}</span>
          </div>
        </form>
      </div>

      <!-- Access -->
      <div v-if="tab==='access'" class="space-y-2">
        <div v-if="!access.length" class="panel p-8 text-center text-xs font-mono text-[var(--color-muted)]">{{ t('no_access') }}</div>
        <div v-for="a in access" :key="a.id" class="panel p-3.5 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div class="text-xs font-medium text-[var(--color-ink)]">{{ a.access_type }}</div>
            <div class="text-[11px] text-[var(--color-ink-soft)] mt-0.5 font-mono">{{ a.requester }}<template v-if="a.provisioning_owner"> · {{ a.provisioning_owner }}</template></div>
          </div>
          <div class="flex items-center gap-2">
            <span class="status-badge" :class="statusBadge(a.status)">
              <span class="h-1.5 w-1.5 rounded-full" :class="statusDot(a.status)"></span>
              {{ t(a.status) || a.status }}
            </span>
            <div class="flex gap-1" v-if="isAdmin || isManager">
              <button v-if="a.status==='requested'" @click="transition(a,'approved')"
                class="px-2.5 py-1 text-xs rounded border border-[var(--color-line)] hover:border-[var(--color-line-strong)] bg-[var(--color-surface)] text-[var(--color-ink)] transition-colors">
                {{ t('approve') }}
              </button>
              <button v-if="a.status==='approved'" @click="transition(a,'provisioned')"
                class="px-2.5 py-1 text-xs rounded border border-[var(--color-line)] hover:border-[var(--color-line-strong)] bg-[var(--color-surface)] text-[var(--color-ink)] transition-colors">
                {{ t('provision') }}
              </button>
              <button v-if="a.status==='provisioned'" @click="transition(a,'verified')"
                class="px-2.5 py-1 text-xs rounded bg-[var(--color-emerald-soft)] text-[var(--color-emerald)] hover:bg-[var(--color-emerald)]/20 transition-colors">
                {{ t('verify') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Open items -->
      <div v-if="tab==='open_items'" class="space-y-2">
        <div v-if="!openItems.length" class="panel p-8 text-center text-xs font-mono text-[var(--color-muted)]">{{ t('no_open_items') }}</div>
        <div v-for="o in openItems" :key="o.id" class="panel p-3.5 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div class="text-xs font-medium text-[var(--color-ink)]">{{ o.title }}</div>
            <div class="text-[11px] text-[var(--color-ink-soft)] mt-0.5">{{ o.description }}</div>
            <div v-if="o.due_date" class="text-[11px] text-[var(--color-muted)] mt-0.5 font-mono">{{ t('due_date') }}: {{ o.due_date }}</div>
          </div>
          <div class="flex items-center gap-2">
            <span class="status-badge" :class="statusBadge(o.status)">
              <span class="h-1.5 w-1.5 rounded-full" :class="statusDot(o.status)"></span>
              {{ t(o.status) || o.status }}
            </span>
            <button v-if="o.status!=='resolved' && (isAdmin || isManager)" @click="resolve(o)"
              class="px-2.5 py-1 text-xs rounded border border-[var(--color-line)] hover:border-[var(--color-line-strong)] bg-[var(--color-surface)] text-[var(--color-ink)] transition-colors">
              {{ t('resolve') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Audit -->
      <div v-if="tab==='audit'" class="space-y-2">
        <div v-if="!audit.length" class="panel p-8 text-center text-xs font-mono text-[var(--color-muted)]">{{ t('no_audit') }}</div>
        <div v-for="a in audit" :key="a.id" class="panel p-3 text-xs space-y-1">
          <div class="flex items-baseline justify-between gap-2 flex-wrap">
            <span class="font-semibold text-[var(--color-ink)] font-mono">{{ a.action }}</span>
            <span class="text-[var(--color-muted)] font-mono text-[11px]">{{ a.timestamp }}</span>
          </div>
          <div class="text-[var(--color-ink-soft)] text-xs">{{ a.description }}</div>
          <div class="text-[var(--color-muted)] font-mono text-[10px]">{{ a.actor }} · {{ a.entity_type }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '../api/client'
import { useAuth } from '../stores/auth'
import type { Case, ChecklistItem, Hardware, AccessReq, OpenItem, AuditEntry } from '../types'

const route = useRoute()
const { t, locale } = useI18n()
const auth = useAuth()
const lang = computed(() => locale.value)

const isAdmin = computed(() => auth.role === 'admin')
const isManager = computed(() => auth.role === 'manager' || auth.role === 'admin')
const canEditChecklist = computed(() => isManager.value)

const caseData = ref<Case | null>(null)
const checklist = ref<ChecklistItem[]>([])
const hardware = ref<Hardware[]>([])
const access = ref<AccessReq[]>([])
const openItems = ref<OpenItem[]>([])
const audit = ref<AuditEntry[]>([])
const loading = ref(true)
const error = ref('')
const tab = ref('checklist')
const tabs = ['checklist', 'hardware', 'access', 'open_items', 'audit']

const handoverBusy = ref(false)
const handoverMsg = ref('')
const handoverErr = ref('')
const handover = reactive({ asset_id: '', handover_date: '', condition: 'new', notes: '' })

const cid = route.params.id as string

const pendingAssets = computed(() => hardware.value.filter(h => !h.handover_date))

async function refreshAll() {
  const [hw, cl, au] = await Promise.all([
    api.get(`/api/hardware?case_id=${cid}`),
    api.get(`/api/cases/${cid}/checklist`),
    api.get(`/api/audit?case_id=${cid}`),
  ])
  hardware.value = hw.data
  checklist.value = cl.data
  audit.value = au.data
}

onMounted(async () => {
  try {
    const [c, cl, hw, ac, oi, au] = await Promise.all([
      api.get(`/api/cases/${cid}`),
      api.get(`/api/cases/${cid}/checklist`),
      api.get(`/api/hardware?case_id=${cid}`),
      api.get(`/api/access?case_id=${cid}`),
      api.get(`/api/open-items?case_id=${cid}`),
      api.get(`/api/audit?case_id=${cid}`),
    ])
    caseData.value = c.data
    checklist.value = cl.data
    hardware.value = hw.data
    access.value = ac.data
    openItems.value = oi.data
    audit.value = au.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('failed_load')
  } finally {
    loading.value = false
  }
})

function getDepTitles(deps: string[]) {
  return (deps || []).map(k => checklist.value.find(i => i.key === k)?.title_de || k).join(', ')
}

function blockedText(it: ChecklistItem) {
  if (it.blocked_reason) return it.blocked_reason
  const deps = getDepTitles(it.depends_on || [])
  return deps ? `${t('blocked')}: ${deps}` : ''
}

function statusBadge(s: string) {
  if (s === 'blocked') return 'bg-[var(--color-rose-soft)] text-[var(--color-rose)] border border-[var(--color-rose)]/30'
  if (s === 'completed' || s === 'verified' || s === 'resolved') return 'bg-[var(--color-emerald-soft)] text-[var(--color-emerald)] border border-[var(--color-emerald)]/30'
  if (s === 'in_progress' || s === 'approved' || s === 'provisioned' || s === 'open') return 'bg-[var(--color-accent-soft)] text-[var(--color-accent)] border border-[var(--color-accent)]/30'
  return 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] border border-[var(--color-line)]'
}

function statusDot(s: string) {
  if (s === 'blocked') return 'bg-[var(--color-rose)]'
  if (s === 'completed' || s === 'verified' || s === 'resolved') return 'bg-[var(--color-emerald)]'
  if (s === 'in_progress' || s === 'approved' || s === 'provisioned' || s === 'open') return 'bg-[var(--color-accent)]'
  return 'bg-[var(--color-muted)]'
}

async function updateItem(it: ChecklistItem, e: Event) {
  const val = (e.target as HTMLSelectElement).value
  if (!val) return
  try {
    const r = await api.patch(`/api/checklist/${it.id}`, { status: val })
    const idx = checklist.value.findIndex(x => x.id === it.id)
    if (idx >= 0) checklist.value[idx] = r.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || t('failed_update')
  }
}

async function submitHandover() {
  handoverBusy.value = true
  handoverErr.value = ''
  handoverMsg.value = ''
  const asset = pendingAssets.value.find(h => h.id === handover.asset_id)
  if (!asset) {
    handoverErr.value = t('select_asset')
    handoverBusy.value = false
    return
  }
  try {
    await api.post('/api/hardware', {
      case_id: cid,
      asset_type: asset.asset_type,
      brand_model: asset.brand_model,
      serial_number: asset.serial_number,
      handover_date: handover.handover_date,
      condition: handover.condition,
      assigned_employee: caseData.value?.employee_name || '',
      notes: handover.notes,
    })
    await refreshAll()
    handoverMsg.value = t('handover_recorded')
    handover.asset_id = ''
    handover.notes = ''
  } catch (err: any) {
    handoverErr.value = err.response?.data?.detail || t('failed_handover')
  } finally {
    handoverBusy.value = false
  }
}

async function transition(a: AccessReq, status: string) {
  try {
    const r = await api.patch(`/api/access/${a.id}`, { status })
    const idx = access.value.findIndex(x => x.id === a.id)
    if (idx >= 0) access.value[idx] = r.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || t('failed_transition')
  }
}

async function resolve(o: OpenItem) {
  try {
    const r = await api.patch(`/api/open-items/${o.id}`, { status: 'resolved' })
    const idx = openItems.value.findIndex(x => x.id === o.id)
    if (idx >= 0) openItems.value[idx] = r.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || t('failed_resolve')
  }
}

async function downloadPdf() {
  try {
    const r = await api.get(`/api/cases/${cid}/handover.pdf`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([r.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `handover-${cid}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    error.value = t('failed_pdf')
  }
}
</script>
