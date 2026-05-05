<!-- src/pages/common/DashboardView.vue -->
<template>
  <div class="unified-dashboard">
    <main class="dashboard-content" aria-labelledby="dashboard-title">
      <h1 id="dashboard-title" class="sr-only">Личный кабинет ученика</h1>

      <div class="main-grid">
        <!-- Левая колонка -->
        <div class="left-column">
          <!-- Профиль пользователя -->
          <section class="card profile-card" aria-labelledby="profile-title">
            <div class="profile-avatar">
              <img v-if="avatarSrc" :src="avatarSrc" alt="" class="avatar-image" />
              <svg v-else viewBox="0 0 100 100" class="avatar-icon" aria-hidden="true">
                <circle cx="50" cy="50" r="50" fill="rgba(255, 255, 255, 0.1)"/>
                <circle cx="50" cy="35" r="15" fill="rgba(255, 255, 255, 0.8)"/>
                <path d="M 20 85 Q 20 65 50 65 Q 80 65 80 85" fill="rgba(255, 255, 255, 0.8)"/>
              </svg>
            </div>
            <div class="profile-info">
              <h2 id="profile-title" class="profile-name">{{ dashboardData?.student_full_name || 'Пользователь' }}</h2>
              <p class="profile-email">{{ dashboardData?.email || '—' }}</p>
              <p v-if="dashboardLoading" class="profile-status">Загружаем профиль...</p>
              <p v-else-if="dashboardError" class="profile-status profile-status--error">{{ dashboardError }}</p>
            </div>
            <router-link :to="{ name: 'edit-profile' }" class="edit-btn">
              Редактировать
            </router-link>
          </section>

          <!-- Осталось занятий -->
          <section class="card balance-section panel-card" aria-labelledby="balance-title">
            <div class="schedule-header">
              <div>
                <h2 id="balance-title" class="schedule-title">Баланс занятий</h2>
                <p class="schedule-subtitle">Доступные уроки ученика</p>
              </div>
              <span class="schedule-count" aria-live="polite">{{ dashboardData?.balance || 0 }}</span>
            </div>

            <div class="balance-body">
              <div class="balance-card" aria-live="polite">
                <span class="balance-value">{{ dashboardData?.balance || 0 }}</span>
                <span class="balance-label">осталось занятий</span>
              </div>
            </div>
          </section>

          <!-- История уроков -->
          <section class="card history-card panel-card" aria-labelledby="history-title">
            <div class="schedule-header">
              <div>
                <h2 id="history-title" class="schedule-title">История уроков</h2>
                <p class="schedule-subtitle">Завершенные занятия и обратная связь</p>
              </div>
              <span class="schedule-count" aria-live="polite">{{ allHistoryLessons.length }}</span>
            </div>

            <div class="schedule-body">
              <div v-if="historyLoading" class="schedule-state loading">Загрузка...</div>
              <div v-else-if="historyError" class="schedule-state error">{{ historyError }}</div>
              <div v-else-if="historyLessons.length === 0" class="schedule-state empty">
                Нет завершенных уроков
              </div>
              <ul v-else class="schedule-list" aria-label="Завершенные уроки">
                <li
                  v-for="lesson in historyLessons"
                  :key="lesson.id"
                  class="schedule-list-item"
                >
                  <button
                    type="button"
                    class="schedule-item schedule-item--split schedule-item--clickable"
                    @click="openLessonDetails(lesson)"
                  >
                    <div class="schedule-time-card">
                      <time class="schedule-date" :datetime="lesson.scheduled_at">
                        {{ formatDate(lesson.scheduled_at) }}
                      </time>
                      <time class="schedule-time" :datetime="lesson.scheduled_at">
                        {{ formatTime(lesson.scheduled_at) }}
                      </time>
                    </div>
                    <div class="schedule-lesson-info">
                      <span class="schedule-course">Курс: {{ lesson.course || '—' }}</span>
                      <span class="schedule-teacher">Преподаватель: {{ lesson.teacher_full_name || 'Не назначен' }}</span>
                    </div>
                  </button>
                </li>
              </ul>
            </div>
            <div class="history-pagination">
              <button
                class="pagination-btn"
                type="button"
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
                type="button"
                :disabled="!canGoHistoryNext"
                @click="handleHistoryNext"
              >
                Вперед
              </button>
            </div>
          </section>
        </div>

        <!-- Правая колонка -->
        <aside class="right-column" aria-label="Ближайшие занятия">
          <!-- Следующие запланированные занятия -->
          <section class="card schedule-card" aria-labelledby="schedule-title">
            <div class="schedule-header">
              <div>
                <h2 id="schedule-title" class="schedule-title">Ближайшие занятия</h2>
                <p class="schedule-subtitle">Запланированные уроки ученика</p>
              </div>
              <span class="schedule-count" aria-live="polite">{{ upcomingLessons.length }}</span>
            </div>

            <div class="schedule-body">
              <div v-if="lessonsLoading" class="schedule-state loading">Загрузка...</div>
              <div v-else-if="lessonsError" class="schedule-state error">{{ lessonsError }}</div>
              <div v-else-if="upcomingLessons.length === 0" class="schedule-state empty">
                Нет запланированных занятий
              </div>
              <ul v-else class="schedule-list schedule-list--upcoming" aria-label="Запланированные уроки">
                <li 
                  v-for="lesson in upcomingLessons" 
                  :key="lesson.id" 
                  class="schedule-item schedule-item--split"
                  :class="{ 'schedule-item--ongoing': isLessonOngoing(lesson) }"
                >
                  <div class="schedule-time-card">
                    <time class="schedule-date" :datetime="lesson.scheduled_at">
                      {{ formatDate(lesson.scheduled_at) }}
                    </time>
                    <time class="schedule-time" :datetime="lesson.scheduled_at">
                      {{ formatTime(lesson.scheduled_at) }}
                    </time>
                  </div>
                  <div class="schedule-lesson-info">
                    <div v-if="isLessonOngoing(lesson)" class="ongoing-badge">
                      <span class="ongoing-dot" aria-hidden="true"></span>
                      Занятие идёт сейчас
                    </div>
                    <span class="schedule-course">Курс: {{ lesson.course || '—' }}</span>
                    <span class="schedule-teacher">Преподаватель: {{ lesson.teacher_full_name || 'Не назначен' }}</span>
                  </div>
                </li>
              </ul>
            </div>
          </section>
        </aside>
      </div>
    </main>

    <!-- Кнопка "Задать вопрос" -->
    <button type="button" class="floating-btn" @click="showRequestForm = true">
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
      <section
        class="modal-content"
        role="dialog"
        aria-modal="true"
        aria-labelledby="lesson-details-title"
        @click.stop
      >
        <div class="modal-header">
          <h3 id="lesson-details-title">Информация об уроке</h3>
          <button type="button" class="modal-close" aria-label="Закрыть окно" @click="closeLessonDetails">×</button>
        </div>
        <dl class="modal-body">
          <div class="detail-item">
            <dt class="detail-label">Дата и время:</dt>
            <dd class="detail-value">
              <time :datetime="selectedHistoryLesson.scheduled_at">
                {{ formatDate(selectedHistoryLesson.scheduled_at) }} в {{ formatTime(selectedHistoryLesson.scheduled_at) }}
              </time>
            </dd>
          </div>
          <div class="detail-item">
            <dt class="detail-label">Курс:</dt>
            <dd class="detail-value">{{ selectedHistoryLesson.course || '—' }}</dd>
          </div>
          <div class="detail-item">
            <dt class="detail-label">Преподаватель:</dt>
            <dd class="detail-value">{{ selectedHistoryLesson.teacher_full_name || 'Не назначен' }}</dd>
          </div>
          <div class="detail-item detail-item--full" v-if="selectedHistoryLesson.feedback">
            <dt class="detail-label">Обратная связь:</dt>
            <dd class="detail-value feedback-text">{{ selectedHistoryLesson.feedback }}</dd>
          </div>
        </dl>
        <div class="modal-footer">
          <button type="button" class="btn-close" @click="closeLessonDetails">Закрыть</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ManagerRequestForm from '../../components/ManagerRequestForm.vue'
