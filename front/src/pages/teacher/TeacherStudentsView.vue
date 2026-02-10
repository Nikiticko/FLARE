<!-- src/pages/teacher/TeacherStudentsView.vue -->
<template>
  <div class="teacher-students-page">
    <main class="students-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">Список учеников</h1>
          <p class="subtitle">
            Просмотр всех ваших учеников и их информации.
          </p>
        </div>
      </div>

      <!-- ПОИСК -->
      <section class="students-card search-card">
        <div class="card-header">
          <div class="card-icon">🔍</div>
          <h2 class="card-title">Поиск учеников</h2>
        </div>
        <div class="search-form">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по email, ФИО ученика или родителя"
            class="search-input"
            @input="handleSearch"
          />
          <button class="btn secondary" @click="loadStudents" :disabled="loadingStudents">
            {{ loadingStudents ? '⏳ Загружаем...' : '🔄 Обновить' }}
          </button>
        </div>
      </section>

      <!-- СПИСОК УЧЕНИКОВ -->
      <section class="students-card students-list-card">
        <div class="card-header">
          <div class="card-icon">👥</div>
          <h2 class="card-title">Мои ученики</h2>
        </div>

        <div v-if="studentsError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ studentsError }}</span>
        </div>

        <div v-if="loadingStudents" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем учеников...</p>
        </div>

        <div v-if="!loadingStudents && students.length" class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>ФИО ученика</th>
                <th>ФИО родителя</th>
                <th>Телефон</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.id">
                <td>{{ student.id }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.student_full_name || '—' }}</td>
                <td>{{ student.parent_full_name || '—' }}</td>
                <td>{{ student.phone || '—' }}</td>
                <td class="actions">
                  <button class="btn small secondary" @click="viewStudentLessons(student)">
                    Уроки
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-else-if="!loadingStudents && !students.length" class="empty-state">
          Учеников пока нет.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { teacherGetStudents } from '../../api/teacher'

const auth = useAuthStore()
const router = useRouter()

const students = ref([])
const loadingStudents = ref(false)
const studentsError = ref(null)
const searchQuery = ref('')

// ===== ЗАГРУЗКА УЧЕНИКОВ =====
const loadStudents = async () => {
  loadingStudents.value = true
  studentsError.value = null

  try {
    const params = {}
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const { data } = await teacherGetStudents(params)
    students.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load students error:', err)
    studentsError.value = err?.response?.data?.detail || 'Не удалось загрузить список учеников'
  } finally {
    loadingStudents.value = false
  }
}

// ===== ПОИСК =====
let searchTimeout = null
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadStudents()
  }, 500)
}

// ===== ПРОСМОТР УРОКОВ УЧЕНИКА =====
const viewStudentLessons = (student) => {
  router.push({ 
    name: 'teacher-schedule',
    query: { studentId: student.id }
  })
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadStudents()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.teacher-students-page {
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
  font-weight: 800;
  margin: 0 0 8px 0;
  color: #e8eaf6;
  letter-spacing: -1px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: #c5cae9;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.students-main {
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

.students-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.students-card:hover {
  box-shadow: 0 12px 30px rgba(255, 215, 0, 0.3);
  border-color: #FF8C00;
  transform: translateY(-2px);
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
  flex: 1;
}

.search-card {
  grid-column: 1 / -1;
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
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
  width: 100%;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
  transform: translateY(-2px);
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
  gap: 6px;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  flex-shrink: 0;
  box-sizing: border-box;
}

.btn.secondary {
  background: transparent;
  color: #FFD700;
  border: 1px solid #FFD700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn.small {
  padding: 8px 16px;
  font-size: 0.85rem;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  margin-top: 16px;
  font-size: 0.95rem;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.2);
  backdrop-filter: blur(10px);
  color: #ffffff;
  border: 1px solid rgba(239, 68, 68, 0.4);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.error-icon {
  font-size: 1.2rem;
}

.students-list-card {
  grid-column: 1 / -1;
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
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.table-container {
  overflow-x: auto;
  overflow-y: visible;
  margin-top: 16px;
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
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.students-table th {
  white-space: nowrap;
}

.students-table td {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.students-table th {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  font-size: 1rem;
}

.students-table td {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  justify-content: flex-start;
}

.actions .btn {
  flex-shrink: 0;
}

@media (max-width: 1200px) {
  .students-main {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 0 20px 28px;
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

  .students-main {
    padding: 0 16px 24px;
    gap: 16px;
  }

  .students-card {
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

  .search-form {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .search-input {
    width: 100%;
    font-size: 0.95rem;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .table-container {
    margin-top: 12px;
  }

  .students-table {
    font-size: 0.85rem;
    min-width: 700px;
  }

  .students-table th,
  .students-table td {
    padding: 10px 12px;
  }

  .students-table th {
    font-size: 0.9rem;
  }

  .actions {
    flex-direction: column;
    gap: 6px;
  }

  .actions .btn {
    width: 100%;
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

  .students-main {
    padding: 0 12px 20px;
    gap: 12px;
  }

  .students-card {
    padding: 16px;
    border-width: 2px;
  }

  .card-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    gap: 8px;
  }

  .card-icon {
    font-size: 1.3rem;
  }

  .card-title {
    font-size: 1.2rem;
  }

  .search-form {
    gap: 10px;
  }

  .search-input {
    font-size: 0.9rem;
    padding: 10px 12px;
  }

  .btn {
    padding: 10px 20px;
    font-size: 0.9rem;
  }

  .btn.small {
    padding: 8px 16px;
    font-size: 0.8rem;
  }

  .table-container {
    margin-top: 10px;
    margin-left: -16px;
    margin-right: -16px;
    padding: 0 16px;
  }

  .students-table {
    font-size: 0.8rem;
    min-width: 650px;
  }

  .students-table th,
  .students-table td {
    padding: 8px 10px;
  }

  .students-table th {
    font-size: 0.85rem;
  }

  .students-table td {
    max-width: 150px;
    font-size: 0.75rem;
  }

  .error-message {
    padding: 10px 12px;
    font-size: 0.85rem;
  }

  .loading-state,
  .empty-state {
    padding: 30px 20px;
    font-size: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border-width: 3px;
  }
}
</style>



