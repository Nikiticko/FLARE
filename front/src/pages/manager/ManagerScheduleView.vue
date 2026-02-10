<!-- src/pages/manager/ManagerScheduleView.vue -->
<template>
  <div class="manager-page">
    <main class="manager-main">
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
        :on-get-courses="() => applicantGetPublicCourses()"
        :on-get-last-lesson-for-student="handleGetLastLessonForStudent"
        user-role="manager"
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
import { managerGetLessons, managerCreateLesson, managerUpdateLesson, managerSearchUserByEmail, managerGetUsersAutocomplete } from '../../api/manager'
import { applicantGetPublicCourses } from '../../api/applicant'

const auth = useAuthStore()
const router = useRouter()

const lessons = ref([])
const lessonsLoading = ref(false)
const lessonsError = ref(null)

const loadLessons = async (params = {}) => {
  lessonsLoading.value = true
  lessonsError.value = null

  try {
    const { data } = await managerGetLessons(params)
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
    console.log('Creating lesson with payload:', payload)
    const response = await managerCreateLesson(payload)
    console.log('Lesson created successfully:', response)
    await loadLessons()
  } catch (err) {
    console.error('create lesson error:', err)
    console.error('Error response:', err?.response?.data)
    throw err
  }
}

const handleUpdateLesson = async (lessonId, payload) => {
  try {
    const response = await managerUpdateLesson(lessonId, payload)
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
    console.log('Searching user by email:', email)
    const { data } = await managerSearchUserByEmail(email)
    console.log('User found:', data)
    return data
  } catch (err) {
    console.error('search user error:', err)
    console.error('Error response:', err?.response?.data)
    console.error('Error status:', err?.response?.status)
    // Если 401, возможно нужно перелогиниться
    if (err?.response?.status === 401) {
      console.warn('Unauthorized - token may have expired')
    }
    throw err
  }
}

const handleGetAutocomplete = async (role, search = '') => {
  try {
    const { data } = await managerGetUsersAutocomplete(role, search)
    return data
  } catch (err) {
    console.error('get autocomplete error:', err)
    return []
  }
}

const handleGetLastLessonForStudent = async (studentId) => {
  try {
    const { data } = await managerGetLessons({
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
  const weekStart = new Date(today)
  const day = weekStart.getDay() || 7
  weekStart.setHours(0, 0, 0, 0)
  weekStart.setDate(weekStart.getDate() - (day - 1))
  
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekEnd.getDate() + 6)
  
  const toISO = (date) => {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }
  
  loadLessons({
    date_from: toISO(weekStart),
    date_to: toISO(weekEnd),
  })
})
</script>

<style scoped>
.manager-page {
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

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  padding: 16px 24px;
  background: rgba(26, 26, 26, 0.95);
  border-bottom: 1px solid rgba(255, 215, 0, 0.3);
}

.manager-header h1 {
  font-size: 22px;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
}

.manager-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 16px;
  border: 1px solid #FFD700;
  background: rgba(255, 215, 0, 0.2);
  color: #FFD700;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 700;
}

.btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #FFD700;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  color: #FFD700;
  transition: all 0.3s ease;
  font-family: inherit;
}

.btn:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.manager-main {
  width: 100%;
  max-width: 100%;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 20px 20px;
  box-sizing: border-box;
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

@media (max-width: 768px) {
  .page-header {
    padding: 16px 16px 0;
  }

  .page-header h1 {
    font-size: 2rem;
  }

  .manager-main {
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

  .manager-main {
    padding: 0 12px 12px;
  }
}
</style>

