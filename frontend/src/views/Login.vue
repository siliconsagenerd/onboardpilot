<template>
  <div class="min-h-screen grid md:grid-cols-2 bg-[var(--color-canvas)] transition-colors">
    <aside class="relative hidden md:flex flex-col justify-between p-10 lg:p-14 bg-[var(--color-surface-elevated)] border-r border-[var(--color-line)] overflow-hidden">
      <div class="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-[var(--color-accent-soft)] blur-3xl" aria-hidden="true"></div>
      <div class="absolute bottom-0 right-0 h-64 w-64 rounded-full bg-[var(--color-secondary-soft)] blur-3xl" aria-hidden="true"></div>

      <div class="relative flex items-center gap-3">
        <span class="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--color-accent)] text-[#ffffff] text-base font-bold shadow-sm">OP</span>
        <div>
          <p class="font-bold tracking-tight text-lg text-[var(--color-ink)]">{{ t('app') }}</p>
          <p class="text-xs font-mono text-[var(--color-ink-soft)]">{{ t('it_ops_console') }}</p>
        </div>
      </div>

      <div class="relative space-y-6">
        <h1 class="text-4xl lg:text-5xl font-bold tracking-tight text-[var(--color-ink)] leading-[1.05]">
          {{ t('onboard_starters') }}
        </h1>
        <p class="text-base text-[var(--color-ink-soft)] max-w-md leading-relaxed">
          {{ t('checklist_deps_desc') }}
        </p>
        <div class="flex flex-wrap gap-2">
          <span class="status-badge bg-[var(--color-accent-soft)] text-[var(--color-accent)]">{{ t('it_admin') }}</span>
          <span class="status-badge bg-[var(--color-secondary-soft)] text-[var(--color-secondary)]">{{ t('manager_role') }}</span>
          <span class="status-badge bg-[var(--color-emerald-soft)] text-[var(--color-emerald)]">{{ t('new_employee') }}</span>
        </div>
      </div>

      <p class="relative text-xs font-mono text-[var(--color-muted)]">© OnboardPilot · synthetic demo data only</p>
    </aside>

    <main class="flex items-center justify-center px-4 py-10 sm:px-8 relative">
      <div class="absolute top-4 right-4 flex items-center gap-2">
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
        </button>

        <div class="inline-flex rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-0.5 shadow-sm" role="group" :aria-label="t('language')">
          <button v-for="o in ['de','en']" :key="o" @click="setLang(o)"
            :class="['px-2.5 py-1 text-xs font-mono rounded-md transition-colors cursor-pointer', lang===o ? 'bg-[var(--color-accent)] text-[#ffffff] font-semibold shadow-sm' : 'text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]']">
            {{ o.toUpperCase() }}
          </button>
        </div>
      </div>

      <div class="w-full max-w-sm">
        <div class="md:hidden flex items-center gap-3 mb-8">
          <span class="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--color-accent)] text-[#ffffff] text-base font-bold shadow-sm">OP</span>
          <div>
            <p class="font-bold tracking-tight text-lg text-[var(--color-ink)]">{{ t('app') }}</p>
            <p class="text-xs font-mono text-[var(--color-ink-soft)]">{{ t('it_ops_console') }}</p>
          </div>
        </div>

        <div class="panel p-8 relative">
          <div class="absolute top-0 left-0 right-0 h-1 bg-[var(--color-accent)] rounded-t-[var(--radius-md)]"></div>

          <h2 class="text-2xl font-bold tracking-tight text-[var(--color-ink)] mb-1">{{ t('login') }}</h2>
          <p class="text-sm text-[var(--color-ink-soft)] mb-6">{{ t('sign_in_continue') }}</p>

          <form @submit.prevent="submit" class="space-y-5">
            <label class="block">
              <span class="text-xs font-semibold font-mono text-[var(--color-ink-soft)] uppercase tracking-wider">{{ t('username') }}</span>
              <input v-model="username" type="text" autocomplete="username" required
                class="mt-2 w-full linear-input px-3 py-2.5 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold font-mono text-[var(--color-ink-soft)] uppercase tracking-wider">{{ t('password') }}</span>
              <input v-model="password" type="password" autocomplete="current-password" required
                class="mt-2 w-full linear-input px-3 py-2.5 text-sm" />
            </label>
            <p v-if="error" class="text-xs font-mono text-[var(--color-rose)] bg-[var(--color-rose-soft)] border border-[var(--color-rose)]/30 p-3 rounded-lg" role="alert">{{ error }}</p>
            <button :disabled="loading" type="submit"
              class="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none">
              {{ loading ? '...' : t('login') }}
            </button>
          </form>

          <div class="mt-8 pt-5 border-t border-[var(--color-line)]">
            <p class="text-xs font-mono text-[var(--color-ink-soft)] mb-3 uppercase tracking-wider">{{ t('demo_credentials') }}</p>
            <div class="space-y-1.5 text-xs font-mono text-[var(--color-muted)]">
              <p>admin / Admin123!</p>
              <p>manager / Manager123!</p>
              <p>employee / Employee123!</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const username = ref('admin')
const password = ref('Admin123!')
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
