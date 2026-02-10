<!-- src/pages/common/DashboardView.vue -->
<template>
  <div class="unified-dashboard">
    <div class="dashboard-content">
      <div class="main-grid">
        <!-- Левая колонка -->
        <div class="left-column">
          <!-- Профиль пользователя -->
          <div class="card profile-card">
            <div class="profile-avatar">
              <svg viewBox="0 0 100 100" class="avatar-icon">
                <circle cx="50" cy="50" r="50" fill="rgba(255, 255, 255, 0.1)"/>
                <circle cx="50" cy="35" r="15" fill="rgba(255, 255, 255, 0.8)"/>
                <path d="M 20 85 Q 20 65 50 65 Q 80 65 80 85" fill="rgba(255, 255, 255, 0.8)"/>
              </svg>
            </div>
            <div class="profile-info">
              <div class="profile-name">{{ dashboardData?.student_full_name || 'Пользователь' }}</div>
              <div class="profile-email">{{ dashboardData?.email || '—' }}</div>
            </div>
            <router-link :to="{ name: 'edit-profile' }" class="edit-btn">
              Редактировать
            </router-link>
          </div>

          <!-- Осталось занятий -->
          <div class="card balance-section">
            <div class="section-title">Осталось занятий</div>
            <div class="balance-cards">
              <div class="balance-card">
                <div class="balance-label">Осталось занятий: {{ dashboardData?.balance || 0 }}</div>
              </div>
            </div>
          </div>

          <!-- История уроков -->
          <div class="card history-card">
            <h2 class="history-title">История уроков</h2>
            <div v-if="historyLoading" class="loading">Загрузка...</div>
            <div v-else-if="historyError" class="error">{{ historyError }}</div>
            <div v-else-if="historyLessons.length === 0" class="empty">
              Нет завершенных уроков
            </div>
            <div v-else class="schedule-list">
              <div
                v-for="lesson in historyLessons"
                :key="lesson.id"
                class="schedule-item schedule-item--clickable"
                @click="openLessonDetails(lesson)"
              >
                <div class="schedule-date">
                  {{ formatDate(lesson.scheduled_at) }} в {{ formatTime(lesson.scheduled_at) }}
                </div>
                <div class="schedule-course">Курс: {{ lesson.course || '—' }}</div>
                <div class="schedule-teacher">Преподаватель: {{ lesson.teacher_full_name || 'Не назначен' }}</div>
              </div>
            </div>
            <div class="history-pagination">
              <button
                class="pagination-btn"
                :disabled="!canGoHistoryPrev"
                @click="handleHistoryPrev"
              >
                Назад
              </button>
              <div class="pagination-info">
                Стр. {{ historyPage }} из {{ historyTotalPages }}
              </div>
              <button
                class="pagination-btn"
                :disabled="!canGoHistoryNext"
                @click="handleHistoryNext"
              >
                Вперед
              </button>
            </div>
          </div>
        </div>

        <!-- Правая колонка -->
        <div class="right-column">
          <!-- Следующие запланированные занятия -->
          <div class="card schedule-card">
            <h2 class="schedule-title">Следующие запланированные занятия</h2>
            <div v-if="lessonsLoading" class="loading">Загрузка...</div>
            <div v-else-if="lessonsError" class="error">{{ lessonsError }}</div>
            <div v-else-if="upcomingLessons.length === 0" class="empty">
              Нет запланированных занятий
            </div>
            <div v-else class="schedule-list">
              <div 
                v-for="(lesson, index) in upcomingLessons" 
                :key="lesson.id" 
                class="schedule-item"
              >
                <div class="schedule-date">
                  {{ formatDate(lesson.scheduled_at) }} в {{ formatTime(lesson.scheduled_at) }}
                </div>
                <div class="schedule-course">Курс: {{ lesson.course || '—' }}</div>
                <div class="schedule-teacher">Преподаватель: {{ lesson.teacher_full_name || 'Не назначен' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Кнопка "Задать вопрос" -->
    <button class="floating-btn" @click="showRequestForm = true">
      Задать вопрос
    </button>

    <!-- Форма обращения к менеджеру -->
    <ManagerRequestForm
      :show="showRequestForm"
      :on-submit="handleCreateRequest"
      @close="showRequestForm = false"
      @success="handleRequestSuccess"
    />

    <!-- Карточка деталей урока -->
    <div v-if="selectedHistoryLesson" class="modal-overlay" @click="closeLessonDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Информация об уроке</h3>
          <button class="modal-close" @click="closeLessonDetails">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <span class="detail-label">Дата и время:</span>
            <span class="detail-value">{{ formatDate(selectedHistoryLesson.scheduled_at) }} в {{ formatTime(selectedHistoryLesson.scheduled_at) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Курс:</span>
            <span class="detail-value">{{ selectedHistoryLesson.course || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Преподаватель:</span>
            <span class="detail-value">{{ selectedHistoryLesson.teacher_full_name || 'Не назначен' }}</span>
          </div>
          <div class="detail-item" v-if="selectedHistoryLesson.feedback">
            <span class="detail-label">Обратная связь:</span>
            <span class="detail-value">{{ selectedHistoryLesson.feedback }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-close" @click="closeLessonDetails">Закрыть</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ManagerRequestForm from '../../components/ManagerRequestForm.vue'
import { getDashboard, studentGetLessons, studentCreateRequest } from '../../api/student'

const auth = useAuthStore()
const router = useRouter()

const dashboardData = ref(null)
const dashboardLoading = ref(false)
const dashboardError = ref(null)

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

const allHistoryLessons = ref([])
const historyLoading = ref(false)
const historyError = ref(null)
const historyPage = ref(1)
const historyPageSize = 5
const selectedHistoryLesson = ref(null)

const showRequestForm = ref(false)

const loadDashboard = async () => {
  dashboardLoading.value = true
  dashboardError.value = null
  try {
    const { data } = await getDashboard()
    dashboardData.value = data
  } catch (err) {
    console.error('load dashboard error:', err)
    dashboardError.value = 'Не удалось загрузить данные'
  } finally {
    dashboardLoading.value = false
  }
}

const loadLessons = async () => {
  lessonsLoading.value = true
  lessonsError.value = null
  try {
    const { data } = await studentGetLessons({
      status: 'PLANNED',
      ordering: 'scheduled_at'
    })
    lessons.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load lessons error:', err)
    lessonsError.value = 'Не удалось загрузить уроки'
  } finally {
    lessonsLoading.value = false
  }
}

const loadHistoryLessons = async () => {
  historyLoading.value = true
  historyError.value = null
  try {
    const { data } = await studentGetLessons({
      status: 'DONE',
      ordering: '-scheduled_at'
    })
    allHistoryLessons.value = Array.isArray(data) ? data : data.results || []
    historyPage.value = 1
  } catch (err) {
    console.error('load history lessons error:', err)
    historyError.value = 'Не удалось загрузить историю уроков'
  } finally {
    historyLoading.value = false
  }
}

const historyLessons = computed(() => {
  const start = (historyPage.value - 1) * historyPageSize
  return allHistoryLessons.value.slice(start, start + historyPageSize)
})

const upcomingLessons = computed(() => {
  const now = new Date()
  return lessons.value
    .filter(lesson => {
      if (!lesson.scheduled_at) return false
      const lessonDate = new Date(lesson.scheduled_at)
      return lessonDate >= now && lesson.status === 'PLANNED'
    })
    .sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at))
    .slice(0, 3) // Максимум 3 занятия
})

const historyTotalPages = computed(() => {
  return allHistoryLessons.value.length > 0 ? Math.ceil(allHistoryLessons.value.length / historyPageSize) : 1
})

const canGoHistoryPrev = computed(() => {
  return historyPage.value > 1
})

const canGoHistoryNext = computed(() => {
  return historyPage.value < historyTotalPages.value
})

const formatDate = (dateString) => {
  if (!dateString) return 'дд.мм.гг'
  const d = new Date(dateString)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const formatTime = (dateString) => {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const handleCreateRequest = async (payload) => {
  await studentCreateRequest(payload)
}

const handleRequestSuccess = () => {
  showRequestForm.value = false
  console.log('Обращение успешно отправлено')
}

const openLessonDetails = (lesson) => {
  selectedHistoryLesson.value = lesson
}

const closeLessonDetails = () => {
  selectedHistoryLesson.value = null
}

const handleHistoryPrev = () => {
  if (!canGoHistoryPrev.value) return
  historyPage.value--
}

const handleHistoryNext = () => {
  if (!canGoHistoryNext.value) return
  historyPage.value++
}

onMounted(async () => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }

  if (!auth.user && auth.isAuthenticated) {
    await auth.fetchMe()
  }

  await loadDashboard()
  await loadLessons()
  await loadHistoryLessons()
})
</script>

<style scoped>
.unified-dashboard {
  min-height: 100vh;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  position: relative;
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: start;
}

/* Карточки */
.card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

/* Профиль */
.profile-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  background: rgba(60, 60, 60, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #FFD700;
}

.avatar-icon {
  width: 60px;
  height: 60px;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: #FFFFFF;
}

.profile-email {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
}

.edit-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFFFFF;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.edit-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
}

/* Секции */
.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 16px;
}

.balance-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.balance-card {
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.balance-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  font-weight: 600;
}

/* Расписание */
.schedule-card {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

/* История уроков */
.history-card {
  display: flex;
  flex-direction: column;
}

.history-title {
  font-size: 1.6rem;
  font-weight: 900;
  color: #FFFFFF;
  text-align: center;
  margin: 0 0 20px 0;
  padding: 0;
}

.history-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
}

.pagination-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFD700;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:hover:not(:disabled) {
  background: #FFD700;
  color: #1A1A1A;
}

.pagination-info {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  font-weight: 600;
}

.schedule-title {
  font-size: 2rem;
  font-weight: 900;
  color: #FFFFFF;
  text-align: center;
  margin: 0 0 24px 0;
  padding: 0;
}

.schedule-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.schedule-item--clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.schedule-item--clickable:hover {
  background: rgba(60, 60, 60, 0.7);
  transform: translateY(-1px);
}

.schedule-date {
  font-weight: 600;
  color: #FFFFFF;
  font-size: 0.95rem;
}

.schedule-course,
.schedule-teacher {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

/* Floating button */
.floating-btn {
  position: fixed;
  bottom: 32px;
  right: 32px;
  padding: 14px 28px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  z-index: 50;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.floating-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

/* Состояния */
.loading,
.empty,
.error {
  text-align: center;
  padding: 24px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
}

.error {
  color: #ffaaaa;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 520px;
  background: #1f1f1f;
  border: 2px solid #FFD700;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.3);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.modal-close {
  background: transparent;
  border: none;
  color: #FFFFFF;
  font-size: 1.6rem;
  cursor: pointer;
}

.modal-body {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-size: 0.75rem;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.6);
}

.detail-value {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.95);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 215, 0, 0.3);
}

.btn-close {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #FFD700;
  background: transparent;
  color: #FFD700;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.btn-close:hover {
  background: #FFD700;
  color: #1A1A1A;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 20px 16px;
  }

  .profile-card {
    flex-direction: column;
    text-align: center;
  }

  .floating-btn {
    bottom: 20px;
    right: 20px;
    padding: 12px 20px;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .dashboard-content {
    padding: 16px 12px;
  }

  .card {
    padding: 16px;
  }

  .profile-card {
    padding: 16px;
  }

  .profile-name {
    font-size: 1.1rem;
  }

  .profile-email {
    font-size: 0.85rem;
  }

  .floating-btn {
    bottom: 16px;
    right: 16px;
    padding: 10px 16px;
    font-size: 0.85rem;
  }
}
</style>
