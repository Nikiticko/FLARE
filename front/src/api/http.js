// src/api/http.js
import axios from 'axios'

// Используем переменную окружения или дефолтное значение для dev режима
// В dev режиме: VITE_API_BASE_URL=http://127.0.0.1:8000/api (или будет использован дефолт)
// В prod: /api (будет проксироваться через Nginx)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://127.0.0.1:8000/api' : '/api')

// Для refresh токена используем тот же baseURL, что и для основного apiClient
const getRefreshURL = () => {
  return `${API_BASE_URL}/token/refresh/`
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
})

// подставляем access-токен из localStorage
apiClient.interceptors.request.use((config) => {
  const access = localStorage.getItem('access')
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})

// Обработка 401 ошибок - автоматическое обновление токена
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Если ошибка 401 и это не запрос на обновление токена
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Если уже идет обновление токена, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refresh = localStorage.getItem('refresh')
      if (!refresh) {
        // Нет refresh токена - очищаем все и выходим
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        processQueue(error, null)
        isRefreshing = false
        
        // Редиректим на страницу логина, если не на странице логина/регистрации
        if (typeof window !== 'undefined' && window.location) {
          const currentPath = window.location.pathname
          if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
            setTimeout(() => {
              window.location.href = '/login'
            }, 100)
          }
        }
        
        return Promise.reject(error)
      }

      try {
        // Пытаемся обновить токен
        // Используем прямой axios, чтобы избежать перехвата через interceptor
        const response = await axios.post(
          getRefreshURL(),
          { refresh }
        )
        
        const { access } = response.data
        localStorage.setItem('access', access)
        
        // Обновляем заголовок в оригинальном запросе
        originalRequest.headers.Authorization = `Bearer ${access}`
        
        // Обрабатываем очередь
        processQueue(null, access)
        isRefreshing = false
        
        // Повторяем оригинальный запрос
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Не удалось обновить токен - очищаем все
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        processQueue(refreshError, null)
        isRefreshing = false
        
        // Обновляем состояние auth store, если он доступен
        // Используем динамический импорт, чтобы избежать циклических зависимостей
        if (typeof window !== 'undefined' && window.location) {
          // Редиректим на страницу логина только если мы не на странице логина/регистрации
          const currentPath = window.location.pathname
          if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
            // Используем setTimeout, чтобы избежать проблем с навигацией во время обработки ошибки
            setTimeout(() => {
              window.location.href = '/login'
            }, 100)
          }
        }
        
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
