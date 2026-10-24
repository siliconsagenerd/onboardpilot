<template>
  <div>
    <div v-if="loading" class="card p-6 text-muted">{{ t('loading') }}</div>
    <div v-else-if="error" class="card p-6 text-danger" role="alert">{{ error }}</div>
    <div v-else class="space-y-6">
      <div class="card p-5 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <div class="flex items-center gap-3 flex-wrap">
            <h1 class="text-2xl font-semibold tracking-tight text-ink">{{ caseData?.employee_name }}</h1>
            <span class="text-xs px-2.5 py-0.5 rounded-md font-medium border bg-surface-2 text-ink-soft border-line">
              {{ t(caseData?.status || '') || caseData?.status }}
            </span>
          </div>
          <p class="text-sm text-muted mt-1">
            {{ caseData?.role_template }} · {{ caseData?.department }} · <span class="mono">{{ caseData?.start_date }}</span>
          </p>
        </div>
        <button @click="downloadPdf"
          class="rounded-md border border-line bg-surface hover:bg-surface-2 px-3.5 py-2 text-sm font-medium text-ink transition-colors focus:ring-2 focus:ring-accent/20 outline-none">
          {{ t('handover_pdf') }}
        </button>
      </div>

      <div class="flex gap-1 border-b border-line pb-2 flex-wrap" role="tablist" :aria-label="t('cases')">
        <button v-for="tt in tabs" :key="tt" @click="tab=tt" role="tab" :aria-selected="tab===tt"
          :class="['px-3 py-1.5 rounded-md text-sm font-medium transition-colors', tab===tt ? 'bg-ink text-canvas' : 'text-ink-soft hover:text-ink hover:bg-surface-2']">
          {{ t(tt) }}
        </button>
      </div>

      <!-- Checklist -->
      <div v-if="tab==='checklist'" class="space-y-3">
        <div v-if="!checklist.length" class="card p-8 text-center text-muted">{{ t('no_items') }}</div>
        <div v-for="it in checklist" :key="it.id" class="card p-4 space-y-2">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div class="flex-1 min-w-[240px]">
              <div class="font-medium text-ink">{{ lang==='de'?it.title_de:it.title_en }}</div>
              <div class="text-xs text-muted mt-0.5">{{ lang==='de'?it.description_de:it.description_en }}</div>
              <div v-if="it.depends_on?.length" class="text-xs text-warn mt-1 font-mono">
                {{ t('depends_on') }}: {{ getDepTitles(it.depends_on) }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs px-2.5 py-1 rounded-md font-medium border" :class="statusClass(it.status)">
                {{ t(it.status) || it.status }}
              </span>
              <select v-if="canEditChecklist" @change="updateItem(it, $event)"
                class="rounded-md border border-line bg-surface text-xs px-2 py-1 focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none"
                :aria-label="t('action')">
                <option value="">{{ t('action') }}</option>
                <option value="not_started">{{ t('not_started') }}</option>
                <option value="in_progress">{{ t('in_progress') }}</option>
                <option value="completed">{{ t('completed') }}</option>
              </select>
            </div>
          </div>
          <div v-if="it.status==='blocked'" class="card-soft border-l-4 !border-l-danger p-3 text-xs text-danger" role="alert">
            <span class="font-semibold">{{ t('blocked') }}:</span> {{ blockedText(it) }}
          </div>
        </div>
      </div>

      <!-- Hardware -->
      <div v-if="tab==='hardware'" class="space-y-4">
        <div v-if="!hardware.length" class="card p-8 text-center text-muted">{{ t('no_hardware') }}</div>
        <div v-for="h in hardware" :key="h.id" class="card p-4 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div class="font-medium text-ink">{{ h.asset_type }} — {{ h.brand_model || '-' }}</div>
            <div class="text-xs text-muted mt-1 font-mono">
              {{ t('serial_number') }}: {{ h.serial_number || '-' }} · {{ t('condition') }}: {{ t('cond_' + h.condition) || h.condition }}
              · {{ h.handover_date ? (t('handover_date') + ': ' + h.handover_date) : t('not_handed_over') }}
            </div>
            <div v-if="h.notes" class="text-xs text-ink-soft mt-1">{{ h.notes }}</div>
          </div>
          <span class="text-xs px-2.5 py-1 rounded-md font-medium border mono"
            :class="h.handover_date ? 'bg-accent-soft text-accent-ink border-accent/20' : 'bg-surface-2 text-muted border-line'">
            {{ h.handover_date ? t('handed_over') : t('pending') }}
          </span>
        </div>

        <form v-if="isAdmin" @submit.prevent="submitHandover" class="card p-5 space-y-4" :aria-label="t('record_handover')">
          <h2 class="font-semibold text-ink">{{ t('record_handover') }}</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <label class="text-xs font-medium text-ink-soft flex flex-col gap-1">
              {{ t('asset') }}
              <select v-model="handover.asset_id" required
                class="rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none">
                <option value="" disabled>{{ t('select_asset') }}</option>
                <option v-for="h in pendingAssets" :key="h.id" :value="h.id">
                  {{ h.asset_type }} — {{ h.brand_model || h.serial_number || h.id }}
                </option>
              </select>
            </label>
            <label class="text-xs font-medium text-ink-soft flex flex-col gap-1">
              {{ t('handover_date') }}
              <input v-model="handover.handover_date" type="date" required
                class="rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none" />
            </label>
            <label class="text-xs font-medium text-ink-soft flex flex-col gap-1">
              {{ t('condition') }}
              <select v-model="handover.condition"
                class="rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none">
                <option value="new">{{ t('cond_new') }}</option>
                <option value="good">{{ t('cond_good') }}</option>
                <option value="fair">{{ t('cond_fair') }}</option>
                <option value="needs_repair">{{ t('cond_needs_repair') }}</option>
              </select>
            </label>
            <label class="text-xs font-medium text-ink-soft flex flex-col gap-1">
              {{ t('notes') }}
              <input v-model="handover.notes" type="text"
                class="rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none" />
            </label>
          </div>
          <div class="flex items-center gap-3">
            <button type="submit" :disabled="handoverBusy"
              class="rounded-md bg-ink text-canvas px-4 py-2 text-sm font-medium hover:bg-ink-soft disabled:opacity-50 transition-colors">
              {{ handoverBusy ? t('saving') : t('save') }}
            </button>
            <span v-if="handoverMsg" class="text-xs text-accent font-medium" role="status">{{ handoverMsg }}</span>
            <span v-if="handoverErr" class="text-xs text-danger" role="alert">{{ handoverErr }}</span>
          </div>
        </form>
      </div>

      <!-- Access -->
      <div v-if="tab==='access'" class="space-y-3">
        <div v-if="!access.length" class="card p-8 text-center text-muted">{{ t('no_access') }}</div>
        <div v-for="a in access" :key="a.id" class="card p-4 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div class="font-medium text-ink">{{ a.access_type }}</div>
            <div class="text-xs text-muted mt-0.5">{{ a.requester }}<template v-if="a.provisioning_owner"> · {{ a.provisioning_owner }}</template></div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs px-2.5 py-1 rounded-md font-medium border" :class="statusClass(a.status)">
              {{ t(a.status) || a.status }}
            </span>
            <div class="flex gap-1" v-if="isAdmin || isManager">
              <button v-if="a.status==='requested'" @click="transition(a,'approved')"
                class="text-xs rounded border border-line bg-surface hover:bg-surface-2 px-2.5 py-1 font-medium text-ink transition-colors">
                {{ t('approve') }}
              </button>
              <button v-if="a.status==='approved'" @click="transition(a,'provisioned')"
                class="text-xs rounded border border-line bg-surface hover:bg-surface-2 px-2.5 py-1 font-medium text-ink transition-colors">
                {{ t('provision') }}
              </button>
              <button v-if="a.status==='provisioned'" @click="transition(a,'verified')"
                class="text-xs rounded bg-accent-soft text-accent-ink hover:bg-accent/20 px-2.5 py-1 font-medium transition-colors">
                {{ t('verify') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Open items -->
      <div v-if="tab==='open_items'" class="space-y-3">
        <div v-if="!openItems.length" class="card p-8 text-center text-muted">{{ t('no_open_items') }}</div>
        <div v-for="o in openItems" :key="o.id" class="card p-4 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div class="font-medium text-ink">{{ o.title }}</div>
            <div class="text-xs text-muted mt-0.5">{{ o.description }}</div>
            <div v-if="o.due_date" class="text-xs text-muted mt-0.5 font-mono">{{ t('due_date') }}: {{ o.due_date }}</div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs px-2.5 py-1 rounded-md font-medium border" :class="statusClass(o.status)">
              {{ t(o.status) || o.status }}
            </span>
            <button v-if="o.status!=='resolved' && (isAdmin || isManager)" @click="resolve(o)"
              class="text-xs rounded border border-line bg-surface hover:bg-surface-2 px-2.5 py-1 font-medium text-ink transition-colors">
              {{ t('resolve') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Audit -->
      <div v-if="tab==='audit'" class="space-y-2">
        <div v-if="!audit.length" class="card p-8 text-center text-muted">{{ t('no_audit') }}</div>
        <div v-for="a in audit" :key="a.id" class="card p-3.5 text-xs space-y-1">
          <div class="flex items-baseline justify-between gap-2 flex-wrap">
            <span class="font-semibold text-ink">{{ a.action }}</span>
            <span class="text-muted mono">{{ a.timestamp }}</span>
          </div>
          <div class="text-ink-soft">{{ a.description }}</div>
          <div class="text-muted font-mono">{{ a.actor }} · {{ a.entity_type }}</div>
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

function statusClass(s: string) {
  if (s === 'blocked') return 'bg-warn-soft text-warn border-warn/20'
  if (s === 'completed' || s === 'verified' || s === 'resolved') return 'bg-accent-soft text-accent-ink border-accent/20'
  if (s === 'in_progress' || s === 'approved' || s === 'provisioned' || s === 'open') return 'bg-info-soft text-info border-info/20'
  return 'bg-surface-2 text-ink-soft border-line'
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
