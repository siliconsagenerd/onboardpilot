<template>
  <div class="min-h-screen bg-[#08090a] text-[#f7f8f8] selection:bg-[#5e6ad2]/30 selection:text-white">
    <!-- Top precision navigation bar -->
    <header v-if="auth.isAuthed" class="sticky top-0 z-40 bg-[#08090a]/80 backdrop-blur-md border-b border-white/[0.08]">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-6">
          <router-link to="/" class="flex items-center gap-2.5 group">
            <span class="inline-flex h-7 w-7 items-center justify-center rounded bg-gradient-to-br from-[#5e6ad2] to-[#434eb0] text-white font-mono text-xs font-semibold shadow-inner">OP</span>
            <span class="font-medium tracking-tight text-sm text-[#f7f8f8] group-hover:text-white transition-colors">{{ t('app') }}</span>
          </router-link>

          <nav class="hidden md:flex items-center gap-1 text-xs font-medium" aria-label="Primary">
            <router-link v-for="l in links" :key="l.to" :to="l.to"
              class="px-2.5 py-1.5 rounded text-[#8a8f98] hover:text-[#f7f8f8] hover:bg-white/[0.04] transition-colors"
              active-class="!text-white !bg-white/[0.08] !shadow-sm">
              {{ t(l.key) }}
            </router-link>
          </nav>
        </div>

        <div class="flex items-center gap-3">
          <!-- Segmented Language Switcher -->
          <div class="inline-flex rounded border border-white/[0.08] bg-[#121316] p-0.5" role="group" :aria-label="t('language')">
            <button v-for="o in ['de','en']" :key="o" @click="setLang(o)"
              :class="['px-2 py-0.5 text-[11px] font-mono rounded transition-colors', lang===o ? 'bg-[#26282e] text-white shadow-sm font-semibold' : 'text-[#8a8f98] hover:text-[#f7f8f8]']">
              {{ o.toUpperCase() }}
            </button>
          </div>

          <div class="h-4 w-px bg-white/[0.08] hidden sm:block"></div>

          <div class="flex items-center gap-2">
            <span class="text-xs font-mono text-[#8a8f98] hidden sm:inline">{{ auth.user?.username }}</span>
            <button @click="doLogout"
              class="px-2.5 py-1 text-xs text-[#8a8f98] hover:text-[#f43f5e] hover:bg-[#f43f5e]/10 rounded transition-colors">
              {{ t('logout') }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      <router-view v-slot="{ Component }">
        <transition name="view-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from './stores/auth'

const { t, locale } = useI18n()
const auth = useAuth()
const router = useRouter()

const lang = computed(() => locale.value)
function setLang(l: string) {
  locale.value = l
  localStorage.setItem('onboardpilot_locale', l)
}

const links = [
  { to: '/', key: 'dashboard' },
  { to: '/cases', key: 'cases' },
  { to: '/guides', key: 'guides' },
  { to: '/public-demo', key: 'public_demo' },
]

function doLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.view-fade-enter-active,
.view-fade-leave-active {
  transition: opacity 0.12s ease;
}
.view-fade-enter-from,
.view-fade-leave-to {
  opacity: 0;
}
</style>
