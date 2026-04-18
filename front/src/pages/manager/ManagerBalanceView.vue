<!-- src/pages/manager/ManagerBalanceView.vue -->
<template>
  <div class="manager-balance-page">
    <main class="balance-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">Управление балансами</h1>
          <p class="subtitle">
            Просмотр и изменение баланса уроков у учеников.
          </p>
        </div>
      </div>

      <!-- ПОИСК И СПИСОК УЧЕНИКОВ -->
      <section class="balance-card">
        <div class="card-header">
          <div class="card-icon">👥</div>
          <h2 class="card-title">Ученики и абитуриенты</h2>
        </div>

        <!-- Поиск -->
        <div class="search-form">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Email или имя ученика"
            class="search-input"
            @keyup.enter="loadAllStudents"
          />
          <button class="btn primary" @click="loadAllStudents" :disabled="loadingStudents">
            {{ loadingStudents ? '⏳ Загружаем...' : '🔍 Поиск' }}
          </button>
        </div>

        <!-- Сообщения об ошибках -->
        <div v-if="studentsError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ studentsError }}</span>
        </div>

        <!-- Загрузка -->
        <div v-if="loadingStudents" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем учеников...</p>
        </div>

        <!-- Таблица учеников -->
        <div v-if="!loadingStudents && allStudents.length" class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Имя ученика</th>
                <th>Роль</th>
                <th>Баланс</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="student in allStudents" 
                :key="student.id"
                @click="openBalanceModal(student)"
                class="clickable-row"
              >
                <td>{{ student.id }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.student_full_name || '—' }}</td>
                <td>{{ student.role === 'STUDENT' ? 'Ученик' : student.role === 'APPLICANT' ? 'Абитуриент' : student.role }}</td>
                <td class="balance-cell">{{ student.balance || 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Пустое состояние -->
        <p v-else-if="!loadingStudents && !allStudents.length" class="empty-state">
          Учеников пока нет.
        </p>
      </section>
    </main>

    <!-- МОДАЛЬНОЕ ОКНО УПРАВЛЕНИЯ БАЛАНСОМ -->
    <div v-if="showBalanceModal && selectedStudent" class="modal-backdrop" @click="closeBalanceModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Управление балансом</h2>
          <button class="btn-icon close" @click="closeBalanceModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Информация об ученике -->
          <div class="student-info">
            <div class="info-item">
              <span class="label">📧 Email:</span>
              <span class="value">{{ selectedStudent.email }}</span>
            </div>
            <div class="info-item highlight">
              <span class="label">💰 Доступно уроков:</span>
              <span class="value large">{{ currentBalance }}</span>
            </div>
          </div>

          <!-- Быстрые действия -->
          <div class="quick-actions">
            <h3 class="section-title">Быстрые действия</h3>
            <div class="action-buttons">
              <button class="btn action-btn" @click="applyQuickAction(1)">+1 урок</button>
              <button class="btn action-btn" @click="applyQuickAction(5)">+5 уроков</button>
              <button class="btn action-btn" @click="applyQuickAction(10)">+10 уроков</button>
              <button class="btn action-btn danger" @click="applyQuickAction(-1)">-1 урок</button>
            </div>
          </div>

          <!-- Ручной ввод изменения -->
          <div class="manual-input">
            <h3 class="section-title">Изменить на</h3>
            <div class="input-group">
              <input
                v-model.number="balanceDelta"
                type="number"
                placeholder="+5 или -3"
                class="form-input"
              />
              <button 
                class="btn primary" 
                @click="applyDelta"
                :disabled="!balanceDelta"
              >
                Применить
              </button>
            </div>
          </div>

          <!-- Установка нового значения -->
          <div class="set-new-value">
            <h3 class="section-title">Установить новое значение</h3>
            <div class="input-group">
              <input
                v-model.number="newBalance"
                type="number"
                min="0"
                placeholder="Количество уроков"
                class="form-input"
              />
              <button 
                class="btn primary" 
                @click="setNewBalance"
                :disabled="newBalance === null || newBalance === ''"
              >
                Установить
              </button>
            </div>
          </div>

          <!-- Сообщения -->
          <p v-if="updateError" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ updateError }}
          </p>
          <p v-if="updateSuccess" class="success-message">
            <span class="success-icon">✅</span>
            {{ updateSuccess }}
          </p>
        </div>

        <!-- Действия модального окна -->
        <div class="modal-actions">
          <button class="btn secondary" @click="closeBalanceModal">
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import {
  managerGetClients,
  managerGetStudentBalance,
  managerUpdateStudentBalance
} from '../../api/manager'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const searchQuery = ref('')
const allStudents = ref([])
const loadingStudents = ref(false)
const studentsError = ref(null)

