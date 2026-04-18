<!-- src/pages/admin/AdminDashboardView.vue -->
<template>
  <div class="admin-page">
    <!-- ОСНОВНОЙ КОНТЕНТ -->
    <main class="admin-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">Управление пользователями</h1>
          <p class="subtitle">
            Просмотр, редактирование и управление пользователями системы.
          </p>
        </div>
      </div>

      <section class="admin-card quick-create-card">
        <div class="card-header">
          <div class="card-icon">⚡</div>
          <h2 class="card-title">Быстрое создание аккаунта</h2>
        </div>

        <form class="quick-create-form" @submit.prevent="handleQuickCreate">
          <div class="quick-create-inputs">
            <div class="filter-group">
              <input
                v-model.trim="quickCreateEmail"
                type="email"
                placeholder="Email нового клиента"
                class="filter-input"
                autocomplete="off"
              />
            </div>

            <button class="btn primary" type="submit" :disabled="creatingUser || !quickCreateEmail">
              {{ creatingUser ? '⏳ Создаём...' : 'Создать аккаунт' }}
            </button>
          </div>

          <p class="quick-create-hint">
            Будет создан аккаунт с паролем `12345678`. Остальные данные пользователь заполнит сам в своём профиле.
          </p>

          <div v-if="createUserError" class="error-message inline-message">
            <span class="error-icon">⚠️</span>
            <span>{{ createUserError }}</span>
          </div>

          <div v-if="createUserSuccess" class="success-message inline-message">
            <span class="success-icon">✅</span>
            <span>{{ createUserSuccess }}</span>
          </div>
        </form>
      </section>

      <!-- ПОЛЬЗОВАТЕЛИ -->
      <section class="admin-card users-card">
        <div class="card-header">
          <div class="card-icon">👥</div>
          <h2 class="card-title">Пользователи</h2>
        </div>

        <div class="section-header">
          <div class="filters">
            <div class="filter-group">
              <input
                v-model="search"
                type="text"
                placeholder="Поиск по email / имени"
                class="filter-input"
              />
            </div>

            <div class="filter-group">
              <select v-model="roleFilter" class="filter-select">
                <option value="">Все роли</option>
                <option value="ADMIN">ADMIN</option>
                <option value="MANAGER">MANAGER</option>
                <option value="TEACHER">TEACHER</option>
                <option value="STUDENT">STUDENT</option>
                <option value="APPLICANT">APPLICANT</option>
              </select>
            </div>

            <button class="btn small" @click="loadUsers" :disabled="loadingUsers">
              {{ loadingUsers ? '⏳ Обновляем...' : '🔄 Обновить' }}
            </button>
          </div>
        </div>

        <div v-if="usersError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ usersError }}</span>
        </div>

        <div v-if="loadingUsers" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем пользователей...</p>
        </div>

        <div v-if="!loadingUsers && users.length" class="table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Контакт</th>
                <th>Имя ученика</th>
                <th>Имя родителя</th>
                <th>Роль</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.phone || '—' }}</td>
                <td>{{ u.student_full_name || '—' }}</td>
                <td>{{ u.parent_full_name || '—' }}</td>
                <td>
                  <select
                    v-model="u.role"
                    class="role-select"
                    @change="handleChangeRole(u)"
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="MANAGER">MANAGER</option>
                    <option value="TEACHER">TEACHER</option>
                    <option value="STUDENT">STUDENT</option>
                    <option value="APPLICANT">APPLICANT</option>
                  </select>
                </td>
                <td class="actions">
                  <button class="btn-icon edit" @click="openEdit(u)" title="Изменить">
                    ✏️
                  </button>
                  <button class="btn-icon delete" @click="handleDelete(u)" title="Удалить">
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="!loadingUsers && !users.length" class="empty-state">
          <p>Пользователей пока нет.</p>
        </div>
      </section>

      <!-- МОДАЛЬНОЕ ОКНО РЕДАКТИРОВАНИЯ -->
      <div v-if="editUser" class="modal-backdrop" @click="cancelEdit">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <h2>Редактирование пользователя #{{ editUser.id }}</h2>
            <button class="btn-icon close" @click="cancelEdit">×</button>
          </div>
          <form @submit.prevent="handleSave">
            <div class="form-row">
              <label class="form-label">
                <span class="label-text">📧 Email</span>
                <input v-model="editForm.email" type="email" required class="form-input" />
              </label>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">📱 Контакт</span>
                <input v-model="editForm.phone" type="text" class="form-input" placeholder="+7... или @username / ссылка" />
                <span class="field-hint">Телефон или соцсеть. Для соцсети укажите username или ссылку.</span>
              </label>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">🎓 Имя ученика</span>
                <input v-model="editForm.student_full_name" type="text" class="form-input" />
              </label>
            </div>

            <div class="form-row">
              <label class="form-label">
                <span class="label-text">👨‍👩‍👧 Имя родителя</span>
                <input v-model="editForm.parent_full_name" type="text" class="form-input" />
              </label>
            </div>

            <div class="password-section">
              <button 
                type="button" 
                class="btn danger" 
                @click="handleResetPassword"
                :disabled="resettingPassword"
              >
                {{ resettingPassword ? '⏳ Сбрасываем...' : '🔑 Сбросить пароль на 12345678' }}
              </button>
            </div>

            <div class="modal-actions">
              <button class="btn primary" type="submit" :disabled="savingUser">
                {{ savingUser ? '⏳ Сохраняем...' : '💾 Сохранить' }}
              </button>
              <button class="btn secondary" type="button" @click="cancelEdit">
                Отмена
              </button>
            </div>

            <div v-if="editError" class="error-message">
              <span class="error-icon">⚠️</span>
              <span>{{ editError }}</span>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { registerApi } from '../../api/auth'
