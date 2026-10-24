<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50">
    <div class="bg-white p-8 rounded-lg shadow w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center">OnboardPilot</h1>
      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm mb-1">{{ t('username') }}</label>
          <input v-model="username" class="w-full border rounded px-3 py-2" required />
        </div>
        <div>
          <label class="block text-sm mb-1">{{ t('password') }}</label>
          <input v-model="password" type="password" class="w-full border rounded px-3 py-2" required />
        </div>
        <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
        <button :disabled="loading" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          {{ loading ? '...' : t('login') }}
        </button>
      </form>
      <div class="mt-4 text-xs text-slate-500">
        <p>Demo: admin / Admin123!</p>
        <p>manager / Manager123!</p>
        <p>employee / Employee123!</p>
      </div>
      <router-link to="/public-demo" class="block text-center mt-4 text-blue-600 text-sm">{{ t('public_demo') }}</router-link>
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
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
