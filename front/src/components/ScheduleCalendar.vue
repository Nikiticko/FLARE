<!-- src/components/ScheduleCalendar.vue -->
<template>
  <div class="schedule-calendar">
    <!-- Панель управления неделей -->
    <section class="admin-card controls-card">
      <div class="controls-row">
        <button @click="shiftWeek(-1)">‹ Предыдущая неделя</button>
        <button @click="goToday">Сегодня</button>
        <button @click="shiftWeek(1)">Следующая неделя ›</button>
      </div>
      <div class="week-label">
        Неделя: {{ weekRangeLabel }}
      </div>
      <p class="hint">
        Клик по пустой ячейке создаёт урок на выбранные дату и время.
      </p>
    </section>

    <!-- КАЛЕНДАРЬ -->
    <section class="admin-card calendar-card">
      <div class="calendar">
        <!-- Заголовки дней -->
        <div class="calendar-header-row">
          <div class="calendar-cell time-col"></div>
          <div
            v-for="day in weekDays"
            :key="day.iso"
            class="calendar-cell day-col"
          >
            <div class="day-name">{{ day.weekday }}</div>
            <div class="day-date">{{ day.display }}</div>
          </div>
        </div>

        <!-- Тело календаря -->
        <div class="calendar-body" ref="calendarBodyRef">
          <div
            v-if="currentTimeIndicator"
            class="current-time-indicator"
            :style="currentTimeIndicator.style"
          >
          </div>
          <div v-for="hour in timeSlots" :key="hour" class="calendar-row">
            <div class="calendar-cell time-col">
              {{ formatHour(hour) }}
            </div>
            <div
              v-for="day in weekDays"
              :key="day.iso + '-' + hour"
              class="calendar-cell slot"
              @click="openCreate(day.iso, hour)"
            >
              <div
                v-for="lesson in lessonsBySlot[day.iso + '-' + hour] || []"
                :key="lesson.id"
                class="lesson-card"
                @click.stop="selectLesson(lesson)"
              >
                <div class="lesson-title">
                  {{ lesson.student_email || ('Уч. ID ' + lesson.student) }}
                </div>
                <div class="lesson-sub">
                  Препод: {{ lesson.teacher_email || ('ID ' + lesson.teacher) }}
                </div>
                <div class="lesson-status">
                  {{ lesson.status }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <p v-if="lessonsLoading" class="status-text">Загружаем уроки...</p>
      <p v-if="lessonsError" class="error">{{ lessonsError }}</p>
    </section>

    <!-- ДЕТАЛИ УРОКА -->
    <section v-if="activeLesson" class="admin-card lesson-info-card">
      <h2>Информация об уроке</h2>
      <p><strong>Ученик:</strong> {{ activeLesson.student_email }}</p>
      <p v-if="activeLesson.parent_full_name"><strong>Родитель:</strong> {{ activeLesson.parent_full_name }}</p>
      <p><strong>Преподаватель:</strong> {{ activeLesson.teacher_email }}</p>
      <p><strong>Статус:</strong> {{ activeLesson.status }}</p>
      <p><strong>Время:</strong> {{ formatDateTime(activeLesson.scheduled_at) }}</p>
      <p>
        <strong>Ссылка:</strong>
        <span v-if="activeLesson.link">
          <a :href="activeLesson.link" target="_blank">{{ activeLesson.link }}</a>
        </span>
        <span v-else>—</span>
      </p>
      <p><strong>Комментарий:</strong> {{ activeLesson.comment || '—' }}</p>
    </section>

    <!-- Модальное окно создания урока -->
    <div v-if="showCreateModal" class="modal-backdrop" @click="closeCreate">
      <div class="modal" @click.stop>
        <h2>Создать урок</h2>
        <form @submit.prevent="handleCreate">
          <label class="field">
            <span>Дата</span>
            <input v-model="formDate" type="date" required />
          </label>
          <label class="field">
            <span>Время</span>
            <input v-model="formTime" type="time" required />
          </label>
          <label class="field">
            <span>ID ученика</span>
            <input v-model="formStudentId" type="number" min="1" required />
          </label>
          <label class="field">
            <span>ID учителя</span>
            <input v-model="formTeacherId" type="number" min="1" required />
          </label>
          <label class="field">
            <span>Ссылка на урок *</span>
            <input v-model="formLink" type="text" placeholder="Discord (по умолчанию)" required />
          </label>
          <label class="field">
            <span>Комментарий</span>
            <textarea v-model="formComment" rows="2"></textarea>
          </label>
          <div class="modal-actions">
            <button type="submit" :disabled="createLoading">
              {{ createLoading ? 'Создаём...' : 'Создать' }}
            </button>
            <button type="button" @click="closeCreate">Отмена</button>
          </div>
          <p v-if="createError" class="error">{{ createError }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  lessons: {
    type: Array,
    default: () => []
  },
  lessonsLoading: {
    type: Boolean,
    default: false
  },
  lessonsError: {
    type: String,
    default: null
  },
  onCreateLesson: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['lesson-selected', 'week-changed'])

// =====================================
// ДАТЫ
// =====================================

function startOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay() || 7
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() - (day - 1))
  return d
}