import {
  adminGetUsers,
  adminUpdateUser,
  adminDeleteUser,
  adminSetUserRole,
  adminResetPassword,
} from '../../api/admin'

const auth = useAuthStore()
const router = useRouter()

const users = ref([])
const loadingUsers = ref(false)
const usersError = ref(null)

const search = ref('')
const roleFilter = ref('')
const quickCreateEmail = ref('')
const creatingUser = ref(false)
const createUserError = ref(null)
const createUserSuccess = ref(null)

const editUser = ref(null)
const editForm = ref({
  email: '',
  phone: '',
  student_full_name: '',
  parent_full_name: '',
})
const savingUser = ref(false)
const editError = ref(null)
const resettingPassword = ref(false)

// ===== ЗАГРУЗКА ПОЛЬЗОВАТЕЛЕЙ =====
const loadUsers = async () => {
  loadingUsers.value = true
  usersError.value = null
  try {
    const params = {}
    if (search.value) params.search = search.value
    if (roleFilter.value) params.role = roleFilter.value

    const { data } = await adminGetUsers(params)
    users.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('admin users load error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось загрузить пользователей'
  } finally {
    loadingUsers.value = false
  }
}

// ===== СМЕНА РОЛИ =====
const handleChangeRole = async (user) => {
  try {
    await adminSetUserRole(user.id, user.role)
  } catch (err) {
    console.error('set role error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось изменить роль пользователя'
    await loadUsers()
  }
}

const handleQuickCreate = async () => {
  if (!quickCreateEmail.value) return

  creatingUser.value = true
  createUserError.value = null
  createUserSuccess.value = null

  try {
    await registerApi({
      email: quickCreateEmail.value,
      phone: '',
      student_full_name: '',
      parent_full_name: '',
      password: '12345678',
    })

    createUserSuccess.value = `Аккаунт для ${quickCreateEmail.value} создан. Стартовый пароль: 12345678`
    quickCreateEmail.value = ''
    await loadUsers()
  } catch (err) {
    console.error('quick create user error:', err)

    if (err?.response?.data) {
      const data = err.response.data
      if (typeof data === 'string') {
        createUserError.value = data
      } else if (data.detail || data.error) {
        createUserError.value = data.detail || data.error
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
        createUserError.value = messages.join(' ') || 'Не удалось создать аккаунт'
      }
    } else {
      createUserError.value = 'Не удалось создать аккаунт'
    }
  } finally {
    creatingUser.value = false
  }
}

// ===== РЕДАКТИРОВАНИЕ =====
const openEdit = (user) => {
  editUser.value = { ...user }
  editForm.value = {
    email: user.email || '',
    phone: user.phone || '',
    student_full_name: user.student_full_name || '',
    parent_full_name: user.parent_full_name || '',
  }
  editError.value = null
}

const cancelEdit = () => {
  editUser.value = null
  editError.value = null
}

const handleSave = async () => {
  if (!editUser.value) return
  savingUser.value = true
  editError.value = null

  try {
    const payload = { ...editForm.value }
    const { data } = await adminUpdateUser(editUser.value.id, payload)
    const idx = users.value.findIndex((u) => u.id === data.id)
    if (idx !== -1) {
      users.value[idx] = data
    }
    editUser.value = null
  } catch (err) {
    console.error('update user error:', err)
    editError.value =
      err?.response?.data?.detail || 'Не удалось сохранить изменения'
  } finally {
    savingUser.value = false
  }
}

// ===== СБРОС ПАРОЛЯ =====
const handleResetPassword = async () => {
  if (!editUser.value) return
  if (!confirm(`Сбросить пароль пользователя ${editUser.value.email} на 12345678?`)) return
  
  resettingPassword.value = true
  editError.value = null

  try {
    const { data } = await adminResetPassword(editUser.value.id)
    alert(data.detail || 'Пароль успешно сброшен')
  } catch (err) {
    console.error('reset password error:', err)
    editError.value =
      err?.response?.data?.detail || 'Не удалось сбросить пароль'
  } finally {
    resettingPassword.value = false
  }
}

// ===== УДАЛЕНИЕ =====
const handleDelete = async (user) => {
  if (!confirm(`Удалить пользователя ${user.email}?`)) return
  try {
    await adminDeleteUser(user.id)
    users.value = users.value.filter((u) => u.id !== user.id)
    if (editUser.value?.id === user.id) {
      editUser.value = null
    }
  } catch (err) {
    console.error('delete user error:', err)
    usersError.value =
      err?.response?.data?.detail || 'Не удалось удалить пользователя'
  }
}

// ===== НАВИГАЦИЯ / АВТОРИЗАЦИЯ =====
const goToSchedule = () => {
  router.push({ name: 'admin-schedule' })
}

const goToLogs = () => {
  router.push({ name: 'admin-logs' })
}

const goToCourses = () => {
  router.push({ name: 'admin-courses' })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadUsers()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.admin-page {
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  padding: 0;
  margin: 0;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.page-header {
  padding: 20px 24px 0;
  margin-bottom: 24px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.title-block {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: #FFFFFF;
  letter-spacing: -1px;
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  flex-shrink: 0;
  box-sizing: border-box;
}

.btn.primary {
  background: #FFD700;
  color: #1A1A1A;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.btn.secondary {
  background: transparent;
  color: #FFD700;
  border: 1px solid #FFD700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn.danger {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
  border: 1px solid rgba(255, 68, 68, 0.4);
}

.btn.small {
  padding: 8px 16px;
  font-size: 0.85rem;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn.primary:hover:not(:disabled) {
  background: #FF8C00;
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.btn.danger:hover:not(:disabled) {
  background: rgba(255, 68, 68, 0.3);
  border-color: rgba(255, 68, 68, 0.6);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.admin-main {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px 32px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  overflow-y: visible;
  overflow-x: hidden;
  box-sizing: border-box;
}

.admin-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.4s ease-out;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

.card-icon {
  font-size: 2rem;
}

.card-title {
  font-size: 1.75rem;
  font-weight: 900;
  margin: 0;
  color: #FFFFFF;
  letter-spacing: -0.5px;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.quick-link {
  background: rgba(40, 45, 60, 0.8);
  border: 2px solid rgba(255, 215, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.quick-link:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.ql-icon {
  font-size: 2rem;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
  flex-shrink: 0;
}

.ql-content {
  flex: 1;
}

.ql-title {
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 8px;
  color: #FFFFFF;
}

.ql-desc {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.section-header {
  margin-bottom: 20px;
}

.quick-create-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.quick-create-inputs {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
}

.quick-create-hint {
  margin: 0;
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.9rem;
  line-height: 1.5;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.filter-group {
  flex: 1;
  min-width: 200px;
  max-width: 100%;
  box-sizing: border-box;
}

.filter-input,
.filter-select {
  width: 100%;
  min-width: 0;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
  box-sizing: border-box;
}

.filter-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
  transform: translateY(-2px);
}

.filter-select {
  cursor: pointer;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.4);
  border-radius: 12px;
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  margin-bottom: 20px;
}

.success-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(76, 175, 80, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(76, 175, 80, 0.4);
  border-radius: 12px;
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.error-icon {
  font-size: 1.2rem;
}

.success-icon {
  font-size: 1.2rem;
}

.inline-message {
  margin-bottom: 0;
}

.table-container {
  overflow-x: auto;
  overflow-y: visible;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  -webkit-overflow-scrolling: touch;
}

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: rgba(40, 40, 40, 0.5);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.5);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.7);
}

.users-table {
  width: 100%;
  min-width: 800px;
  border-collapse: collapse;
  font-size: 0.9rem;
  table-layout: auto;
}

.users-table thead {
  background: rgba(255, 215, 0, 0.1);
}

.users-table th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 700;
  color: #FFFFFF;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  box-sizing: border-box;
}

.users-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  color: rgba(255, 255, 255, 0.9);
  box-sizing: border-box;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.users-table tbody tr {
  transition: background 0.2s;
}

.users-table tbody tr:hover {
  background: rgba(255, 215, 0, 0.1);
}

.role-select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  width: 100%;
  min-width: 120px;
  max-width: 100%;
  box-sizing: border-box;
}

.role-select option {
  background: #282D3C;
  color: #FFFFFF;
  padding: 8px;
}

.role-select:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  justify-content: flex-start;
  align-items: center;
}

.actions .btn-icon {
  flex-shrink: 0;
}

.btn-icon {
  padding: 8px 12px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-icon.edit:hover {
  background: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

.btn-icon.delete:hover {
  background: rgba(255, 107, 107, 0.3);
  transform: translateY(-2px);
}

.btn-icon.close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
}

.btn-icon.close:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* МОДАЛЬНОЕ ОКНО */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  box-sizing: border-box;
}

.modal {
  background: rgba(30, 30, 30, 0.98);
  border: 3px solid #FFD700;
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: modalSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #FFFFFF;
  flex: 1;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
  width: 100%;
}

.modal-actions .btn {
  flex: 1;
  min-width: 120px;
}

.password-section {
  margin: 20px 0;
  padding: 16px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 12px;
}

.password-section .btn {
  width: 100%;
}

.form-row {
  margin-bottom: 16px;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label-text {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.field-hint {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  line-height: 1.4;
}

.form-input {
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.form-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
}

.edit-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
  width: 100%;
}

.edit-actions .btn {
  flex: 1;
  min-width: 120px;
}

@media (max-width: 1200px) {
  .admin-main {
    padding: 0 24px 32px;
  }

  .quick-links {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 16px 0;
    margin-bottom: 20px;
  }

  .page-title {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 0.9rem;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .admin-main {
    padding: 0 16px 24px;
    gap: 16px;
  }

  .admin-card {
    padding: 20px;
  }

  .card-header {
    margin-bottom: 20px;
    padding-bottom: 16px;
  }

  .card-icon {
    font-size: 1.5rem;
  }

  .card-title {
    font-size: 1.5rem;
  }

  .quick-links {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .filters {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .quick-create-inputs {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    width: 100%;
    min-width: 0;
  }

  .section-header {
    margin-bottom: 16px;
  }

  .table-container {
    overflow-x: auto;
    margin-top: 12px;
  }

  .users-table {
    min-width: 800px;
    font-size: 0.85rem;
  }

  .users-table th,
  .users-table td {
    padding: 10px 12px;
  }

  .users-table th {
    font-size: 0.8rem;
  }

  .actions {
    flex-direction: column;
    gap: 6px;
  }

  .actions .btn-icon {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 12px 0;
    margin-bottom: 16px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 0.85rem;
  }

  .admin-main {
    padding: 0 12px 20px;
    gap: 12px;
  }

  .admin-card {
    padding: 16px;
    border-width: 2px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
  }

  .card-icon {
    font-size: 1.3rem;
  }

  .card-title {
    font-size: 1.1rem;
  }

  .filters {
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }

  .filter-group {
    width: 100%;
    min-width: 0;
  }

  .filter-input,
  .filter-select {
    width: 100%;
    font-size: 0.9rem;
    padding: 10px 12px;
  }

  .btn {
    padding: 10px 16px;
    font-size: 0.85rem;
  }

  .btn.small {
    padding: 8px 14px;
    font-size: 0.8rem;
  }

  .table-container {
    margin-top: 10px;
    margin-left: -16px;
    margin-right: -16px;
    padding: 0 16px;
  }

  .users-table {
    min-width: 700px;
    font-size: 0.8rem;
  }

  .users-table th,
  .users-table td {
    padding: 8px 10px;
  }

  .users-table th {
    font-size: 0.75rem;
  }

  .users-table td {
    max-width: 120px;
    font-size: 0.75rem;
  }

  .role-select {
    font-size: 0.75rem;
    padding: 6px 8px;
    min-width: 100px;
  }

  .btn-icon {
    padding: 6px 10px;
    font-size: 1rem;
  }

  .actions {
    gap: 6px;
  }

  .form-row {
    margin-bottom: 14px;
  }

  .form-input {
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .label-text {
    font-size: 0.85rem;
  }

  .error-message {
    padding: 10px 12px;
    font-size: 0.85rem;
    margin-bottom: 16px;
  }

  .loading-state {
    padding: 30px 20px;
  }

  .spinner {
    width: 36px;
    height: 36px;
    border-width: 3px;
  }

  .empty-state {
    padding: 30px 20px;
    font-size: 0.9rem;
  }
}
</style>
