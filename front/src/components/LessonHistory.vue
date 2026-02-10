<!-- src/components/LessonHistory.vue -->
<template>
  <div class="lesson-history-card card">
    <div class="card-header">
      <h2>История занятий</h2>
      <button @click="loadLessons" class="btn-refresh" :disabled="lessonsLoading">
        {{ lessonsLoading ? 'Загрузка...' : 'Обновить' }}
      </button>
    </div>
    <div v-if="lessonsLoading" class="loading">Загрузка истории занятий...</div>
    <div v-else-if="lessonsError" class="error">{{ lessonsError }}</div>
    <div v-else-if="completedLessons.length === 0" class="empty">
      У вас пока нет завершенных занятий
    </div>
    <div v-else class="lessons-list">
      <div 
        v-for="lesson in completedLessons" 
        :key="lesson.id" 
        class="lesson-item"
        @click="openLessonDetails(lesson)"
      >
        <div class="lesson-date">
          <div class="date-value">{{ formatDateTime(lesson.scheduled_at) }}</div>
        </div>
        <div class="lesson-info">
          <div class="lesson-teacher">
            <span class="info-label">Преподаватель:</span>
            <span class="info-value">{{ lesson.teacher_full_name || 'Не назначен' }}</span>
          </div>
          <div class="lesson-status" :class="'status-' + lesson.status.toLowerCase()">
            {{ getStatusText(lesson.status) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно с деталями занятия -->
    <div v-if="selectedLesson" class="modal-overlay" @click="closeLessonDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Информация о занятии</h3>
          <button class="modal-close" @click="closeLessonDetails">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <span class="detail-label">Дата и время:</span>
            <span class="detail-value">{{ formatDateTime(selectedLesson.scheduled_at) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Преподаватель:</span>
            <span class="detail-value">{{ selectedLesson.teacher_full_name || 'Не назначен' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Статус:</span>
            <span class="detail-value">
              <span class="lesson-status" :class="'status-' + selectedLesson.status.toLowerCase()">
                {{ getStatusText(selectedLesson.status) }}
              </span>
            </span>
          </div>
          <div v-if="selectedLesson.link" class="detail-item">
            <span class="detail-label">Ссылка на урок:</span>
            <span class="detail-value link-text">{{ selectedLesson.link }}</span>
          </div>
          <div v-if="selectedLesson.feedback" class="detail-item detail-item--full">
            <span class="detail-label">Обратная связь по уроку:</span>
            <div class="detail-value feedback-text">{{ selectedLesson.feedback }}</div>
          </div>
          <div class="detail-item">
            <span class="detail-label">Списано с баланса:</span>
            <span class="detail-value">{{ selectedLesson.debited_from_balance ? 'Да' : 'Нет' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Создано:</span>
            <span class="detail-value">{{ formatDateTime(selectedLesson.created_at) }}</span>
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
import { studentGetLessons } from '../api/student'

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)
const selectedLesson = ref(null)

const loadLessons = async () => {
  lessonsLoading.value = true
  lessonsError.value = null
  try {
    const { data } = await studentGetLessons({
      status: 'DONE',
      ordering: '-scheduled_at' // Сначала самые новые
    })
    lessons.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load lessons history error:', err)
    lessonsError.value = 'Не удалось загрузить историю занятий'
  } finally {
    lessonsLoading.value = false
  }
}

const completedLessons = computed(() => {
  return lessons.value.filter(lesson => lesson.status === 'DONE')
})

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusText = (status) => {
  const statusMap = {
    'PLANNED': 'Запланировано',
    'DONE': 'Проведено',
    'CANCELLED': 'Отменено',
  }
  return statusMap[status] || status
}

const openLessonDetails = (lesson) => {
  selectedLesson.value = lesson
}

const closeLessonDetails = () => {
  selectedLesson.value = null
}

onMounted(() => {
  loadLessons()
})
</script>

<style scoped>
.lesson-history-card {
  /* Убрано grid-column для встраивания в новую сетку */
}

.lesson-history-card.card {
  background: rgba(76, 68, 118, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.lesson-history-card.card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  background: rgba(76, 68, 118, 0.95);
  border-color: rgba(102, 126, 234, 0.6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.card-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #ffffff;
  font-weight: 800;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.btn-refresh {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lesson-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 8px;
  border-left: 4px solid rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
  cursor: pointer;
}

.lesson-item:hover {
  background: rgba(102, 126, 234, 0.35);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transform: translateX(4px);
  border-color: rgba(102, 126, 234, 0.6);
}

.lesson-date {
  font-weight: 600;
  color: #ffffff;
  min-width: 180px;
  flex-shrink: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.date-value {
  font-size: 1rem;
}

.lesson-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.lesson-teacher {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.info-label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.info-value {
  color: #ffffff;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.lesson-status {
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.status-done {
  background: rgba(56, 142, 60, 0.3);
  color: #ffffff;
  border: 1px solid rgba(56, 142, 60, 0.5);
  font-weight: 600;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.loading,
.empty,
.error {
  text-align: center;
  padding: 32px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.error {
  color: #ffb3b3;
  font-weight: 600;
  text-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-body {
  padding: 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.detail-item--full {
  margin-bottom: 24px;
}

.detail-label {
  font-weight: 600;
  color: #666;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #333;
  font-size: 1rem;
  word-break: break-word;
}

.link-text {
  color: #1e88e5;
  font-family: monospace;
  font-size: 0.9rem;
  background: #f5f5f5;
  padding: 8px 12px;
  border-radius: 6px;
  word-break: break-all;
}

.feedback-text {
  background: rgba(102, 126, 234, 0.1);
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  white-space: pre-wrap;
  line-height: 1.6;
  margin-top: 8px;
  color: #333;
}

.modal-footer {
  padding: 24px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
}

.btn-close {
  padding: 10px 24px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-close:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .lesson-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .lesson-date {
    min-width: auto;
    width: 100%;
  }

  .modal-content {
    max-width: 100%;
    margin: 10px;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 16px;
  }
}
</style>






