<template>
  <div>
    <div v-if="loading" class="text-slate-500">{{ t('loading') }}</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else>
      <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h1 class="text-2xl font-bold text-slate-900">{{ caseData?.employee_name }}</h1>
        <button @click="downloadPdf" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">{{ t('handover_pdf') }}</button>
      </div>

      <div class="flex gap-2 mb-4 flex-wrap" role="tablist" aria-label="Case sections">
        <button v-for="tt in tabs" :key="tt" @click="tab=tt" :class="['px-3 py-1.5 rounded text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2', tab===tt?'bg-blue-600 text-white':'bg-slate-200 text-slate-700 hover:bg-slate-300']" :aria-selected="tab===tt" role="tab">{{ t(tt) }}</button>
      </div>

      <!-- Checklist -->
      <div v-if="tab==='checklist'" class="space-y-3">
        <div v-if="!checklist.length" class="text-slate-400">{{ t('no_items') }}</div>
        <div v-for="it in checklist" :key="it.id" class="bg-white p-4 rounded shadow flex flex-col gap-2">
          <div class="flex items-start justify-between gap-2 flex-wrap">
            <div>
              <div class="font-medium text-slate-900">{{ lang==='de'?it.title_de:it.title_en }}</div>
              <div class="text-xs text-slate-500">{{ lang==='de'?it.description_de:it.description_en }}</div>
              <div v-if="it.depends_on?.length" class="text-xs text-amber-600 mt-1">
                {{ t('depends_on') }}: {{ getDepTitles(it.depends_on) }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs px-2.5 py-1 rounded-full font-medium" :class="statusClass(it.status)">
                {{ t(it.status) || it.status }}
              </span>
              <select v-if="canEditChecklist" @change="updateItem(it, $event)" class="border border-slate-300 rounded text-xs px-2 py-1 bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500" :aria-label="t('action')">
                <option value="">{{ t('action') }}</option>
                <option value="not_started">{{ t('not_started') }}</option>
                <option value="in_progress">{{ t('in_progress') }}</option>
                <option value="completed">{{ t('completed') }}</option>
              </select>
            </div>
          </div>
          <div v-if="it.status==='blocked'" class="bg-red-50 border-l-4 border-red-500 p-3 text-xs text-red-700 flex flex-col gap-0.5" role="alert">
            <span class="font-semibold">{{ t('blocked') }}</span>
            <span>{{ blockedText(it) }}</span>
          </div>
        </div>
      </div>

      <!-- Hardware -->
      <div v-if="tab==='hardware'" class="space-y-4">
        <div v-if="!hardware.length" class="text-slate-400">{{ t('no_hardware') }}</div>
        <div v-for="h in hardware" :key="h.id" class="bg-white p-4 rounded shadow">
          <div class="flex items-start justify-between gap-2 flex-wrap">
            <div>
              <div class="font-medium text-slate-900">{{ h.asset_type }} — {{ h.brand_model || '-' }}</div>
              <div class="text-xs text-slate-500 mt-0.5">
                {{ t('serial_number') }}: {{ h.serial_number || '-' }} · {{ t('condition') }}: {{ h.condition }}
                · {{ h.handover_date ? (t('handover_date') + ': ' + h.handover_date) : t('not_handed_over') }}
              </div>
              <div v-if="h.notes" class="text-xs text-slate-600 mt-1">{{ h.notes }}</div>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full font-medium" :class="h.handover_date ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'">
              {{ h.handover_date ? t('handed_over') : t('pending') }}
            </span>
          </div>
        </div>

        <form v-if="isAdmin" @submit.prevent="submitHandover" class="bg-slate-50 border border-slate-200 p-4 rounded space-y-3" aria-label="Hardware handover">
          <h2 class="font-semibold text-slate-900">{{ t('record_handover') }}</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label class="text-xs text-slate-700 flex flex-col gap-1">
              {{ t('asset') }}
              <select v-model="handover.asset_id" required class="border border-slate-300 rounded px-2 py-1.5 text-sm bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
                <option value="" disabled>{{ t('select_asset') }}</option>
                <option v-for="h in pendingAssets" :key="h.id" :value="h.id">
                  {{ h.asset_type }} — {{ h.brand_model || h.serial_number || h.id }}
                </option>
              </select>
            </label>
            <label class="text-xs text-slate-700 flex flex-col gap-1">
              {{ t('handover_date') }}
              <input v-model="handover.handover_date" type="date" required class="border border-slate-300 rounded px-2 py-1.5 text-sm bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500" />
            </label>
            <label class="text-xs text-slate-700 flex flex-col gap-1">
              {{ t('condition') }}
              <select v-model="handover.condition" class="border border-slate-300 rounded px-2 py-1.5 text-sm bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
                <option value="new">{{ t('cond_new') }}</option>
                <option value="good">{{ t('cond_good') }}</option>
                <option value="fair">{{ t('cond_fair') }}</option>
                <option value="needs_repair">{{ t('cond_needs_repair') }}</option>
              </select>
            </label>
            <label class="text-xs text-slate-700 flex flex-col gap-1">
              {{ t('notes') }}
              <input v-model="handover.notes" type="text" class="border border-slate-300 rounded px-2 py-1.5 text-sm bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500" />
            </label>
          </div>
          <div class="flex items-center gap-3">
            <button type="submit" :disabled="handoverBusy" class="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white px-4 py-2 rounded text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">
              {{ handoverBusy ? t('saving') : t('save') }}
            </button>
            <span v-if="handoverMsg" class="text-sm text-emerald-700 font-medium" role="status">{{ handoverMsg }}</span>
            <span v-if="handoverErr" class="text-sm text-red-700" role="alert">{{ handoverErr }}</span>
          </div>
        </form>
      </div>

      <!-- Access -->
      <div v-if="tab==='access'" class="space-y-2">
        <div v-if="!access.length" class="text-slate-400">{{ t('no_access') }}</div>
        <div v-for="a in access" :key="a.id" class="bg-white p-4 rounded shadow flex items-center justify-between gap-2 flex-wrap">
          <div>
            <div class="font-medium text-slate-900">{{ a.access_type }}</div>
            <div class="text-xs text-slate-500 mt-0.5">{{ a.requester }}<template v-if="a.provisioning_owner"> · {{ a.provisioning_owner }}</template></div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs px-2.5 py-1 rounded-full font-medium" :class="statusClass(a.status)">{{ t(a.status) || a.status }}</span>
            <div class="flex gap-1" v-if="isAdmin || isManager">
              <button v-if="a.status==='requested'" @click="transition(a,'approved')" class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded">{{ t('approve') }}</button>
              <button v-if="a.status==='approved'" @click="transition(a,'provisioned')" class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded">{{ t('provision') }}</button>
              <button v-if="a.status==='provisioned'" @click="transition(a,'verified')" class="text-xs bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded">{{ t('verify') }}</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Open items -->
      <div v-if="tab==='open'" class="space-y-2">
        <div v-if="!openItems.length" class="text-slate-400">{{ t('no_open_items') }}</div>
        <div v-for="o in openItems" :key="o.id" class="bg-white p-4 rounded shadow flex items-center justify-between gap-2 flex-wrap">
          <div>
            <div class="font-medium text-slate-900">{{ o.title }}</div>
            <div class="text-xs text-slate-500 mt-0.5">{{ o.description }}</div>
            <div v-if="o.due_date" class="text-xs text-slate-400 mt-0.5">{{ t('due_date') }}: {{ o.due_date }}</div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs px-2.5 py-1 rounded-full font-medium" :class="statusClass(o.status)">{{ t(o.status) || o.status }}</span>
            <button v-if="o.status!=='resolved' && (isAdmin || isManager)" @click="resolve(o)" class="text-xs text-green-700 hover:text-green-800 font-medium">{{ t('resolve') }}</button>
          </div>
        </div>
      </div>

      <!-- Audit -->
      <div v-if="tab==='audit'" class="space-y-2">
        <div v-if="!audit.length" class="text-slate-400">{{ t('no_audit') }}</div>
        <div v-for="a in audit" :key="a.id" class="bg-white p-4 rounded shadow text-sm">
          <div class="flex items-baseline justify-between gap-2 flex-wrap">
            <span class="font-medium text-slate-900">{{ a.action }}</span>
            <span class="text-xs text-slate-400">{{ a.timestamp }}</span>
          </div>
          <div class="text-xs text-slate-500 mt-0.5">{{ a.description }}</div>
          <div class="text-xs text-slate-400 mt-0.5">{{ a.actor }} · {{ a.entity_type }}</div>
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
const tabs = ['checklist', 'hardware', 'access', 'open', 'audit']

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
    error.value = e.response?.data?.detail || 'Failed to load'
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
  return deps ? `Blocked: requires '${deps}' to be completed first.` : ''
}