function addDays(date, n) {
  const d = new Date(date)
  d.setDate(d.getDate() + n)
  return d
}

function toISO(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatRu(date) {
  const d = new Date(date)
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
}

const currentDate = ref(new Date())

const weekStart = computed(() => startOfWeek(currentDate.value))

const weekDays = computed(() => {
  const names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
  const arr = []
  for (let i = 0; i < 7; i++) {
    const d = addDays(weekStart.value, i)
    arr.push({
      date: d,
      iso: toISO(d),
      weekday: names[i],
      display: formatRu(d),
    })
  }
  return arr
})

const weekRangeLabel = computed(() => {
  const start = weekStart.value
  const end = addDays(start, 6)
  return `${formatRu(start)} — ${formatRu(end)}`
})

// =====================================
// УРОКИ
// =====================================

const timeSlots = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
const slotHeight = 40
const timeColWidth = 70

const calendarBodyRef = ref(null)
const calendarBodyWidth = ref(0)

const now = ref(new Date())
let nowTimer = null

const updateNow = () => {
  now.value = new Date()
}

const updateCalendarBodyWidth = () => {
  if (calendarBodyRef.value) {
    calendarBodyWidth.value = calendarBodyRef.value.clientWidth
  }
}

const currentTimeIndicator = computed(() => {
  if (!calendarBodyWidth.value || !weekDays.value.length) return null

  const current = now.value
  const todayIso = toISO(current)
  const dayIndex = weekDays.value.findIndex(day => day.iso === todayIso)
  if (dayIndex < 0) return null

  const startHour = timeSlots[0]
  const endHour = timeSlots[timeSlots.length - 1] + 1
  const totalMinutes = current.getHours() * 60 + current.getMinutes()
  if (totalMinutes < startHour * 60 || totalMinutes > endHour * 60) return null

  const minutesFromStart = totalMinutes - startHour * 60
  const top = (minutesFromStart / 60) * slotHeight

  const dayWidth = (calendarBodyWidth.value - timeColWidth) / 7
  const left = timeColWidth + dayWidth * dayIndex

  const label = current.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })

  return {
    style: {
      top: `${top}px`,
      left: `${left}px`,
      width: `${dayWidth}px`,
    },
    label,
  }
})

const activeLesson = ref(null)

// Группируем уроки по слотам YYYY-MM-DD-HH
const lessonsBySlot = computed(() => {
  const map = {}
  for (const L of props.lessons) {
    if (!L.scheduled_at) continue
    const dt = new Date(L.scheduled_at)
    const key = `${toISO(dt)}-${dt.getHours()}`
    if (!map[key]) map[key] = []
    map[key].push(L)
  }
  return map
})

const formatHour = (h) => `${String(h).padStart(2, '0')}:00`

const formatDateTime = (val) => {
  const d = new Date(val)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// =====================================
// СОЗДАНИЕ УРОКА
// =====================================

const showCreateModal = ref(false)
const formDate = ref('')
const formTime = ref('')
const formStudentId = ref('')
const formTeacherId = ref('')
const formLink = ref('Discord')
const formComment = ref('')

const createLoading = ref(false)
const createError = ref('')

const openCreate = (iso, hour) => {
  formDate.value = iso
  formTime.value = `${String(hour).padStart(2, '0')}:00`
  formStudentId.value = ''
  formTeacherId.value = ''
  formLink.value = 'Discord'
  formComment.value = ''
  createError.value = ''
  showCreateModal.value = true
}

const closeCreate = () => {
  showCreateModal.value = false
}

const handleCreate = async () => {
  createError.value = ''

  const payload = {
    student: Number(formStudentId.value),
    teacher: Number(formTeacherId.value),
    scheduled_at: `${formDate.value}T${formTime.value}`,
    link: formLink.value?.trim() || 'Discord',
    comment: formComment.value || '',
  }

  createLoading.value = true

  try {
    await props.onCreateLesson(payload)
    showCreateModal.value = false
  } catch (err) {
    console.error(err)
    createError.value = err?.response?.data?.detail || 'Ошибка создания урока'
  }

  createLoading.value = false
}

const selectLesson = (lesson) => {
  activeLesson.value = lesson
  emit('lesson-selected', lesson)
}

// =====================================
// НАВИГАЦИЯ НЕДЕЛИ
// =====================================

const shiftWeek = (delta) => {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + delta * 7)
  currentDate.value = d
  emit('week-changed', {
    date_from: toISO(weekStart.value),
    date_to: toISO(addDays(weekStart.value, 6))
  })
}

