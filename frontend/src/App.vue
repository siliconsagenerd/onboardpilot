<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <nav v-if="auth.isAuthed" class="bg-white border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-2">
        <router-link to="/" class="font-bold text-blue-600 text-lg">OnboardPilot</router-link>
        <div class="flex items-center gap-3 text-sm flex-wrap">
          <router-link to="/" class="hover:text-blue-600">{{ t('dashboard') }}</router-link>
          <router-link to="/cases" class="hover:text-blue-600">{{ t('cases') }}</router-link>
          <router-link to="/guides" class="hover:text-blue-600">{{ t('guides') }}</router-link>
          <router-link to="/public-demo" class="hover:text-blue-600">{{ t('public_demo') }}</router-link>
          <select v-model="lang" @change="setLang" class="border rounded px-2 py-1">
            <option value="de">DE</option>
            <option value="en">EN</option>
          </select>
          <button @click="doLogout" class="text-slate-500 hover:text-red-600">{{ t('logout') }}</button>
        </div>
      </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-6">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuth } from './stores/auth'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const auth = useAuth()
const { t, locale } = useI18n()
const router = useRouter()

const lang = computed({
  get: () => locale.value,
  set: (v: string) => { locale.value = v; localStorage.setItem('lang', v) }
})

function setLang() { localStorage.setItem('lang', lang.value) }

function doLogout() {
  auth.logout()
  router.push('/login')
}
</script>
