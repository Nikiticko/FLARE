// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { useAuthStore } from './stores/auth'

// Установка favicon при загрузке приложения
const setFavicon = () => {
  let favicon = document.querySelector("link[rel='icon']")
  if (!favicon) {
    favicon = document.createElement('link')
    favicon.rel = 'icon'
    favicon.type = 'image/png'
    document.head.appendChild(favicon)
  }
  // Добавляем версию для обхода кэша
  favicon.href = '/logo.png?' + Date.now()
  // Удаляем версию после первой загрузки
  setTimeout(() => {
    favicon.href = '/logo.png'
  }, 100)
}

setFavicon()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// если есть токен в localStorage — сразу пытаемся подтянуть пользователя
const auth = useAuthStore(pinia)
if (auth.access && !auth.user) {
  auth.fetchMe()
}

app.mount('#app')
