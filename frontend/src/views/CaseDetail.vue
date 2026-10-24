<template>
  <div>
    <div v-if="loading" class="text-slate-500">Loading...</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else>
      <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h1 class="text-2xl font-bold">{{ caseData?.employee_name }}</h1>
        <button @click="downloadPdf" class="bg-blue-600 text-white px-4 py-2 rounded text-sm">Handover PDF</button>
      </div>

      <div class="flex gap-2 mb-4 flex-wrap">
        <button v-for="t in tabs" :key="t" @click="tab=t" :class="['px-3 py-1 rounded text-sm', tab===t?'bg-blue-600 text-white':'bg-slate-200']">{{ t }}</button>
      </div>

      <!-- Checklist -->
      <div v-if="tab==='checklist'" class="space-y-2">
        <div v-if="!checklist.length" class="text-slate-400">No items</div>
        <div v-for="it in checklist" :key="it.id" class="bg-white p-3 rounded shadow flex items-center justify-between gap-2">
          <div>
            <div class="font-medium">{{ lang==='de'?it.title_de:it.title_en }}</div>
            <div class="text-xs text-slate-500">{{ lang==='de'?it.description_de:it.description_en }}</div>
            <div v-if="it.depends_on?.length" class="text-xs text-amber-600">Depends on: {{ it.depends_on.join(', ') }}</div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs px-2 py-1 rounded bg-slate-100">{{ it.status }}</span>
            <select @change="updateItem(it, $event)" class="border rounded text-xs px-2 py-1">
              <option value="">Action</option>
              <option value="not_started">Not started</option>
              <option value="in_progress">In progress</option>
              <option value="completed">Complete</option>
            </select>
            <button @click="reopen(it)" class="text-xs text-blue-600">Reopen</button>
          </div>
        </div>
      </div>

      <!-- Hardware -->
      <div v-if="tab==='hardware'" class="space-y-2">
        <div v-if="!hardware.length" class="text-slate-400">No hardware</div>
        <div v-for="h in hardware" :key="h.id" class="bg-white p-3 rounded shadow">
          <div class="font-medium">{{ h.asset_type }} — {{ h.brand_model }}</div>
          <div class="text-xs text-slate-500">S/N: {{ h.serial_number }} · {{ h.condition }} · {{ h.handover_date || 'not handed over' }}</div>
        </div>
      </div>

      <!-- Access -->
      <div v-if="tab==='access'" class="space-y-2">
        <div v-if="!access.length" class="text-slate-400">No access requests</div>
        <div v-for="a in access" :key="a.id" class="bg-white p-3 rounded shadow flex items-center justify-between gap-2">
          <div>
            <div class="font-medium">{{ a.access_type }}</div>
            <div class="text-xs text-slate-500">{{ a.status }} · {{ a.requester }}</div>
          </div>
          <div class="flex gap-1">
            <button v-if="a.status==='requested'" @click="transition(a,'approved')" class="text-xs bg-blue-600 text-white px-2 py-1 rounded">Approve</button>
            <button v-if="a.status==='approved'" @click="transition(a,'provisioned')" class="text-xs bg-blue-600 text-white px-2 py-1 rounded">Provision</button>
            <button v-if="a.status==='provisioned'" @click="transition(a,'verified')" class="text-xs bg-green-600 text-white px-2 py-1 rounded">Verify</button>
          </div>
        </div>
      </div>

      <!-- Open items -->
      <div v-if="tab==='open'" class="space-y-2">
        <div v-if="!openItems.length" class="text-slate-400">No open items</div>
        <div v-for="o in openItems" :key="o.id" class="bg-white p-3 rounded shadow flex items-center justify-between gap-2">
          <div>
            <div class="font-medium">{{ o.title }}</div>
            <div class="text-xs text-slate-500">{{ o.owner }} · {{ o.priority }} · {{ o.status }} · due {{ o.due_date }}</div>
          </div>
          <button v-if="o.status!=='resolved'" @click="resolve(o)" class="text-xs text-green-600">Resolve</button>
        </div>
      </div>

      <!-- Audit -->
      <div v-if="tab==='audit'" class="space-y-2">
        <div v-if="!audit.length" class="text-slate-400">No audit entries</div>
        <div v-for="a in audit" :key="a.id" class="bg-white p-3 rounded shadow text-sm">
          <span class="font-medium">{{ a.action }}</span> by {{ a.actor }} — {{ a.timestamp }}
          <div class="text-xs text-slate-500">{{ a.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '../api/client'
import type { Case, ChecklistItem, Hardware, AccessReq, OpenItem, AuditEntry } from '../types'

const route = useRoute()
const { locale } = useI18n()
const lang = computed(() => locale.value)

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

const cid = route.params.id as string

onMounted(async () => {
  try {
    const c = await api.get(`/api/cases/${cid}`)
    caseData.value = c.data
    const cl = await api.get(`/api/cases/${cid}/checklist`)
    checklist.value = cl.data
    const hw = await api.get(`/api/hardware?case_id=${cid}`)
    hardware.value = hw.data
    const ac = await api.get(`/api/access?case_id=${cid}`)
    access.value = ac.data
    const oi = await api.get(`/api/open-items?case_id=${cid}`)
    openItems.value = oi.data
    const au = await api.get(`/api/audit?case_id=${cid}`)
    audit.value = au.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load'
  } finally {
    loading.value = false
  }
})

async function updateItem(it: ChecklistItem, e: Event) {
  const val = (e.target as HTMLSelectElement).value
  if (!val) return
  try {
    const r = await api.patch(`/api/checklist/${it.id}`, { status: val })
    const idx = checklist.value.findIndex(x => x.id === it.id)
    if (idx >= 0) checklist.value[idx] = r.data
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Update failed')
  }
}

async function reopen(it: ChecklistItem) {
  try {
    const r = await api.post(`/api/checklist/${it.id}/reopen`)
    const idx = checklist.value.findIndex(x => x.id === it.id)
    if (idx >= 0) checklist.value[idx] = r.data
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Reopen failed')
  }
}

async function transition(a: AccessReq, status: string) {
  try {
    const r = await api.patch(`/api/access/${a.id}`, { status })
    const idx = access.value.findIndex(x => x.id === a.id)
    if (idx >= 0) access.value[idx] = r.data
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Transition failed')
  }
}

async function resolve(o: OpenItem) {
  try {
    const r = await api.patch(`/api/open-items/${o.id}`, { status: 'resolved' })
    const idx = openItems.value.findIndex(x => x.id === o.id)
    if (idx >= 0) openItems.value[idx] = r.data
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Resolve failed')
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
    alert('PDF download failed')
  }
}
</script>