function statusClass(s: string) {
  if (s === 'blocked') return 'bg-amber-100 text-amber-800'
  if (s === 'completed' || s === 'verified' || s === 'resolved') return 'bg-emerald-100 text-emerald-800'
  if (s === 'not_started' || s === 'requested') return 'bg-slate-100 text-slate-700'
  if (s === 'in_progress' || s === 'approved' || s === 'provisioned' || s === 'open') return 'bg-blue-100 text-blue-800'
  return 'bg-slate-100 text-slate-700'
}

async function updateItem(it: ChecklistItem, e: Event) {
  const val = (e.target as HTMLSelectElement).value
  if (!val) return
  try {
    const r = await api.patch(`/api/checklist/${it.id}`, { status: val })
    const idx = checklist.value.findIndex(x => x.id === it.id)
    if (idx >= 0) checklist.value[idx] = r.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Update failed'
  }
}

async function submitHandover() {
  handoverBusy.value = true
  handoverErr.value = ''
  handoverMsg.value = ''
  const asset = pendingAssets.value.find(h => h.id === handover.asset_id)
  if (!asset) {
    handoverErr.value = 'Select an asset'
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
    handoverErr.value = err.response?.data?.detail || 'Handover failed'
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
    error.value = err.response?.data?.detail || 'Transition failed'
  }
}

async function resolve(o: OpenItem) {
  try {
    const r = await api.patch(`/api/open-items/${o.id}`, { status: 'resolved' })
    const idx = openItems.value.findIndex(x => x.id === o.id)
    if (idx >= 0) openItems.value[idx] = r.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Resolve failed'
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
    error.value = 'PDF download failed'
  }
}
</script>