import { getDashboard, studentGetLessons, studentCreateRequest } from '../../api/student'
import { resolveMediaUrl } from '../../utils/media'

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
  const lessonDurationMinutes = 60 // Длительность урока в минутах
  
  return lessons.value
    .filter(lesson => {
      if (!lesson.scheduled_at) return false
      const lessonDate = new Date(lesson.scheduled_at)
      const lessonEndDate = new Date(lessonDate.getTime() + lessonDurationMinutes * 60 * 1000)
      
      // Показываем если урок ещё не закончился (включая текущие)
      return lessonEndDate >= now && lesson.status === 'PLANNED'
    })
    .sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at))
    .slice(0, 3) // Максимум 3 занятия
})

const isLessonOngoing = (lesson) => {
  if (!lesson.scheduled_at) return false
  
  const now = new Date()
  const lessonDate = new Date(lesson.scheduled_at)
  const lessonDurationMinutes = 60 // Длительность урока в минутах
  const lessonEndDate = new Date(lessonDate.getTime() + lessonDurationMinutes * 60 * 1000)
  
  // Урок идёт прямо сейчас, если текущее время между началом и концом урока
  return now >= lessonDate && now <= lessonEndDate
}

const historyTotalPages = computed(() => {
  return allHistoryLessons.value.length > 0 ? Math.ceil(allHistoryLessons.value.length / historyPageSize) : 1
})