// Модальное окно
const showBalanceModal = ref(false)
const selectedStudent = ref(null)
const currentBalance = ref(0)
const balanceDelta = ref(null)
const newBalance = ref(null)
const updatingBalance = ref(false)
const updateError = ref(null)
const updateSuccess = ref(null)

// ===== ЗАГРУЗКА ВСЕХ УЧЕНИКОВ =====
const loadAllStudents = async () => {
  loadingStudents.value = true
  studentsError.value = null

  try {
    const params = {}
    if (searchQuery.value && searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }

    // Загружаем и студентов, и абитуриентов
    const [studentsResponse, applicantsResponse] = await Promise.all([
      managerGetClients({ ...params, role: 'STUDENT' }),
      managerGetClients({ ...params, role: 'APPLICANT' })
    ])
    
    const students = Array.isArray(studentsResponse.data) ? studentsResponse.data : studentsResponse.data.results || []
    const applicants = Array.isArray(applicantsResponse.data) ? applicantsResponse.data : applicantsResponse.data.results || []
    
    // Объединяем студентов и абитуриентов
    const allClients = [...students, ...applicants]
    
    // Загружаем баланс для каждого ученика
    const studentsWithBalance = await Promise.all(
      allClients.map(async (student) => {
        try {
          const { data: balanceData } = await managerGetStudentBalance(student.id)
          return { ...student, balance: balanceData.lessons_available }
        } catch {
          return { ...student, balance: 0 }
        }
      })
    )

    allStudents.value = studentsWithBalance
  } catch (err) {
    console.error('load all students error:', err)
    studentsError.value = 'Не удалось загрузить список учеников'
  } finally {
    loadingStudents.value = false
  }
}

// ===== ОТКРЫТИЕ МОДАЛЬНОГО ОКНА =====
const openBalanceModal = async (student) => {
  selectedStudent.value = student
  currentBalance.value = student.balance || 0
  balanceDelta.value = null
  newBalance.value = null
  updateError.value = null
  updateSuccess.value = null
  showBalanceModal.value = true

  // Загружаем актуальный баланс
  try {
    const { data } = await managerGetStudentBalance(student.id)
    currentBalance.value = data.lessons_available
  } catch (err) {
    console.error('load balance error:', err)
  }
}

// ===== ЗАКРЫТИЕ МОДАЛЬНОГО ОКНА =====
const closeBalanceModal = () => {
  showBalanceModal.value = false
  selectedStudent.value = null
  balanceDelta.value = null
  newBalance.value = null
  updateError.value = null
  updateSuccess.value = null
}

// ===== БЫСТРЫЕ ДЕЙСТВИЯ =====
const applyQuickAction = async (delta) => {
  const action = delta > 0 ? 'добавить' : 'списать'
  const absValue = Math.abs(delta)
  const lessons = absValue === 1 ? 'урок' : (absValue < 5 ? 'урока' : 'уроков')
  
  if (!confirm(`${action === 'добавить' ? 'Добавить' : 'Списать'} ${absValue} ${lessons} ${action === 'добавить' ? 'для' : 'у'} ученика ${selectedStudent.value.email}?`)) {
    return
  }
  
  await updateBalance({ delta })
}