const goToday = () => {
  currentDate.value = new Date()
  emit('week-changed', {
    date_from: toISO(weekStart.value),
    date_to: toISO(addDays(weekStart.value, 6))
  })
}

onMounted(() => {
  updateNow()
  updateCalendarBodyWidth()
  nowTimer = setInterval(updateNow, 60000)
  window.addEventListener('resize', updateCalendarBodyWidth)
})

onUnmounted(() => {
  if (nowTimer) clearInterval(nowTimer)
  window.removeEventListener('resize', updateCalendarBodyWidth)
})

// Экспортируем функции для внешнего использования
defineExpose({
  weekStart,
  weekEnd: computed(() => addDays(weekStart.value, 6)),
  shiftWeek,
  goToday
})
</script>

<style scoped>
.schedule-calendar {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.admin-card {
  background: #111;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #333;
}

.controls-card {
  grid-column: 1 / -1;
}

.calendar-card {
  grid-column: 1 / 2;
}

.lesson-info-card {
  grid-column: 2 / 3;
}

.controls-row button {
  margin-right: 8px;
  padding: 6px 10px;
  background: #1e88e5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: white;
}

.controls-row button:hover {
  background: #1565c0;
}

.week-label {
  margin: 12px 0;
  color: #aaa;
}

.hint {
  color: #888;
  font-size: 0.9rem;
  margin-top: 8px;
}

.calendar {
  --calendar-scrollbar: 12px;
  --slot-height: 40px;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
  font-size: 14px;
}

.calendar-header-row,
.calendar-row {
  display: grid;
  grid-template-columns: 70px repeat(7, 1fr);
  box-sizing: border-box;
}

.calendar-row {
  height: var(--slot-height);
}

.calendar-header-row {
  padding-right: var(--calendar-scrollbar);
}

.time-col {
  background: #101010;
  text-align: right;
  padding-right: 8px;
  color: #aaa;
}

.day-col {
  background: #151515;
  text-align: center;
  border-right: 1px solid #222;
  padding: 8px;
}

.day-name {
  font-weight: 600;
  color: #fff;
}

.day-date {
  font-size: 0.85rem;
  color: #aaa;
  margin-top: 4px;
}

.calendar-body {
  max-height: 600px;
  overflow-y: auto;
  scrollbar-gutter: stable;
  position: relative;
}

.current-time-indicator {
  position: absolute;
  height: 2px;
  background: #FFD700;
  z-index: 4;
  pointer-events: none;
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.6);
}

.current-time-indicator::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #FFD700;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.8);
}

.slot {
  cursor: pointer;
  position: relative;
  min-height: var(--slot-height);
  border-right: 1px solid #222;
  border-bottom: 1px solid #222;
  padding: 2px;
}

.slot:hover {
  background: #1a1a1a;
}

.lesson-card {
  background: #1e88e5;
  color: white;
  border-radius: 6px;
  padding: 4px 6px;
  margin: 2px 0;
  font-size: 12px;
}

.lesson-title {
  font-weight: bold;
}

.lesson-sub {
  font-size: 11px;
  opacity: 0.9;
  margin-top: 2px;
}

.lesson-status {
  font-size: 11px;
  margin-top: 2px;
  opacity: 0.8;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: 340px;
  background: #111;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 20px;
  color: #f5f5f5;
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
}

.field span {
  margin-bottom: 4px;
  color: #aaa;
  font-size: 0.9rem;
}

.field input,
.field textarea {
  background: #000;
  border: 1px solid #444;
  color: white;
  padding: 8px;
  border-radius: 6px;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: #1e88e5;
}

.modal-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.modal-actions button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.modal-actions button[type="submit"] {
  background: #1e88e5;
  color: white;
}

.modal-actions button[type="submit"]:hover:not(:disabled) {
  background: #1565c0;
}

.modal-actions button[type="submit"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-actions button[type="button"] {
  background: #333;
  color: white;
}

.modal-actions button[type="button"]:hover {
  background: #444;
}

.error {
  color: #ff6b6b;
  margin-top: 8px;
  font-size: 0.9rem;
}

.status-text {
  font-size: 13px;
  color: #aaa;
  margin-top: 8px;
}

.lesson-info-card h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #fff;
}

.lesson-info-card p {
  margin: 8px 0;
  color: #ccc;
}

.lesson-info-card a {
  color: #1e88e5;
  text-decoration: none;
}

.lesson-info-card a:hover {
  text-decoration: underline;
}
</style>








