import { defineStore } from 'pinia'
import { api } from '../api/client'

export const useAuth = defineStore('auth', {
  state: () => ({ token: localStorage.getItem('token') || '', user: null as any, role: localStorage.getItem('role') || '' }),
  getters: { isAuthed: (s) => !!s.token },
  actions: {
    async login(username: string, password: string) {
      const r = await api.post('/api/auth/login', { username, password })
      this.token = r.data.access_token
      this.role = r.data.role
      localStorage.setItem('token', this.token)
      localStorage.setItem('role', this.role)
      const me = await api.get('/api/auth/me')
      this.user = me.data
      return r.data
    },
    logout() {
      this.token = ''
      this.user = null
      this.role = ''
      localStorage.removeItem('token')
      localStorage.removeItem('role')
    }
  }
})