// ===== ПРИМЕНИТЬ ИЗМЕНЕНИЕ =====
const applyDelta = async () => {
  if (!balanceDelta.value) return
  
  const delta = balanceDelta.value
  const action = delta > 0 ? 'добавить' : 'списать'
  const absValue = Math.abs(delta)
  const lessons = absValue === 1 ? 'урок' : (absValue < 5 && absValue > 1 ? 'урока' : 'уроков')
  
  if (!confirm(`${action === 'добавить' ? 'Добавить' : 'Списать'} ${absValue} ${lessons} ${action === 'добавить' ? 'для' : 'у'} ученика ${selectedStudent.value.email}?`)) {
    return
  }
  
  await updateBalance({ delta: balanceDelta.value })
  balanceDelta.value = null
}

// ===== УСТАНОВИТЬ НОВОЕ ЗНАЧЕНИЕ =====
const setNewBalance = async () => {
  if (newBalance.value === null || newBalance.value === '') return
  
  const currentBal = currentBalance.value
  const newBal = newBalance.value
  const diff = newBal - currentBal
  const action = diff > 0 ? 'увеличится' : (diff < 0 ? 'уменьшится' : 'не изменится')
  
  if (!confirm(`Установить баланс ученика ${selectedStudent.value.email} на ${newBal} уроков? Текущий баланс: ${currentBal}. Баланс ${action} на ${Math.abs(diff)} ${Math.abs(diff) === 1 ? 'урок' : (Math.abs(diff) < 5 && Math.abs(diff) > 1 ? 'урока' : 'уроков')}.`)) {
    return
  }
  
  await updateBalance({ lessons_available: newBalance.value })
  newBalance.value = null
}

// ===== ОБНОВЛЕНИЕ БАЛАНСА =====
const updateBalance = async (payload) => {
  if (!selectedStudent.value) return

  updatingBalance.value = true
  updateError.value = null
  updateSuccess.value = null

  try {
    const { data } = await managerUpdateStudentBalance(selectedStudent.value.id, payload)
    currentBalance.value = data.lessons_available
    updateSuccess.value = 'Баланс успешно обновлён'
    
    // Обновляем баланс в списке
    const studentIndex = allStudents.value.findIndex(s => s.id === selectedStudent.value.id)
    if (studentIndex !== -1) {
      allStudents.value[studentIndex].balance = data.lessons_available
    }
    
    // Автоматически закрываем модалку через 1 секунду после успешного обновления
    setTimeout(() => {
      if (updateSuccess.value) {
        closeBalanceModal()
      }
    }, 1000)
  } catch (err) {
    console.error('update balance error:', err)
    updateError.value = err?.response?.data?.detail || 'Не удалось обновить баланс'
  } finally {
    updatingBalance.value = false
  }
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }

  loadAllStudents()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.manager-balance-page {
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

.balance-main {
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

.balance-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  flex-wrap: wrap;
}

.card-icon {
  font-size: 2rem;
}

.card-title {
  font-size: 1.75rem;
  font-weight: 900;
  margin: 0;
  color: #FFFFFF;
  flex: 1;
}

.search-form {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
}

.btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
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
  border: 2px solid #FFD700;
}

