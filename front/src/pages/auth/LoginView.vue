<!-- src/pages/auth/LoginView.vue -->
<template>
  <div class="auth-page">
    <div class="auth-page-content">
      <div class="auth-container">
        <div class="auth-card">
        <div class="auth-header">
          <div class="auth-icon">🔐</div>
          <h1 class="auth-title">Вход</h1>
          <p class="auth-subtitle">Добро пожаловать обратно!</p>
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">
              <span class="label-icon">📧</span>
              <span>Email</span>
            </label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="admin@test.com"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <span class="label-icon">🔑</span>
              <span>Пароль</span>
            </label>
            <div class="password-input-wrapper">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="••••••••"
                class="form-input"
              />
              <label class="show-password-checkbox">
                <input
                  type="checkbox"
                  v-model="showPassword"
                  class="checkbox-input"
                />
                <span class="checkbox-label">Показать пароль</span>
              </label>
            </div>
          </div>

          <button 
            class="btn-submit" 
            type="submit" 
            :disabled="auth.loading"
          >
            <span v-if="!auth.loading">Войти</span>
            <span v-else class="loading-text">
              <span class="spinner"></span>
              Входим...
            </span>
          </button>

          <div v-if="auth.error" class="error-message">
            <span class="error-icon">⚠️</span>
            <span>{{ auth.error }}</span>
          </div>
        </form>

        <div class="auth-footer">
          <p class="hint">
            Нет аккаунта?
            <router-link :to="{ name: 'register' }" class="auth-link">
              Зарегистрироваться
            </router-link>
          </p>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const auth = useAuthStore()
const router = useRouter()

const handleSubmit = async () => {
  const ok = await auth.login({ email: email.value, password: password.value })
  if (ok) {
    const target = auth.getRedirectRouteByRole()
    router.push(target)
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.auth-page {
  min-height: 100vh;
  width: 100%;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  margin: 0;
  padding: 0;
}

.auth-page :deep(.top-navigation-bar) {
  position: relative;
  z-index: 1001;
}

.auth-page-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  position: relative;
  z-index: 1;
  width: 100%;
  box-sizing: border-box;
  min-height: calc(100vh - 80px);
}


.auth-container {
  width: 100%;
  max-width: 480px;
  position: relative;
  z-index: 1;
  margin: 0 auto;
  box-sizing: border-box;
}

.auth-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 48px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease-out;
  width: 100%;
  box-sizing: border-box;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.auth-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.auth-title {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: #FFFFFF;
  letter-spacing: -1px;
}

.auth-subtitle {
  font-size: 1rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  box-sizing: border-box;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.95rem;
}

.label-icon {
  font-size: 1.2rem;
}

.form-input {
  padding: 16px 20px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-input:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
  transform: translateY(-2px);
}

.password-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.show-password-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  user-select: none;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #FFD700;
}

.checkbox-label {
  cursor: pointer;
}

.btn-submit {
  margin-top: 8px;
  padding: 18px 24px;
  background: #FFD700;
  color: #1A1A1A;
  font-weight: 700;
  font-size: 1.05rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
  font-family: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
}

.btn-submit:hover:not(:disabled) {
  background: #FF8C00;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn-submit:active:not(:disabled) {
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 10px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(26, 26, 26, 0.2);
  border-top-color: #1A1A1A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(255, 68, 68, 0.2);
  border: 2px solid rgba(255, 68, 68, 0.4);
  border-radius: 8px;
  color: #ffaaaa;
  font-size: 0.95rem;
  font-weight: 500;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

.error-icon {
  font-size: 1.2rem;
}

.auth-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.hint {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
}

.auth-link {
  color: #FFD700;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.auth-link:hover {
  border-bottom-color: #FFD700;
  color: #FF8C00;
}

@media (max-width: 768px) {
  .auth-page-content {
    padding: 30px 16px;
    min-height: calc(100vh - 60px);
  }

  .auth-container {
    max-width: 100%;
  }

  .auth-card {
    padding: 36px 28px;
    border-radius: 12px;
    width: 100%;
  }

  .auth-icon {
    font-size: 3rem;
  }

  .auth-title {
    font-size: 2rem;
  }

  .auth-subtitle {
    font-size: 0.9rem;
  }

  .form-input {
    padding: 14px 18px;
    font-size: 0.95rem;
    width: 100%;
  }

  .btn-submit {
    padding: 16px 24px;
    font-size: 1rem;
    width: 100%;
  }
}

@media (max-width: 480px) {
  .auth-page-content {
    padding: 20px 12px;
  }

  .auth-card {
    padding: 28px 20px;
  }

  .auth-icon {
    font-size: 2.5rem;
  }

  .auth-title {
    font-size: 1.75rem;
  }

  .auth-subtitle {
    font-size: 0.85rem;
  }

  .form-input {
    padding: 12px 14px;
    font-size: 0.9rem;
  }

  .btn-submit {
    padding: 14px 20px;
    font-size: 0.95rem;
  }
}
</style>
