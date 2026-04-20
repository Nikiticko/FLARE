import axios from 'axios'

const resolveDefaultApiBaseUrl = () => {
  if (!import.meta.env.DEV) {
    return '/api'
  }

  if (typeof window === 'undefined') {
    return 'http://127.0.0.1:8000/api'
  }

  const { protocol, hostname } = window.location
  return `${protocol}//${hostname}:8000/api`
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || resolveDefaultApiBaseUrl()

const getRefreshURL = () => `${API_BASE_URL}/token/refresh/`
const getCsrfURL = () => `${API_BASE_URL}/auth/csrf/`
const AUTH_SESSION_COOKIE = 'auth_session'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

const readCookie = (name) => {
  if (typeof document === 'undefined') {
    return null
  }

  const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const match = document.cookie.match(new RegExp(`(?:^|; )${escapedName}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

export const hasAuthSessionMarker = () => readCookie(AUTH_SESSION_COOKIE) === '1'

let csrfRequest = null

export async function ensureCsrfCookie() {
  const existing = readCookie('csrftoken')
  if (existing) {
    return existing
  }

  if (!csrfRequest) {
    csrfRequest = axios.get(getCsrfURL(), { withCredentials: true })
      .finally(() => {
        csrfRequest = null
      })
  }

  await csrfRequest
  return readCookie('csrftoken')
}

apiClient.interceptors.request.use(async (config) => {
  const method = String(config.method || 'get').toUpperCase()
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrfToken = readCookie('csrftoken') || await ensureCsrfCookie()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }

  return config
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve()
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const requestUrl = String(originalRequest?.url || '')
    const shouldTryRefresh =
      error.response?.status === 401 &&
      originalRequest &&
      hasAuthSessionMarker() &&
      !originalRequest._retry &&
      !requestUrl.includes('/auth/login/') &&
      !requestUrl.includes('/auth/register/') &&
      !requestUrl.includes('/auth/admin-login/') &&
      !requestUrl.includes('/auth/logout/') &&
      !requestUrl.includes('/token/refresh/')

    if (shouldTryRefresh) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => apiClient(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await ensureCsrfCookie()
        const csrfToken = readCookie('csrftoken')
        const headers = csrfToken ? { 'X-CSRFToken': csrfToken } : undefined
        await axios.post(getRefreshURL(), {}, { withCredentials: true, headers })
        processQueue(null)
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)
        if (typeof window !== 'undefined' && window.location) {
          const currentPath = window.location.pathname
          if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
            setTimeout(() => {
              window.location.href = '/login'
            }, 100)
          }
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
