<!-- src/pages/admin/AdminScheduleView.vue -->
<template>
  <div class="admin-page">
    <main class="admin-main">
      <div class="page-header">
        <h1>Календарь уроков</h1>
      </div>
      <ScheduleView
        :lessons="lessons"
        :lessons-loading="lessonsLoading"
        :lessons-error="lessonsError"
        :on-create-lesson="handleCreateLesson"
        :on-update-lesson="handleUpdateLesson"
        :on-search-user="handleSearchUser"
        :on-get-autocomplete="handleGetAutocomplete"
        :on-get-courses="() => adminGetCourses()"
        :on-get-last-lesson-for-student="handleGetLastLessonForStudent"
        user-role="admin"
        :current-user-email="auth.user?.email || ''"
        @lesson-selected="selectLesson"
        @week-changed="handleWeekChanged"
      />
    </main>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ScheduleView from '../../components/ScheduleView.vue'
import { adminGetLessons, adminCreateLesson, adminUpdateLesson } from '../../api/lessons'
import { adminGetUsersAutocomplete, adminGetCourses } from '../../api/admin'
import { managerSearchUserByEmail } from '../../api/manager'

const auth = useAuthStore()
const router = useRouter()

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

function toISO(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function addDays(date, n) {
  const d = new Date(date)
  d.setDate(d.getDate() + n)
  return d
}

function startOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay() || 7
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() - (day - 1))
  return d
}

const loadLessons = async (params = {}) => {
  lessonsLoading.value = true
  lessonsError.value = null

  try {
    const { data } = await adminGetLessons(params)
    lessons.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load lessons error:', err)
    lessonsError.value = 'Ошибка загрузки уроков'
  } finally {
    lessonsLoading.value = false
  }
}

const handleCreateLesson = async (payload) => {
  try {
    await adminCreateLesson(payload)
    await loadLessons()
  } catch (err) {
    console.error('create lesson error:', err)
    throw err
  }
}

const handleUpdateLesson = async (lessonId, payload) => {
  try {
    const response = await adminUpdateLesson(lessonId, payload)
    await loadLessons()
    // Возвращаем обновленный урок из ответа или находим его в списке
    if (response?.data) {
      return response.data
    }
    // Если ответ не содержит данных, находим обновленный урок в списке
    const updatedLesson = lessons.value.find(l => l.id === lessonId)
    return updatedLesson || null
  } catch (err) {
    console.error('update lesson error:', err)
    throw err
  }
}

const handleSearchUser = async (email, type) => {
  try {
    // Используем эндпоинт менеджера, так как он доступен для админа
    const { data } = await managerSearchUserByEmail(email)
    return data
  } catch (err) {
    // Не логируем 404 как ошибку - это нормально, когда пользователь не найден
    if (err?.response?.status !== 404) {
      console.error('search user error:', err)
    }
    throw err
  }
}

const handleGetAutocomplete = async (role, search = '') => {
  try {
    const { data } = await adminGetUsersAutocomplete(role, search)
    return data
  } catch (err) {
    console.error('get autocomplete error:', err)
    return []
  }
}

const handleGetLastLessonForStudent = async (studentId) => {
  try {
    const { data } = await adminGetLessons({
      student: studentId,
      ordering: '-scheduled_at'
    })
    const list = Array.isArray(data) ? data : data?.results || []
    return list[0] || null
  } catch (err) {
    console.error('get last lesson error:', err)
    return null
  }
}

const selectLesson = (lesson) => {
  console.log('Selected lesson:', lesson)
}

const handleWeekChanged = (params) => {
  loadLessons(params)
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  
  // Загружаем уроки на текущую неделю
  const today = new Date()
  const weekStart = startOfWeek(today)
  const weekEnd = addDays(weekStart, 6)
  
  loadLessons({
    date_from: toISO(weekStart),
    date_to: toISO(weekEnd),
  })
})
</script>


<style scoped>
.admin-page {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  padding: 0;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 20px 24px 0;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  color: #e8eaf6;
  letter-spacing: -1px;
}

.admin-main {
  width: 100%;
  max-width: 100%;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 20px 20px;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 16px 0;
  }

  .page-header h1 {
    font-size: 2rem;
  }

  .admin-main {
    padding: 0 16px 16px;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 12px 0;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .admin-main {
    padding: 0 12px 12px;
  }
}
</style>
