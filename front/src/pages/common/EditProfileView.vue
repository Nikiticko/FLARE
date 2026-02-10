<!-- src/pages/common/EditProfileView.vue -->
<template>
  <div class="edit-profile">
    <div class="profile-content">
      <div class="page-header">
        <h1>Редактирование профиля</h1>
      </div>
      <div class="profile-form card">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              placeholder="example@mail.com"
            />
          </div>

          <div class="form-group">
            <label for="phone">Телефон</label>
            <input
              id="phone"
              v-model="formData.phone"
              type="text"
              placeholder="+7..."
            />
          </div>

          <div class="form-group">
            <label for="student_full_name">ФИО ученика</label>
            <input
              id="student_full_name"
              v-model="formData.student_full_name"
              type="text"
              placeholder="Иванов Иван Иванович"
            />
          </div>

          <div class="form-group">
            <label for="parent_full_name">ФИО родителя</label>
            <input
              id="parent_full_name"
              v-model="formData.parent_full_name"
              type="text"
              placeholder="Иванова Мария Петровна"
            />
          </div>

          <!-- Смена пароля -->
          <div class="password-section">
            <button
              type="button"
              class="btn-change-password"
              @click="togglePasswordForm"
            >
              {{ showPasswordForm ? 'Скрыть' : 'Изменить пароль' }}
            </button>
            <div v-if="showPasswordForm" class="password-form">
              <div class="form-group">
                <label for="old_password">Текущий пароль</label>
                <div class="password-row" :class="{ 'password-verified': oldPasswordVerified }">
                  <div class="password-row-top">
                    <input
                      id="old_password"
                      v-model="passwordForm.old_password"
                      :type="showOldPassword ? 'text' : 'password'"
                      placeholder="Введите текущий пароль"
                      :disabled="oldPasswordVerified"
                    />
                    <button
                      type="button"
                      class="btn-verify"
                      :disabled="verifyLoading || oldPasswordVerified || !passwordForm.old_password"
                      @click="handleVerifyPassword"
                    >
                      {{ verifyLoading ? '...' : (oldPasswordVerified ? '✓' : 'Проверить') }}
                    </button>
                  </div>
                  <label class="show-password-checkbox">
                    <input type="checkbox" v-model="showOldPassword" class="checkbox-input" />
                    <span class="checkbox-label">Показать пароль</span>
                  </label>
                </div>
              </div>
              <div class="form-group">
                <label for="new_password">Новый пароль</label>
                <div class="password-row">
                  <input
                    id="new_password"
                    v-model="passwordForm.new_password"
                    :type="showNewPassword ? 'text' : 'password'"
                    minlength="8"
                    placeholder="Минимум 8 символов"
                    :disabled="!oldPasswordVerified"
                  />
                  <label class="show-password-checkbox">
                    <input type="checkbox" v-model="showNewPassword" class="checkbox-input" />
                    <span class="checkbox-label">Показать пароль</span>
                  </label>
                </div>
              </div>
              <button
                type="button"
                class="btn-save-password"
                :disabled="passwordLoading || !oldPasswordVerified || !passwordForm.new_password || passwordForm.new_password.length < 8"
                @click="handleChangePassword"
              >
                {{ passwordLoading ? 'Сохранение...' : 'Сохранить новый пароль' }}
              </button>
              <p v-if="passwordError" class="error-message">{{ passwordError }}</p>
              <p v-if="passwordSuccess" class="success-message">{{ passwordSuccess }}</p>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="loading">
              {{ loading ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <router-link :to="cancelRoute" class="btn-cancel">
              Отмена
            </router-link>
          </div>

          <p v-if="error" class="error-message">
            {{ error }}
          </p>

          <p v-if="success" class="success-message">
            Профиль успешно обновлен!
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import { updateMeApi, changePasswordApi, verifyPasswordApi } from '../../api/auth'

const auth = useAuthStore()
const router = useRouter()

const cancelRoute = computed(() => {
  const role = auth.normalizedRole
  if (role === 'student' || role === 'applicant' || role === 'teacher' || role === 'manager' || role === 'admin') {
    return { name: 'dashboard' }
  }
  return { name: 'home' }
})

const formData = ref({
  email: '',
  phone: '',
  student_full_name: '',
  parent_full_name: ''
})

const loading = ref(false)
const error = ref(null)
const success = ref(false)

const showPasswordForm = ref(false)
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const passwordForm = ref({ old_password: '', new_password: '' })
const oldPasswordVerified = ref(false)
const verifyLoading = ref(false)
const passwordLoading = ref(false)
const passwordError = ref(null)
const passwordSuccess = ref(null)

const loadProfile = async () => {
  if (!auth.user && auth.isAuthenticated) {
    await auth.fetchMe()
  }
  
  if (auth.user) {
    formData.value = {
      email: auth.user.email || '',
      phone: auth.user.phone || '',
      student_full_name: auth.user.student_full_name || '',
      parent_full_name: auth.user.parent_full_name || ''
    }
  }
}

const handleSubmit = async () => {
  loading.value = true
  error.value = null
  success.value = false

  try {
    const { data } = await updateMeApi(formData.value)
    
    // Обновляем данные в store
    await auth.fetchMe()
    
    success.value = true
    
    // Через 2 секунды перенаправляем в личный кабинет
    setTimeout(() => {
      const role = auth.normalizedRole
      if (role === 'student' || role === 'applicant' || role === 'teacher' || role === 'manager' || role === 'admin') {
        router.push({ name: 'dashboard' })
      } else {
        router.push({ name: 'home' })
      }
    }, 2000)
  } catch (err) {
    console.error('Ошибка обновления профиля:', err)
    
    if (err?.response?.data) {
      const data = err.response.data
      if (typeof data === 'string') {
        error.value = data
      } else if (data.detail) {
        error.value = data.detail
      } else if (data.email) {
        error.value = Array.isArray(data.email) ? data.email[0] : data.email
      } else {
        const messages = []
        for (const key in data) {
          const val = data[key]
          if (Array.isArray(val)) {
            messages.push(val.join(' '))
          } else if (typeof val === 'string') {
            messages.push(val)
          }
        }
        error.value = messages.join(' ') || 'Ошибка обновления профиля'
      }
    } else {
      error.value = 'Ошибка обновления профиля'
    }
  } finally {
    loading.value = false
  }
}

const togglePasswordForm = () => {
  showPasswordForm.value = !showPasswordForm.value
  if (!showPasswordForm.value) {
    passwordForm.value = { old_password: '', new_password: '' }
    oldPasswordVerified.value = false
    passwordError.value = null
    passwordSuccess.value = null
  }
}

const handleVerifyPassword = async () => {
  if (!passwordForm.value.old_password) return
  verifyLoading.value = true
  passwordError.value = null
  try {
    await verifyPasswordApi({ old_password: passwordForm.value.old_password })
    oldPasswordVerified.value = true
  } catch (err) {
    const data = err?.response?.data
    passwordError.value = data?.detail || 'Неверный пароль'
  } finally {
    verifyLoading.value = false
  }
}

const handleChangePassword = async () => {
  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = 'Пароль должен содержать минимум 8 символов'
    return
  }
  passwordLoading.value = true
  passwordError.value = null
  passwordSuccess.value = null
  try {
    await changePasswordApi({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    })
    passwordSuccess.value = 'Пароль успешно изменён'
    passwordForm.value = { old_password: '', new_password: '' }
    oldPasswordVerified.value = false
    showPasswordForm.value = false
  } catch (err) {
    const data = err?.response?.data
    if (data?.old_password) {
      passwordError.value = Array.isArray(data.old_password) ? data.old_password[0] : data.old_password
    } else if (data?.new_password) {
      passwordError.value = Array.isArray(data.new_password) ? data.new_password[0] : data.new_password
    } else if (data?.detail) {
      passwordError.value = data.detail
    } else {
      passwordError.value = 'Ошибка смены пароля'
    }
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.edit-profile {
  min-height: 100vh;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  position: relative;
}

.profile-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 48px;
  position: relative;
  z-index: 1;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 2rem;
  margin: 0;
  color: #FFFFFF;
  font-weight: 900;
  letter-spacing: -1px;
}

.card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 12px 30px rgba(255, 215, 0, 0.3);
  border-color: #FF8C00;
  transform: translateY(-2px);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 0.95rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.form-group input {
  width: 100%;
  padding: 14px 18px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}


.password-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.btn-change-password {
  padding: 10px 20px;
  background: transparent;
  color: #FFD700;
  border: 1px solid #FFD700;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-family: inherit;
}

.btn-change-password:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.password-form {
  margin-top: 20px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  border: 1px solid rgba(255, 215, 0, 0.2);
}

.password-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.password-row:focus-within {
  outline: none;
  box-shadow: none;
}

.password-row-top {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
}

.password-row-top input {
  flex: 1;
  min-width: 0;
}

.password-row .show-password-checkbox {
  align-self: flex-start;
}

.password-row.password-verified input {
  border-color: rgba(76, 175, 80, 0.8);
  background: rgba(76, 175, 80, 0.15);
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.3);
}

.btn-verify {
  flex-shrink: 0;
  padding: 10px 16px;
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
  border: 1px solid #FFD700;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-family: inherit;
}

.btn-verify:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.3);
  border-color: #FF8C00;
  color: #FF8C00;
}

