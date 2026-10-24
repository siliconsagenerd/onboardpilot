<template>
  <div class="min-h-screen bg-[var(--color-canvas)] text-[var(--color-ink)] selection:bg-[#5e6ad2]/20 selection:text-[var(--color-ink)] transition-colors duration-150">
    <!-- Top precision navigation bar -->
    <header v-if="auth.isAuthed" class="sticky top-0 z-40 bg-[var(--color-surface)]/90 backdrop-blur-md border-b border-[var(--color-line)]">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-6">
          <router-link to="/" class="flex items-center gap-2.5 group">
            <span class="inline-flex h-7 w-7 items-center justify-center rounded bg-gradient-to-br from-[#5e6ad2] to-[#434eb0] text-white font-mono text-xs font-semibold shadow-inner">OP</span>
            <span class="font-medium tracking-tight text-sm text-[var(--color-ink)] group-hover:text-[#5e6ad2] transition-colors">{{ t('app') }}</span>
          </router-link>

          <nav class="hidden md:flex items-center gap-1 text-xs font-medium" aria-label="Primary">
            <router-link v-for="l in links" :key="l.to" :to="l.to"
              class="px-2.5 py-1.5 rounded text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] hover:bg-[var(--color-canvas-subtle)] transition-colors"
              active-class="!text-[var(--color-ink)] !bg-[var(--color-canvas-subtle)] !font-semibold">
              {{ t(l.key) }}
            </router-link>
          </nav>
        </div>

        <div class="flex items-center gap-3">
          <!-- Theme Toggle (Light / Dark) -->
          <button @click="toggleTheme"
            class="px-2 py-1 text-xs font-mono rounded border border-[var(--color-line)] bg-[var(--color-surface)] hover:bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] transition-colors flex items-center gap-1.5"
            :title="isDark ? 'Switch to Light' : 'Switch to Dark'">
            <span>{{ isDark ? '🌙' : '☀️' }}</span>
            <span class="text-[10px] hidden sm:inline uppercase">{{ isDark ? 'Dark' : 'Light' }}</span>
          </button>

          <!-- Segmented Language Switcher -->
          <div class="inline-flex rounded border border-[var(--color-line)] bg-[var(--color-surface)] p-0.5" role="group" :aria-label="t('language')">
            <button v-for="o in ['de','en']" :key="o" @click="setLang(o)"
              :class="['px-2 py-0.5 text-[11px] font-mono rounded transition-colors', lang===o ? 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink)] font-semibold shadow-xs' : 'text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]']">
              {{ o.toUpperCase() }}
            </button>
          </div>

          <div class="h-4 w-px bg-[var(--color-line)] hidden sm:block"></div>

          <div class="flex items-center gap-2">
            <span class="text-xs font-mono text-[var(--color-ink-soft)] hidden sm:inline">{{ auth.user?.username }}</span>
            <button @click="doLogout"
              class="px-2.5 py-1 text-xs text-[var(--color-ink-soft)] hover:text-[var(--color-rose)] hover:bg-[var(--color-rose-soft)] rounded transition-colors">
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from './stores/auth'

const { t, locale } = useI18n()
const auth = useAuth()
const router = useRouter()

const isDark = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('onboardpilot_theme')
  // Default is LIGHT unless user explicitly chose dark
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