const canGoHistoryPrev = computed(() => {
  return historyPage.value > 1
})

const canGoHistoryNext = computed(() => {
  return historyPage.value < historyTotalPages.value
})

const avatarSrc = computed(() => {
  const source =
    dashboardData.value?.avatar_url ||
    auth.user?.avatar_url ||
    dashboardData.value?.avatar ||
    auth.user?.avatar ||
    ''
  return resolveMediaUrl(source)
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

.unified-dashboard,
.unified-dashboard * {
  box-sizing: border-box;
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 32px 112px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.main-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 32px;
  align-items: start;
}

.left-column,
.right-column {
  min-width: 0;
}

/* Карточки */
.card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  min-width: 0;
  overflow: hidden;
}

.panel-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Профиль */
.profile-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
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

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.profile-info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1.2;
  color: #FFFFFF;
  margin: 0;
  overflow-wrap: anywhere;
}

.profile-email {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  overflow-wrap: anywhere;
}

.profile-status {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.85rem;
}

.profile-status--error {
  color: #ffaaaa;
}

.edit-btn {
  min-height: 40px;
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
  justify-self: end;
}

.edit-btn:hover {
  background: #FFD700;
  color: #1A1A1A;
}

.balance-body {
  min-width: 0;
  max-width: 100%;
}

.balance-card {
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
}

.balance-value {
  color: #FFFFFF;
  font-size: 2.4rem;
  font-weight: 900;
  line-height: 1;
}

.balance-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  font-weight: 600;
}

.schedule-card {
  min-height: 360px;
}

/* История уроков */
.history-card {
  min-height: 420px;
}

.history-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.pagination-btn {
  min-width: 96px;
  min-height: 40px;
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
  border-color: #FFD700;
}

.pagination-info {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  font-weight: 600;
}

.schedule-title {
  font-size: 1.8rem;
  font-weight: 900;
  line-height: 1.15;
  color: #FFFFFF;
  text-align: left;
  margin: 0;
  padding: 0;
  overflow-wrap: anywhere;
}

.schedule-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.28);
  min-width: 0;
  max-width: 100%;
}

.schedule-header > div {
  min-width: 0;
}

.schedule-subtitle {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.92rem;
  line-height: 1.35;
}

.schedule-count {
  flex: 0 0 auto;
  min-width: 42px;
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #FFD700;
  border-radius: 8px;
  color: #FFD700;
  font-size: 1.1rem;
  font-weight: 900;
  line-height: 1;
}

.schedule-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 260px;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}

.schedule-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  list-style: none;
  margin: 0;
  padding: 0;
  min-width: 0;
  width: 100%;
  max-width: 100%;
  overflow: visible;
}

.schedule-list--upcoming {
  justify-content: flex-start;
}

.schedule-list-item {
  display: flex;
  min-width: 0;
  max-width: 100%;
}

.schedule-item {
  appearance: none;
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 100%;
  color: inherit;
  font: inherit;
  text-align: left;
  overflow: hidden;
}

