<template>
  <div class="min-h-screen bg-[var(--color-canvas)] text-[var(--color-ink)] selection:bg-[var(--color-accent)]/25 selection:text-[var(--color-ink)] transition-colors duration-200">
    <div v-if="auth.isAuthed" class="w-full px-4 sm:px-6 py-1.5 border-b border-[var(--color-line)] bg-[var(--color-surface)]/60 text-[9px] font-mono text-[var(--color-muted)] uppercase tracking-wider flex items-center justify-between gap-2 flex-wrap">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-[var(--color-accent)] font-bold">Bewerbungsprojekt</span>
        <span>·</span>
        <span>EUROKEY Software GmbH · Saarbrücken</span>
        <span>·</span>
        <span>Digital Dispatch</span>
      </div>
      <div class="flex items-center gap-2">
        <span>Vol. IV · Issue 12</span>
        <span>·</span>
        <span>OnboardPilot Console</span>
      </div>
    </div>
    <header v-if="auth.isAuthed" class="sticky top-0 z-40 border-b border-[var(--color-line)] bg-[var(--color-surface)]/80 backdrop-blur-xl">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        <div class="flex items-center gap-8 min-w-0">
          <router-link to="/" class="flex items-center gap-3 group shrink-0">
            <span class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--color-accent)] text-[#ffffff] text-sm font-bold shadow-sm ring-1 ring-[var(--color-accent)]/20 transition-transform group-hover:scale-105">OP</span>
            <span class="font-bold tracking-tight text-base text-[var(--color-ink)] group-hover:text-[var(--color-accent)] transition-colors">{{ t('app') }}</span>
          </router-link>

          <nav class="hidden md:flex items-center gap-1 text-sm font-medium" aria-label="Primary">
            <router-link v-for="l in links" :key="l.to" :to="l.to"
              class="px-3 py-2 rounded-lg text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] hover:bg-[var(--color-canvas-subtle)] transition-colors"
              active-class="!text-[var(--color-accent)] !bg-[var(--color-accent-soft)] !font-semibold">
              {{ t(l.key) }}
            </router-link>
          </nav>
        </div>

        <div class="flex items-center gap-2">
          <button @click="toggleTheme"
            class="px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] hover:bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] transition-colors flex items-center gap-1.5 cursor-pointer shadow-sm"
            :title="isDark ? t('theme_light') : t('theme_dark')"
            :aria-label="t('theme')">
            <svg v-if="isDark" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
            <span class="hidden sm:inline text-xs font-semibold">{{ isDark ? t('theme_dark') : t('theme_light') }}</span>
          </button>

          <div class="inline-flex rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-0.5 shadow-sm" role="group" :aria-label="t('language')">
            <button v-for="o in ['de','en']" :key="o" @click="setLang(o)"
              :class="['px-2.5 py-1 text-xs font-mono rounded-md transition-colors cursor-pointer', lang===o ? 'bg-[var(--color-accent)] text-[#ffffff] font-semibold shadow-sm' : 'text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]']">
              {{ o.toUpperCase() }}
            </button>
          </div>

          <button @click="doLogout"
            class="px-3 py-1.5 text-xs font-medium rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] hover:bg-[var(--color-rose-soft)] hover:text-[var(--color-rose)] text-[var(--color-ink-soft)] transition-colors cursor-pointer shadow-sm">
            {{ t('logout') }}
          </button>
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
    <footer v-if="auth.isAuthed" class="border-t border-[var(--color-line)] py-4 mt-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between text-xs text-[var(--color-muted)] font-mono">
        <span>Vishrut Pandey · OnboardPilot · IT Operations Console</span>
        <span>FastAPI · Vue 3 · SQLite · OpenAI/Laya</span>
      </div>
    </footer>
    <ProjectSpotlight />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from './stores/auth'
import ProjectSpotlight from './components/ProjectSpotlight.vue'

const { t, locale } = useI18n()
const auth = useAuth()
const router = useRouter()

const isDark = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('onboardpilot_theme')
  if (saved === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
})

function toggleTheme() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('onboardpilot_theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('onboardpilot_theme', 'light')
  }
}

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

<style>
.view-fade-enter-active,
.view-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.view-fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.view-fade-leave-to {
  opacity: 0;
}
</style>
