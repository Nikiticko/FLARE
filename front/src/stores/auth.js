import { defineStore } from 'pinia'
import { loginApi, getMeApi, registerApi, logoutApi, getCsrfApi } from '../api/auth'
import { hasAuthSessionMarker } from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
    initialized: false,
    initPromise: null,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    role: (state) => state.user?.role || null,
    normalizedRole() {
      return this.role ? String(this.role).toLowerCase() : null
    },
  },

  actions: {
    async initialize() {
      if (this.initialized) {
        return
      }

      if (this.initPromise) {
        await this.initPromise
        return
      }

      this.initPromise = (async () => {
        this.loading = true
        try {
          await getCsrfApi()
          if (hasAuthSessionMarker()) {
            await this.fetchMe()
          }
        } catch (err) {
          if (err?.response?.status !== 401) {
            console.error('Auth initialize error:', err)
          }
        } finally {
          this.initialized = true
          this.loading = false
          this.initPromise = null
        }
      })()

      await this.initPromise
    },

    async login({ email, password }) {
      this.loading = true
      this.error = null
      try {
        const { data } = await loginApi({ email, password })
        this.user = data.user || null
        this.initialized = true

        if (!this.user) {
          await this.fetchMe()
        }
        return true
      } catch (err) {
        console.error('Login error:', err)
        this.error =
          err?.response?.data?.detail ||
          err?.response?.data?.error ||
          'Ошибка авторизации'
        this.user = null
        this.initialized = true
        return false
      } finally {
        this.loading = false
      }
    },

    async register(payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await registerApi(payload)
        this.user = data.user || null
        this.initialized = true

        if (!this.user) {
          await this.fetchMe()
        }
        return true
      } catch (err) {
        console.error('Register error:', err)

        if (err?.response?.data) {
          const data = err.response.data
          if (typeof data === 'string') {
            this.error = data
          } else if (data.detail || data.error) {
            this.error = data.detail || data.error
          } else {
            const messages = []
            for (const key in data) {
              const value = data[key]
              if (Array.isArray(value)) {
                messages.push(value.join(' '))
              } else if (typeof value === 'string') {
                messages.push(value)
              }
            }
            this.error = messages.join(' ') || 'Ошибка регистрации'
          }
        } else {
          this.error = 'Ошибка регистрации'
        }

        this.user = null
        this.initialized = true
        return false
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      const { data } = await getMeApi()
      this.user = data
      return data
    },

    async logout() {
      try {
        await logoutApi()
      } catch (err) {
        if (err?.response?.status !== 401 && err?.response?.status !== 403) {
          console.error('Logout error:', err)
        }
      } finally {
        this.user = null
        this.error = null
        this.initialized = true
      }
    },

    getRedirectRouteByRole() {
      switch (this.normalizedRole) {
        case 'admin':
          return { name: 'admin-dashboard' }
        case 'manager':
          return { name: 'manager-balance' }
        case 'teacher':
          return { name: 'teacher-students' }
        case 'student':
          return { name: 'dashboard' }
        case 'applicant':
          return { name: 'dashboard' }
        default:
          return { name: 'home' }
      }
    },
  },
})
