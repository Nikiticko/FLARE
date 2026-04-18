<template>
  <transition name="cookie-banner">
    <aside v-if="visible" class="cookie-banner">
      <div class="cookie-banner__content">
        <p class="cookie-banner__text">
          Сайт использует обязательные cookie для входа, защиты форм и сохранения сессии.
          Продолжая использование сайта, вы соглашаетесь с их применением.
        </p>
        <div class="cookie-banner__actions">
          <RouterLink :to="{ name: 'cookie-policy' }" class="cookie-banner__link">
            Политика cookie
          </RouterLink>
          <button type="button" class="cookie-banner__button" @click="accept">
            Понятно
          </button>
        </div>
      </div>
    </aside>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const STORAGE_KEY = 'cookie_notice_accepted_v1'
const visible = ref(typeof window !== 'undefined' && window.localStorage.getItem(STORAGE_KEY) !== '1')

const accept = () => {
  window.localStorage.setItem(STORAGE_KEY, '1')
  visible.value = false
}
</script>

<style scoped>
.cookie-banner {
  position: fixed;
  left: 20px;
  right: 20px;
  bottom: 20px;
  z-index: 1300;
  display: flex;
  justify-content: center;
}

.cookie-banner__content {
  width: min(920px, 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 20px;
  border-radius: 16px;
  background: rgba(22, 22, 22, 0.96);
  border: 1px solid rgba(255, 215, 0, 0.35);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(18px);
}

.cookie-banner__text {
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  font-size: 0.95rem;
  line-height: 1.5;
}

.cookie-banner__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.cookie-banner__link {
  color: #ffd700;
  text-decoration: none;
  font-weight: 700;
}

.cookie-banner__button {
  border: none;
  border-radius: 10px;
  padding: 11px 16px;
  background: #ffd700;
  color: #141414;
  font-weight: 800;
  cursor: pointer;
}

.cookie-banner__button:hover {
  background: #ffc700;
}

.cookie-banner-enter-active,
.cookie-banner-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.cookie-banner-enter-from,
.cookie-banner-leave-to {
  opacity: 0;
  transform: translateY(16px);
}

@media (max-width: 768px) {
  .cookie-banner {
    left: 12px;
    right: 12px;
    bottom: 12px;
  }

  .cookie-banner__content {
    flex-direction: column;
    align-items: stretch;
  }

  .cookie-banner__actions {
    justify-content: space-between;
  }
}
</style>
