<template>
  <div class="min-h-screen grid place-items-center bg-[#08090a] px-4">
    <div class="w-full max-w-sm panel p-7 relative">
      <!-- Glow effect -->
      <div class="absolute -top-12 left-1/2 -translate-x-1/2 w-48 h-24 bg-[#5e6ad2]/20 blur-3xl pointer-events-none rounded-full"></div>

      <div class="flex items-center gap-3 mb-6 relative">
        <span class="inline-flex h-9 w-9 items-center justify-center rounded bg-gradient-to-br from-[#5e6ad2] to-[#434eb0] text-white font-mono text-xs font-semibold shadow-inner">OP</span>
        <div>
          <h1 class="text-sm font-semibold tracking-tight text-[#f7f8f8]">{{ t('app') }}</h1>
          <p class="text-xs text-[#8a8f98] font-mono">console access</p>
        </div>
      </div>

      <form @submit.prevent="submit" class="space-y-4 relative">
        <label class="block">
          <span class="text-xs font-medium font-mono text-[#8a8f98]">{{ t('username') }}</span>
          <input v-model="username" type="text" autocomplete="username" required
            class="mt-1 w-full linear-input px-3 py-2 text-xs" />
        </label>
        <label class="block">
          <span class="text-xs font-medium font-mono text-[#8a8f98]">{{ t('password') }}</span>
          <input v-model="password" type="password" autocomplete="current-password" required
            class="mt-1 w-full linear-input px-3 py-2 text-xs" />
        </label>
        <p v-if="error" class="text-xs font-mono text-[#f43f5e] bg-[#f43f5e]/10 border border-[#f43f5e]/20 p-2 rounded" role="alert">{{ error }}</p>
        <button :disabled="loading" type="submit"
          class="w-full rounded bg-[#5e6ad2] hover:bg-[#6875e5] text-white py-2 text-xs font-medium disabled:opacity-50 transition-colors shadow-sm cursor-pointer">
          {{ loading ? '…' : t('login') }}
        </button>
      </form>

      <div class="mt-6 pt-4 border-t border-white/[0.08] relative">
        <p class="text-[11px] font-mono text-[#8a8f98] mb-2">{{ t('demo_credentials') }}</p>
        <div class="space-y-1 text-[11px] font-mono text-[#62666d]">
          <p>admin / secret</p>
          <p>manager / secret</p>
          <p>viewer / secret</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const username = ref('admin')
const password = ref('secret')
const loading = ref(false)
const error = ref('')

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