.schedule-item--split {
  display: grid;
  grid-template-columns: minmax(88px, 116px) minmax(0, 1fr);
  align-items: stretch;
  gap: 14px;
  min-height: 104px;
  min-width: 0;
  max-width: 100%;
}

.schedule-item--ongoing {
  background: rgba(255, 215, 0, 0.15);
  border-color: #FFD700;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
  }
  50% {
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
  }
}

.schedule-item--clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.schedule-item--clickable:hover,
.schedule-item--clickable:focus-visible {
  background: rgba(60, 60, 60, 0.7);
  border-color: #FFD700;
  transform: translateY(-1px);
}

.schedule-item--clickable:focus-visible,
.edit-btn:focus-visible,
.pagination-btn:focus-visible,
.floating-btn:focus-visible,
.modal-close:focus-visible,
.btn-close:focus-visible {
  outline: 3px solid rgba(255, 215, 0, 0.55);
  outline-offset: 3px;
}

.schedule-date {
  font-weight: 600;
  color: #FFFFFF;
  font-size: 0.95rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.schedule-time-card {
  min-width: 0;
  max-width: 100%;
  padding: 12px;
  border-radius: 8px;
  background: rgba(26, 26, 26, 0.45);
  border: 1px solid rgba(255, 215, 0, 0.35);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  text-align: center;
}

.schedule-time-card .schedule-date {
  font-size: 0.84rem;
  color: rgba(255, 255, 255, 0.76);
}

.schedule-time {
  color: #FFFFFF;
  font-size: 1.35rem;
  font-weight: 900;
  line-height: 1;
}

.schedule-lesson-info {
  min-width: 0;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.ongoing-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 6px 12px;
  width: fit-content;
  max-width: 100%;
  background: rgba(255, 76, 76, 0.2);
  border: 1px solid #ff4c4c;
  border-radius: 6px;
  color: #ff4c4c;
  font-size: 0.85rem;
  font-weight: 700;
  text-align: center;
  margin: 4px 0;
  animation: blink 1.5s ease-in-out infinite;
}

.ongoing-dot {
  width: 8px;
  height: 8px;
  background: #ff4c4c;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(255, 76, 76, 0.7);
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.schedule-course,
.schedule-teacher {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
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
  border-color: #FFD700;
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

.schedule-state {
  flex: 1;
  min-height: 220px;
  min-width: 0;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed rgba(255, 215, 0, 0.25);
  border-radius: 8px;
  background: rgba(50, 50, 50, 0.35);
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
  max-height: calc(100dvh - 40px);
  background: #1f1f1f;
  border: 2px solid #FFD700;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  margin: 0;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: auto;
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
  margin: 0;
  overflow-wrap: anywhere;
}

.detail-item--full {
  margin-top: 8px;
}

.feedback-text {
  background: rgba(60, 60, 60, 0.5);
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid #FFD700;
  white-space: pre-wrap;
  line-height: 1.6;
  margin-top: 6px;
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
  border-color: #FFD700;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 20px 16px 104px;
  }

  .profile-card {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
  }

  .profile-info {
    align-items: center;
  }

  .edit-btn {
    justify-self: stretch;
    text-align: center;
  }

  .floating-btn {
    bottom: 20px;
    right: 20px;
    padding: 12px 20px;
    font-size: 0.9rem;
  }

  .schedule-card {
    min-height: auto;
  }

  .schedule-body {
    min-height: 220px;
  }
}

@media (max-width: 480px) {
  .dashboard-content {
    padding: 16px 12px 96px;
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

  .schedule-title {
    font-size: 1.45rem;
  }

  .schedule-header {
    align-items: stretch;
  }

  .schedule-count {
    min-width: 38px;
    min-height: 38px;
  }

  .schedule-item--split {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .schedule-time-card {
    align-items: center;
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }

  .schedule-time {
    font-size: 1.15rem;
  }

  .history-pagination {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .pagination-info {
    grid-column: 1 / -1;
    order: -1;
    text-align: center;
  }

  .floating-btn {
    left: 16px;
    bottom: 16px;
    right: 16px;
    padding: 10px 16px;
    font-size: 0.85rem;
  }
}
</style>
