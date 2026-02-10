// src/stores/auth.js
import { defineStore } from 'pinia'
import { loginApi, getMeApi, registerApi } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    user: null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.access,
    role: (state) => state.user?.role || null,
    normalizedRole() {
      return this.role ? String(this.role).toLowerCase() : null
    },
  },

  actions: {
    async login({ email, password }) {
      this.loading = true
      this.error = null
      try {
        const { data } = await loginApi({ email, password })

        // ВАЖНО: бэк возвращает { user, tokens }, а не { access, refresh }
        this.access = data.tokens.access
        this.refresh = data.tokens.refresh || null

        localStorage.setItem('access', this.access)
        if (this.refresh) {
          localStorage.setItem('refresh', this.refresh)
        }

        await this.fetchMe()
        return true
      } catch (err) {
        console.error('Login error:', err)
        this.error =
          err?.response?.data?.detail ||
          err?.response?.data?.error ||
          'Ошибка авторизации'
        this.access = null
        this.refresh = null
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        return false
      } finally {
        this.loading = false
      }
    },

    // регистрация + автологин
    async register(payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await registerApi(payload)

        // tokens и пользователь приходят сразу
        this.access = data.tokens?.access || null
        this.refresh = data.tokens?.refresh || null
        this.user = data.user || null

        if (this.access) {
          localStorage.setItem('access', this.access)
        }
        if (this.refresh) {
          localStorage.setItem('refresh', this.refresh)
        }

        return true
      } catch (err) {
        console.error('Register error:', err)

        if (err?.response?.data) {
          const d = err.response.data
          if (typeof d === 'string') {
            this.error = d
          } else if (d.detail || d.error) {
            this.error = d.detail || d.error
          } else {
            // собираем сообщения валидаторов в одну строку
            const msgs = []
            for (const key in d) {
              const val = d[key]
              if (Array.isArray(val)) {
                msgs.push(val.join(' '))
              } else if (typeof val === 'string') {
                msgs.push(val)
              }
            }
            this.error = msgs.join(' ') || 'Ошибка регистрации'
          }
        } else {
          this.error = 'Ошибка регистрации'
        }

        this.access = null
        this.refresh = null
        this.user = null
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        return false
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      if (!this.access) return
      try {
        const { data } = await getMeApi()
        this.user = data
        // Обновляем access токен из localStorage на случай, если он был обновлен interceptor'ом
        const currentAccess = localStorage.getItem('access')
        if (currentAccess && currentAccess !== this.access) {
          this.access = currentAccess
        }
      } catch (err) {
        // Не логируем пользователя при 401, если токен был обновлен автоматически
        // Interceptor в http.js уже обработает обновление токена
        if (err?.response?.status === 401) {
          // Если после обновления токена все еще 401, значит токен невалидный
          // Проверяем, есть ли еще access токен (возможно он был обновлен)
          const currentAccess = localStorage.getItem('access')
          if (!currentAccess || currentAccess === this.access) {
            // Токен не был обновлен, значит он невалидный - выходим
            console.error('fetchMe error: Invalid token, logging out')
            this.logout()
          } else {
            // Токен был обновлен, обновляем его в store
            this.access = currentAccess
            // Пытаемся снова получить данные пользователя
            try {
              const { data } = await getMeApi()
              this.user = data
            } catch (retryErr) {
              // Если и после обновления токена не получилось, выходим
              console.error('fetchMe retry error:', retryErr)
              this.logout()
            }
          }
        } else {
          console.error('fetchMe error:', err)
          // Для других ошибок не выходим автоматически
        }
      }
    },

    logout() {
      this.access = null
      this.refresh = null
      this.user = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    },

    // маршрут, куда редиректить в зависимости от роли
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
