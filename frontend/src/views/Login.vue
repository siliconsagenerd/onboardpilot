<template>
  <div class="min-h-screen grid place-items-center bg-canvas px-4">
    <div class="w-full max-w-md card p-8">
      <div class="flex items-center gap-3 mb-6">
        <span class="inline-flex h-10 w-10 items-center justify-center rounded-md bg-ink text-canvas font-mono text-sm font-semibold">OP</span>
        <div>
          <h1 class="text-xl font-semibold tracking-tight">{{ t('app') }}</h1>
          <p class="text-sm text-muted">{{ t('login') }}</p>
        </div>
      </div>
      <form @submit.prevent="submit" class="space-y-4">
        <label class="block">
          <span class="text-sm font-medium text-ink-soft">{{ t('username') }}</span>
          <input v-model="username" type="text" autocomplete="username" required
            class="mt-1 w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none" />
        </label>
        <label class="block">
          <span class="text-sm font-medium text-ink-soft">{{ t('password') }}</span>
          <input v-model="password" type="password" autocomplete="current-password" required
            class="mt-1 w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus:border-accent focus:ring-2 focus:ring-accent/20 outline-none" />
        </label>
        <p v-if="error" class="text-sm text-danger" role="alert">{{ error }}</p>
        <button :disabled="loading" type="submit"
          class="w-full rounded-md bg-ink text-canvas py-2.5 text-sm font-medium hover:bg-ink-soft disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {{ loading ? '…' : t('login') }}
        </button>
      </form>
      <div class="mt-6 pt-4 border-t border-line">
        <p class="text-xs text-muted mb-2">{{ t('demo_credentials') }}</p>
        <ul class="text-xs text-ink-soft space-y-0.5 font-mono">
          <li>admin / Admin123!</li>
          <li>manager / Manager123!</li>
          <li>employee / Employee123!</li>
        </ul>
      </div>
      <router-link to="/public-demo" class="block text-center mt-4 text-sm text-accent hover:underline">
        {{ t('public_demo') }}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import { useI18n } from 'vue-i18n'

const auth = useAuth()
const router = useRouter()
const { t } = useI18n()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    if (auth.role === 'employee') router.push('/cases')
    else router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('failed_login')
  } finally {
    loading.value = false
  }
}
</script>