.btn.danger {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
  border: 2px solid rgba(255, 68, 68, 0.4);
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn.primary:hover:not(:disabled) {
  background: #FF8C00;
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.btn.danger:hover:not(:disabled) {
  background: rgba(255, 68, 68, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  margin-top: 16px;
  font-size: 0.95rem;
  font-weight: 600;
}

.error-message {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
  border: 2px solid rgba(255, 68, 68, 0.4);
}

.success-message {
  background: rgba(76, 175, 80, 0.2);
  color: #a5d6a7;
  border: 2px solid rgba(76, 175, 80, 0.4);
}

.error-icon,
.success-icon {
  font-size: 1.2rem;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  font-weight: 600;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.table-container {
  overflow-x: auto;
  overflow-y: visible;
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

.students-table {
  width: 100%;
  min-width: 600px;
  border-collapse: collapse;
  font-size: 0.95rem;
  table-layout: auto;
}

.students-table th,
.students-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-sizing: border-box;
}

.students-table th {
  white-space: nowrap;
  font-weight: 700;
  color: #FFFFFF;
  background: rgba(255, 215, 0, 0.1);
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
  font-size: 1rem;
}

.students-table td {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
}

.clickable-row {
  cursor: pointer;
  transition: all 0.2s ease;
}

.clickable-row:hover {
  background: rgba(255, 215, 0, 0.15);
  transform: scale(1.01);
}

.balance-cell {
  font-weight: 700;
  font-size: 1.1rem;
  color: #FFD700;
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

.btn-icon {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  padding: 4px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.student-info {
  padding: 20px;
  background: rgba(50, 50, 50, 0.6);
  border-radius: 12px;
  border: 2px solid rgba(255, 215, 0, 0.3);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  gap: 12px;
}

.info-item.highlight {
  border-top: 2px solid rgba(255, 255, 255, 0.3);
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  padding: 16px 0;
  margin-top: 8px;
}

.info-item .label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  font-weight: 600;
}

.info-item .value {
  color: #FFFFFF;
  font-weight: 500;
}

.info-item .value.large {
  font-size: 2.5rem;
  color: #FFD700;
  font-weight: 900;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}

.quick-actions {
  padding: 20px;
  background: rgba(50, 50, 50, 0.4);
  border-radius: 12px;
  border: 2px solid rgba(255, 215, 0, 0.2);
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.action-btn {
  padding: 14px 20px;
  font-size: 1rem;
}

.manual-input,
.set-new-value {
  padding: 20px;
  background: rgba(50, 50, 50, 0.4);
  border-radius: 12px;
  border: 2px solid rgba(255, 215, 0, 0.2);
}

.input-group {
  display: flex;
  gap: 12px;
}

.form-input {
  flex: 1;
  min-width: 0;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
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
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px solid rgba(255, 215, 0, 0.2);
}

.modal-actions .btn {
  flex: 1;
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

  .balance-main {
    padding: 0 16px 24px;
    gap: 16px;
  }

  .balance-card {
    padding: 20px;
  }

  .search-form {
    flex-direction: column;
    gap: 10px;
  }

  .search-input {
    width: 100%;
  }

  .btn {
    width: 100%;
  }

  .table-container {
    margin-left: -20px;
    margin-right: -20px;
    padding: 0 20px;
  }

  .students-table {
    min-width: 700px;
    font-size: 0.85rem;
  }

  .students-table th,
  .students-table td {
    padding: 10px 12px;
  }

  .modal {
    padding: 24px;
    max-width: 95%;
  }

  .modal-header h2 {
    font-size: 1.3rem;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .input-group {
    flex-direction: column;
  }

  .modal-actions {
    flex-direction: column;
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

  .balance-main {
    padding: 0 12px 20px;
    gap: 12px;
  }

  .balance-card {
    padding: 16px;
    border-width: 2px;
  }

  .card-icon {
    font-size: 1.3rem;
  }

  .card-title {
    font-size: 1.2rem;
  }

  .table-container {
    margin-left: -16px;
    margin-right: -16px;
    padding: 0 16px;
  }

  .students-table {
    min-width: 600px;
    font-size: 0.8rem;
  }

  .students-table th,
  .students-table td {
    padding: 8px 10px;
  }

  .balance-cell {
    font-size: 0.9rem;
  }

  .modal {
    padding: 20px;
  }

  .modal-header h2 {
    font-size: 1.1rem;
  }

  .student-info {
    padding: 16px;
  }

  .info-item .value.large {
    font-size: 2rem;
  }

  .section-title {
    font-size: 1rem;
  }

  .quick-actions,
  .manual-input,
  .set-new-value {
    padding: 16px;
  }
}
</style>
