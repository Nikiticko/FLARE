<!-- src/pages/admin/AdminCoursesView.vue -->
<template>
  <div class="admin-page">
    <main class="admin-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">📚 Управление курсами</h1>
          <p class="subtitle">Создание и редактирование курсов</p>
        </div>
      </div>
      <div class="admin-grid">
      <section class="admin-card price-card">
        <div class="section-header">
          <div class="section-title-group">
            <div class="section-icon">💳</div>
            <h2>Стоимость занятия</h2>
          </div>
        </div>

        <p v-if="priceLoading" class="status-text">Загружаем текущую стоимость...</p>
        <p v-if="priceError" class="error">{{ priceError }}</p>

        <form v-if="!priceLoading" @submit.prevent="saveLessonPrice" class="price-form">
          <label class="field">
            <span>Стоимость одного занятия (₽)</span>
            <input
              v-model.number="lessonPriceForm"
              type="number"
              min="1"
              max="100000"
              step="1"
              required
            />
          </label>

          <p class="price-hint">Изменение применяется ко всем новым оплатам сразу после сохранения.</p>

          <div class="form-actions">
            <button type="submit" class="btn primary" :disabled="priceSaving">
              {{ priceSaving ? 'Сохраняем...' : 'Сохранить стоимость' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Список курсов -->
      <section class="admin-card">
        <div class="section-header">
          <div class="section-title-group">
            <div class="section-icon">📚</div>
            <h2>Курсы</h2>
          </div>
          <button class="btn primary" @click="openCreateCourse">+ Создать курс</button>
        </div>

        <p v-if="loading" class="status-text">Загружаем курсы...</p>
        <p v-if="error" class="error">{{ error }}</p>

        <div v-if="!loading && courses.length" class="courses-list">
          <div
            v-for="course in courses"
            :key="course.id"
            class="course-item"
            :class="{ 'course-item--active': editingCourseId === course.id }"
          >
            <div class="course-item-header">
              <h3>{{ course.title }}</h3>
              <div class="course-item-actions">
                <button class="btn-icon" @click="editCourse(course)" title="Редактировать">
                  ✏️
                </button>
                <button class="btn-icon" @click="deleteCourse(course.id)" title="Удалить">
                  🗑️
                </button>
              </div>
            </div>
            <p v-if="course.description" class="course-description-preview">{{ course.description }}</p>
          </div>
        </div>

        <p v-if="!loading && !courses.length" class="empty-state">
          Курсов пока нет. Создайте первый курс.
        </p>
      </section>
      </div>

      <!-- Окно редактирования курса (поверх интерфейса) -->
      <div v-if="showCourseForm" class="course-form-overlay" @click.self="closeCourseForm">
        <div class="course-form-panel">
          <div class="course-form-header">
            <h2 class="course-form-title">{{ editingCourseId ? 'Редактировать курс' : 'Новый курс' }}</h2>
            <button type="button" class="course-form-close" @click="closeCourseForm" title="Закрыть">×</button>
          </div>
          <form @submit.prevent="saveCourse" class="course-form">
            <label class="field">
              <span>Название *</span>
              <input v-model="courseForm.title" type="text" required placeholder="Название курса" />
            </label>
            <label class="field">
              <span>Описание</span>
              <textarea
                v-model="courseForm.description"
                rows="10"
                placeholder="Описание курса с разметкой. Переносы строк сохраняются."
              ></textarea>
            </label>
            <div class="form-actions">
              <button type="submit" class="btn primary" :disabled="saving">
                {{ saving ? 'Сохранение...' : 'Сохранить' }}
              </button>
              <button type="button" class="btn secondary" @click="closeCourseForm">Отмена</button>
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
import {
  adminGetCourses,
  adminCreateCourse,
  adminUpdateCourse,
  adminDeleteCourse,
  adminGetLessonPrice,
  adminUpdateLessonPrice,
} from '../../api/admin'

const auth = useAuthStore()
const router = useRouter()

const courses = ref([])
const loading = ref(false)
const error = ref(null)
const saving = ref(false)
const priceLoading = ref(false)
const priceSaving = ref(false)
const priceError = ref(null)
const lessonPriceForm = ref(1000)

// Форма (inline)
const showCourseForm = ref(false)
const editingCourseId = ref(null)

const courseForm = ref({
  title: '',
  description: '',
})

// Загрузка курсов
const loadCourses = async () => {
  loading.value = true
  error.value = null
  try {
    const { data } = await adminGetCourses()
    courses.value = data
  } catch (err) {
    console.error('Ошибка загрузки курсов:', err)
    error.value = 'Ошибка загрузки курсов'
  } finally {
    loading.value = false
  }
}

const openCreateCourse = () => {
  editingCourseId.value = null
  courseForm.value = { title: '', description: '' }
  showCourseForm.value = true
}

const closeCourseForm = () => {
  showCourseForm.value = false
  editingCourseId.value = null
}

const editCourse = (course) => {
  editingCourseId.value = course.id
  courseForm.value = {
    title: course.title,
    description: course.description || '',
  }
  showCourseForm.value = true
}

const saveCourse = async () => {
  saving.value = true
  try {
    if (editingCourseId.value) {
      await adminUpdateCourse(editingCourseId.value, courseForm.value)
    } else {
      await adminCreateCourse(courseForm.value)
    }
    await loadCourses()
    closeCourseForm()
  } catch (err) {
    console.error('Ошибка сохранения курса:', err)
    alert('Ошибка сохранения курса: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
  } finally {
    saving.value = false
  }
}

const deleteCourse = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот курс?')) return
  try {
    await adminDeleteCourse(id)
    if (editingCourseId.value === id) {
      closeCourseForm()
    }
    await loadCourses()
  } catch (err) {
    console.error('Ошибка удаления курса:', err)
    alert('Ошибка удаления курса: ' + (err?.response?.data?.detail || 'Неизвестная ошибка'))
  }
}

const loadLessonPrice = async () => {
  priceLoading.value = true
  priceError.value = null
  try {
    const { data } = await adminGetLessonPrice()
    lessonPriceForm.value = Number(data?.lesson_price_rub || 1000)
  } catch (err) {
    console.error('Ошибка загрузки стоимости занятия:', err)
    priceError.value = 'Ошибка загрузки стоимости занятия'
  } finally {
    priceLoading.value = false
  }
}

const saveLessonPrice = async () => {
  const value = Number(lessonPriceForm.value)
  if (!Number.isInteger(value) || value <= 0) {
    alert('Введите корректную стоимость (целое число больше 0).')
    return
  }

  const confirmed = confirm(`Подтвердите изменение стоимости занятия на ${value} ₽`)
  if (!confirmed) {
    return
  }

  priceSaving.value = true
  priceError.value = null
  try {
    await adminUpdateLessonPrice(value)
    await loadLessonPrice()
  } catch (err) {
    console.error('Ошибка сохранения стоимости занятия:', err)
    priceError.value = err?.response?.data?.detail || 'Ошибка сохранения стоимости занятия'
  } finally {
    priceSaving.value = false
  }
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadLessonPrice()
  loadCourses()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.admin-page {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.title-block {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: #ffffff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  letter-spacing: -1px;
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}

.admin-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 32px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  overflow-y: auto;
}

.admin-grid {
  display: grid;
  grid-template-columns: minmax(280px, 380px) 1fr;
  gap: 20px;
}

.price-card {
  align-self: start;
}

.price-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.price-hint {
  margin: 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 0.92rem;
  line-height: 1.45;
}

.admin-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.4s ease-out;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.section-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

.section-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.status-text {
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 40px;
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.error {
  color: #ffffff;
  text-align: center;
  padding: 20px;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.4);
  border-radius: 12px;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.empty-state {
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  padding: 40px;
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.courses-list {
  display: grid;
  gap: 20px;
}

.course-item {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.course-item:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.course-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.course-item-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.course-item-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 8px 12px;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.course-description-preview {
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.course-item--active {
  border-color: rgba(255, 215, 0, 0.6);
  box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.3);
}

/* Окно редактирования (поверх интерфейса) */
.course-form-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: overlayFadeIn 0.2s ease;
}

@keyframes overlayFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.course-form-panel {
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  background: rgba(26, 26, 26, 0.98);
  border: 1px solid rgba(255, 215, 0, 0.4);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: panelSlideIn 0.25s ease;
}

@keyframes panelSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.course-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.course-form-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: #FFD700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.course-form-close {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.course-form-close:hover {
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
}

.course-form .field {
  margin-bottom: 20px;
}

.course-form .field span {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  font-weight: 600;
}

.course-form input,
.course-form textarea {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(0, 0, 0, 0.3);
  color: #ffffff;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.course-form input::placeholder,
.course-form textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.course-form input:focus,
.course-form textarea:focus {
  outline: none;
  border-color: #FFD700;
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.2);
}

.course-form textarea {
  resize: vertical;
  min-height: 150px;
  white-space: pre-wrap;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.form-actions .btn {
  flex: 1;
}

.form-actions .btn.secondary {
  background: transparent;
  color: #FFD700;
  border: 1px solid rgba(255, 215, 0, 0.5);
}

.form-actions .btn.secondary:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FFD700;
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
  text-decoration: none;
}

.btn.primary {
  background: #FFD700;
  color: #1A1A1A;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn.primary:hover:not(:disabled) {
  background: #FF8C00;
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.course-form .field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@media (max-width: 768px) {
  .admin-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .section-header .btn {
    width: 100%;
  }
}
</style>
