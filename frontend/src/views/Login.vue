<template>
  <div class="min-h-screen grid place-items-center bg-[var(--color-canvas)] px-4 transition-colors relative">
    <!-- Top-right corner quick controls (Theme & Language) -->
    <div class="absolute top-4 right-4 flex items-center gap-2">
      <!-- Theme toggle -->
      <button @click="toggleTheme"
        class="px-2.5 py-1 text-xs font-mono rounded border border-[var(--color-line)] bg-[var(--color-surface)] hover:bg-[var(--color-canvas-subtle)] text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] transition-colors flex items-center gap-1.5 shadow-xs cursor-pointer"
        :title="isDark ? t('theme_light') : t('theme_dark')"
        :aria-label="t('theme')">
        <svg v-if="isDark" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
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
        <svg v-else class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
        <span class="text-[11px] font-semibold">{{ isDark ? t('theme_dark') : t('theme_light') }}</span>
      </button>

      <!-- Language Switcher -->
      <div class="inline-flex rounded border border-[var(--color-line)] bg-[var(--color-surface)] p-0.5 shadow-xs" role="group" :aria-label="t('language')">
        <button v-for="o in ['de','en']" :key="o" @click="setLang(o)"
          :class="['px-2 py-0.5 text-[11px] font-mono rounded transition-colors cursor-pointer', lang===o ? 'bg-[var(--color-canvas-subtle)] text-[var(--color-ink)] font-semibold' : 'text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]']">
          {{ o.toUpperCase() }}
        </button>
      </div>
    </div>

    <div class="w-full max-w-sm panel p-7 relative">
      <!-- Glow effect -->
      <div class="absolute -top-12 left-1/2 -translate-x-1/2 w-48 h-24 bg-[var(--color-accent)]/15 blur-3xl pointer-events-none rounded-full"></div>

      <div class="flex items-center gap-3 mb-6 relative">
        <span class="inline-flex h-9 w-9 items-center justify-center rounded bg-gradient-to-br from-[#5e6ad2] to-[#434eb0] text-white font-mono text-xs font-semibold shadow-inner">OP</span>
        <div>
          <h1 class="text-sm font-semibold tracking-tight text-[var(--color-ink)]">{{ t('app') }}</h1>
          <p class="text-xs text-[var(--color-ink-soft)] font-mono">console access</p>
        </div>
      </div>

      <form @submit.prevent="submit" class="space-y-4 relative">
        <label class="block">
          <span class="text-xs font-medium font-mono text-[var(--color-ink-soft)]">{{ t('username') }}</span>
          <input v-model="username" type="text" autocomplete="username" required
            class="mt-1 w-full linear-input px-3 py-2 text-xs" />
        </label>
        <label class="block">
          <span class="text-xs font-medium font-mono text-[var(--color-ink-soft)]">{{ t('password') }}</span>
          <input v-model="password" type="password" autocomplete="current-password" required
            class="mt-1 w-full linear-input px-3 py-2 text-xs" />
        </label>
        <p v-if="error" class="text-xs font-mono text-[var(--color-rose)] bg-[var(--color-rose-soft)] border border-[var(--color-rose)]/20 p-2 rounded" role="alert">{{ error }}</p>
        <button :disabled="loading" type="submit"
          class="w-full rounded bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white py-2 text-xs font-medium disabled:opacity-50 transition-colors shadow-xs cursor-pointer">
          {{ loading ? '…' : t('login') }}
        </button>
      </form>

      <div class="mt-6 pt-4 border-t border-[var(--color-line)] relative">
        <p class="text-[11px] font-mono text-[var(--color-ink-soft)] mb-2">{{ t('demo_credentials') }}</p>
        <div class="space-y-1 text-[11px] font-mono text-[var(--color-muted)]">
          <p>admin / secret</p>
          <p>manager / secret</p>
          <p>viewer / secret</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const username = ref('admin')
const password = ref('secret')
const loading = ref(false)
const error = ref('')

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

const auth = useAuth()
const router = useRouter()

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('invalid_credentials')
  } finally {
    loading.value = false
  }
}
</script>
