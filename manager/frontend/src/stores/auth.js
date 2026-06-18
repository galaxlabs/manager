import { defineStore } from 'pinia'
import { frappeCall } from '@/api/frappe'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.user,
    fullName: (state) => state.user?.full_name || '',
  },
  actions: {
    async login(usr, pwd) {
      const res = await frappeCall('login', { usr, pwd })
      this.user = res.message
      this.token = localStorage.getItem('token')
      return res
    },
    async checkSession() {
      try {
        const res = await frappeCall('frappe.auth.get_logged_user')
        this.user = res.message
        return true
      } catch {
        this.clear()
        return false
      }
    },
    clear() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    },
  },
})