.btn-verify:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.show-password-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  user-select: none;
  outline: none;
  box-shadow: none;
}

.show-password-checkbox:focus,
.show-password-checkbox:focus-within {
  outline: none;
  box-shadow: none;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #FFD700;
  outline: none;
  box-shadow: none;
}

.checkbox-input:focus {
  outline: none;
  box-shadow: none;
}

/* Исключаем чекбокс из подсветки формы */
.form-group input:not(.checkbox-input):focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.checkbox-label {
  cursor: pointer;
}

.btn-save-password {
  margin-top: 16px;
  padding: 10px 20px;
  background: #FFD700;
  color: #1A1A1A;
  border: 1px solid #FFD700;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-family: inherit;
}

.btn-save-password:hover:not(:disabled) {
  background: #FF8C00;
  border-color: #FF8C00;
  transform: translateY(-2px);
}

.btn-save-password:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn-save {
  padding: 12px 24px;
  background: #FFD700;
  color: #1A1A1A;
  border: 1px solid #FFD700;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
  font-family: inherit;
}

.btn-save:hover:not(:disabled) {
  background: #FF8C00;
  border-color: #FF8C00;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  padding: 12px 24px;
  background: transparent;
  color: #FFD700;
  border: 1px solid #FFD700;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
  font-family: inherit;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.btn-cancel:hover {
  border-color: rgba(255, 107, 107, 0.6);
  color: #ffb3b3;
  background: rgba(255, 107, 107, 0.1);
}

.error-message {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.5);
  border-radius: 8px;
  color: #ffb3b3;
  font-size: 0.9rem;
  text-shadow: 0 1px 4px rgba(255, 107, 107, 0.3);
}

.success-message {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  color: #ffffff;
  font-size: 0.9rem;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .profile-content {
    padding: 24px 16px 32px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .card {
    padding: 24px;
  }

  .form-group {
    margin-bottom: 20px;
  }

  .form-group input {
    padding: 12px 16px;
    font-size: 0.95rem;
  }

  .form-actions {
    flex-direction: column;
    gap: 10px;
  }

  .btn-save,
  .btn-cancel {
    width: 100%;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .password-row-top {
    flex-wrap: wrap;
  }

  .password-row-top .btn-verify {
    width: 100%;
  }

  .profile-content {
    padding: 20px 12px 24px;
  }

  .page-header h1 {
    font-size: 1.3rem;
  }

  .card {
    padding: 20px;
  }

  .form-group {
    margin-bottom: 18px;
  }

  .form-group label {
    font-size: 0.9rem;
  }

  .form-group input {
    padding: 10px 14px;
    font-size: 0.9rem;
  }

  .btn-save,
  .btn-cancel {
    padding: 10px 20px;
    font-size: 0.95rem;
  }
}
</style>
