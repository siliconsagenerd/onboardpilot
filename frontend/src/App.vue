<template>
  <div class="min-h-screen bg-canvas text-ink">
    <header v-if="auth.isAuthed" class="sticky top-0 z-20 bg-canvas/80 backdrop-blur border-b border-line">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
        <router-link to="/" class="flex items-center gap-2 group">
          <span class="inline-flex h-8 w-8 items-center justify-center rounded-md bg-ink text-canvas font-mono text-sm font-semibold">OP</span>
          <span class="font-semibold tracking-tight">{{ t('app') }}</span>
        </router-link>
        <nav class="flex items-center gap-1 text-sm flex-wrap" aria-label="Primary">
          <router-link v-for="l in links" :key="l.to" :to="l.to"
            class="px-3 py-1.5 rounded-md text-ink-soft hover:text-ink hover:bg-surface-2 transition-colors"
            active-class="!text-ink !bg-surface !border !border-line">
            {{ t(l.key) }}
          </router-link>
        </nav>
        <div class="flex items-center gap-3">
          <div class="inline-flex rounded-md border border-line bg-surface p-0.5" role="group" :aria-label="t('language')">
            <button v-for="o in ['de','en']" :key="o" @click="setLang(o)"
              :class="['px-2.5 py-1 text-xs font-medium rounded transition-colors', lang===o?'bg-ink text-canvas':'text-ink-soft hover:text-ink']">
              {{ o.toUpperCase() }}
            </button>
          </div>
          <button @click="doLogout" class="text-sm text-muted hover:text-danger transition-colors">{{ t('logout') }}</button>
        </div>
      </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
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

const lang = computed(() => locale.value)
const links = [
  { to: '/', key: 'dashboard' },
  { to: '/cases', key: 'cases' },
  { to: '/guides', key: 'guides' },
  { to: '/public-demo', key: 'public_demo' },
]

function setLang(v: string) { locale.value = v; localStorage.setItem('lang', v) }
function doLogout() { auth.logout(); router.push('/login') }
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
