<!-- src/components/ScheduleView.vue -->
<template>
  <div class="schedule-view">
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
    <section class="calendar-wrapper">
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
              @click="handleSlotClick($event, day.iso, hour)"
            >
              <!-- Слот теперь пустой, карточки позиционируются абсолютно -->
            </div>
          </div>
          
          <!-- Абсолютно позиционированные карточки уроков с учетом минут -->
          <div
            v-for="item in lessonsWithPositions"
            :key="item.lesson.id"
            :class="[
              'lesson-card-positioned', 
              `lesson-card--${item.lesson.status?.toLowerCase() || 'planned'}`,
              { 'lesson-card--trial': item.lesson.is_trial }
            ]"
            :style="item.style"
            @click="selectLesson(item.lesson)"
            :title="`ID: ${item.lesson.id}`"
          >
            <div class="lesson-time">
              {{ formatLessonTime(item.lesson.scheduled_at) }}
            </div>
            <div class="lesson-student">
              {{ item.lesson.student_email || ('Уч. ID ' + item.lesson.student) }}
            </div>
            <div v-if="item.lesson.is_trial" class="lesson-trial-badge">Пробное</div>
          </div>
        </div>
      </div>

      <p v-if="lessonsLoading" class="status-text">Загружаем уроки...</p>
      <p v-if="lessonsError" class="error">{{ lessonsError }}</p>
    </section>


    <!-- Модальное окно создания урока -->
    <div v-if="showCreateModal" class="modal-backdrop" @click="closeCreate">
      <div class="modal" @click.stop>
        <h2>Создать урок</h2>
        <form @submit.prevent="handleCreate">
          <!-- Поле для ученика (по email) -->
          <label class="field">
            <span>Email ученика *</span>
            <div class="email-input-wrapper">
              <input
                v-model="formStudentEmail"
                type="email"
                :list="`student-email-list-${canSelectTeacher ? 'manager' : 'teacher'}`"
                placeholder="student@example.com"
                required
                @blur="validateStudentEmail"
                @input="handleStudentEmailInput"
                autocomplete="off"
              />
              <datalist :id="`student-email-list-${canSelectTeacher ? 'manager' : 'teacher'}`">
                <option
                  v-for="student in studentAutocompleteList"
                  :key="student.id"
                  :value="student.email"
                >
                  {{ student.student_full_name || student.email }}
                </option>
              </datalist>
              <button
                type="button"
                class="btn-search"
                @click="searchStudent"
                :disabled="searchingStudent"
              >
                {{ searchingStudent ? '...' : 'Найти' }}
              </button>
            </div>
            <span v-if="foundStudent" class="found-user">
              ✓ Найден: {{ foundStudent.student_full_name || foundStudent.email }}
            </span>
            <span v-if="studentError" class="error-text">{{ studentError }}</span>
          </label>

          <!-- Поле для учителя (для менеджера и админа) -->
          <label v-if="canSelectTeacher" class="field">
            <span>Email учителя *</span>
            <div class="email-input-wrapper">
              <input
                v-model="formTeacherEmail"
                type="email"
                list="teacher-email-list-manager"
                placeholder="teacher@example.com"
                required
                @blur="validateTeacherEmail"
                @input="handleTeacherEmailInput"
                autocomplete="off"
              />
              <datalist id="teacher-email-list-manager">
                <option
                  v-for="teacher in teacherAutocompleteList"
                  :key="teacher.id"
                  :value="teacher.email"
                >
                  {{ teacher.email }}
                </option>
              </datalist>
              <button
                type="button"
                class="btn-search"
                @click="searchTeacher"
                :disabled="searchingTeacher"
              >
                {{ searchingTeacher ? '...' : 'Найти' }}
              </button>
            </div>
            <span v-if="foundTeacher" class="found-user">
              ✓ Найден: {{ foundTeacher.email }}
            </span>
            <span v-if="teacherError" class="error-text">{{ teacherError }}</span>
          </label>

          <!-- Для учителя показываем информацию о текущем учителе -->
          <div v-if="isTeacher" class="field">
            <span>Учитель</span>
            <input :value="currentUserEmail" type="email" disabled />
          </div>

          <!-- Курс (становится курсом по умолчанию для ученика) -->
          <label v-if="coursesList.length" class="field">
            <span>Курс</span>
            <select v-model="formCourseId">
              <option value="">— Не выбран —</option>
              <option
                v-for="c in coursesList"
                :key="c.id"
                :value="c.id"
              >
                {{ c.title }}
              </option>
            </select>
          </label>

          <label class="field">
            <span>Дата *</span>
            <input v-model="formDate" type="date" required />
          </label>

          <label class="field">
            <span>Время *</span>
            <input v-model="formTime" type="time" required />
          </label>

          <label class="field">
            <span>Ссылка на урок *</span>
            <input v-model="formLink" type="text" placeholder="Discord (по умолчанию)" required />
          </label>

          <label class="field">
            <span>Комментарий</span>
            <textarea v-model="formComment" rows="2"></textarea>
          </label>

          <!-- Пробное занятие (для менеджера и админа) -->
          <label v-if="canCreateTrial" class="field" style="flex-direction: row; align-items: center; gap: 8px;">
            <input
              v-model="formIsTrial"
              type="checkbox"
              style="width: auto; margin: 0;"
            />
            <span style="margin: 0;">Пробное занятие (не списывается с баланса)</span>
          </label>

          <div class="modal-actions">
            <button type="submit" :disabled="createLoading || !canCreateLesson">
              {{ createLoading ? 'Создаём...' : 'Создать' }}
            </button>
            <button type="button" @click="closeCreate">Отмена</button>
          </div>

          <p v-if="createError" class="error">{{ createError }}</p>
        </form>
      </div>
    </div>

    <!-- Модальное окно редактирования урока -->
    <div v-if="showEditModal && activeLesson" class="modal-backdrop" @click="closeEdit">
      <div class="modal" @click.stop>
        <h2>Редактировать урок - {{ activeLesson.student_email || 'ID ' + activeLesson.student }}</h2>
        <form @submit.prevent="handleUpdate">
          <label class="field">
            <span>Статус</span>
            <select v-model="editForm.status">
              <option value="PLANNED">Запланировано</option>
              <option value="DONE">Проведено</option>
              <option value="CANCELLED">Отменено</option>
            </select>
          </label>

          <!-- Курс (при смене станет курсом по умолчанию для ученика) -->
          <label v-if="coursesList.length" class="field">
            <span>Курс</span>
            <select v-model="editForm.course_id">
              <option value="">— Не выбран —</option>
              <option
                v-for="c in coursesList"
                :key="c.id"
                :value="c.id"
              >
                {{ c.title }}
              </option>
            </select>
          </label>

          <label class="field">
            <span>Ссылка на урок *</span>
            <input v-model="editForm.link" type="text" placeholder="Discord (по умолчанию)" required />
          </label>

          <label class="field">
            <span>Комментарий</span>
            <textarea v-model="editForm.comment" rows="3" placeholder="Комментарий к уроку"></textarea>
          </label>

          <!-- Поле причины отмены (показывается только при статусе CANCELLED) -->
          <label v-if="editForm.status === 'CANCELLED'" class="field field--required">
            <span>Причина отмены <span class="required-mark">*</span></span>
            <textarea 
              v-model="editForm.cancellation_reason" 
              rows="4" 
              placeholder="Укажите причину отмены занятия"
              required
            ></textarea>
          </label>

          <!-- Поле обратной связи (показывается только при статусе DONE) -->
          <label v-if="editForm.status === 'DONE'" class="field field--required">
            <span>Обратная связь по уроку <span class="required-mark">*</span></span>
            <textarea 
              v-model="editForm.feedback" 
              rows="5" 
              placeholder="Опишите, что было на уроке, какие темы разобрали, что нужно повторить и т.д."
              required
            ></textarea>
          </label>

          <div class="modal-actions">
            <button type="submit" :disabled="updateLoading">
              {{ updateLoading ? 'Сохраняем...' : 'Сохранить' }}
            </button>
            <button type="button" @click="closeEdit">Отмена</button>
          </div>

          <p v-if="updateError" class="error">{{ updateError }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'

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
  },
  onUpdateLesson: {
    type: Function,
    default: null
  },
  onSearchUser: {
    type: Function,
    default: null
  },
  onGetAutocomplete: {
    type: Function,
    default: null
  },
  onGetCourses: {
    type: Function,
    default: null
  },
  onGetLastLessonForStudent: {
    type: Function,
    default: null
  },
  userRole: {
    type: String,
    default: 'manager' // 'manager' или 'teacher'
  },
  currentUserEmail: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['lesson-selected', 'week-changed'])

const auth = useAuthStore()

const isManager = computed(() => props.userRole === 'manager')
const isTeacher = computed(() => props.userRole === 'teacher')
const isAdmin = computed(() => props.userRole === 'admin' || auth.user?.role === 'ADMIN')
// Админ имеет те же возможности, что и менеджер
const canSelectTeacher = computed(() => isManager.value || isAdmin.value)
const canCreateTrial = computed(() => isManager.value || isAdmin.value)
const canEditTime = computed(() => isManager.value || isAdmin.value)
const canEditLesson = computed(() => props.onUpdateLesson !== null)

// Загружаем список курсов при монтировании (для выбора при создании/редактировании)
onMounted(() => {
  if (props.onGetCourses) {
    props.onGetCourses()
      .then((res) => {
        const data = res?.data
        coursesList.value = Array.isArray(data) ? data : data?.results || []
      })
      .catch(() => {
        coursesList.value = []
      })
  }

  updateNow()
  updateCalendarBodyWidth()
  nowTimer = setInterval(updateNow, 60000)
  window.addEventListener('resize', updateCalendarBodyWidth)
})

onUnmounted(() => {
  if (nowTimer) clearInterval(nowTimer)
  window.removeEventListener('resize', updateCalendarBodyWidth)
})

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

const timeSlots = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
const slotHeight = 42
const timeColWidth = 45

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

const lessonsBySlot = computed(() => {
  const map = {}
  console.log('[ScheduleView] lessonsBySlot computing, total lessons:', props.lessons.length)
  
  for (const L of props.lessons) {
    // Проверяем наличие ID - пропускаем уроки без ID
    if (!L.id) {
      console.error('[ScheduleView] Урок без ID обнаружен (пропускаем):', L)
      continue // Пропускаем урок без ID вместо добавления в map
    }
    
    if (!L.scheduled_at) continue
    const dt = new Date(L.scheduled_at)
    const hour = dt.getHours()
    const minutes = dt.getMinutes()
    // Группируем по часам (уроки в :00 и :30 попадают в один слот для отображения)
    const key = `${toISO(dt)}-${hour}`
    if (!map[key]) map[key] = []
    map[key].push(L)
  }
  
  console.log('[ScheduleView] lessonsBySlot map created, total slots:', Object.keys(map).length)
  return map
})

// Вычисляем позиции уроков с учетом минут для точного позиционирования
const lessonsWithPositions = computed(() => {
  if (!calendarBodyWidth.value || !weekDays.value.length) return []
  
  const result = []
  const startHour = timeSlots[0]
  const dayWidth = (calendarBodyWidth.value - timeColWidth) / 7
  
  for (const lesson of props.lessons) {
    if (!lesson.id || !lesson.scheduled_at) continue
    
    const dt = new Date(lesson.scheduled_at)
    const lessonIso = toISO(dt)
    
    // Находим индекс дня недели
    const dayIndex = weekDays.value.findIndex(day => day.iso === lessonIso)
    if (dayIndex < 0) continue // Урок вне текущей недели
    
    // Вычисляем позицию по вертикали (учитываем часы и минуты)
    const lessonHour = dt.getHours()
    const lessonMinutes = dt.getMinutes()
    const totalMinutes = lessonHour * 60 + lessonMinutes
    const minutesFromStart = totalMinutes - startHour * 60
    const top = (minutesFromStart / 60) * slotHeight
    
    // Вычисляем позицию по горизонтали
    const left = timeColWidth + dayWidth * dayIndex
    const width = dayWidth * 0.8 // Занимаем 80% ширины колонки дня
    
    // Высота карточки = 1 час
    const height = slotHeight
    
    result.push({
      lesson,
      style: {
        top: `${top}px`,
        left: `${left}px`,
        width: `${width}px`,
        height: `${height}px`
      }
    })
  }
  
  return result
})

const formatHour = (h) => `${String(h).padStart(2, '0')}:00`

const formatLessonTime = (scheduledAt) => {
  if (!scheduledAt) return ''
  const dt = new Date(scheduledAt)
  const startHour = dt.getHours()
  const startMin = dt.getMinutes()
  const endHour = (startHour + 1) % 24
  const startStr = `${String(startHour).padStart(2, '0')}:${String(startMin).padStart(2, '0')}`
  const endStr = `${String(endHour).padStart(2, '0')}:${String(startMin).padStart(2, '0')}`
  return `${startStr} - ${endStr}`
}

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
const formStudentEmail = ref('')
const formTeacherEmail = ref('')
const formLink = ref('Discord')
const formComment = ref('')
const formIsTrial = ref(false)
const formCourseId = ref(null) // '' или id курса

const coursesList = ref([])

const foundStudent = ref(null)
const foundTeacher = ref(null)
const searchingStudent = ref(false)
const searchingTeacher = ref(false)
const studentError = ref('')
const teacherError = ref('')

// Автодополнение
const studentAutocompleteList = ref([])
const teacherAutocompleteList = ref([])
const autocompleteLoading = ref(false)
let studentAutocompleteTimeout = null
let teacherAutocompleteTimeout = null

const createLoading = ref(false)
const createError = ref('')

const handleSlotClick = (event, iso, hour) => {
  // Определяем, в какую половину ячейки кликнули (верхняя = :00, нижняя = :30)
  const rect = event.currentTarget.getBoundingClientRect()
  const clickY = event.clientY - rect.top
  const slotHeight = rect.height
  const minutes = clickY < slotHeight / 2 ? 0 : 30
  
  openCreate(iso, hour, minutes)
}

const openCreate = async (iso, hour, minutes = 0) => {
  formDate.value = iso
  formTime.value = `${String(hour).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
  formStudentEmail.value = ''
  formTeacherEmail.value = ''
  formLink.value = 'Discord'
  formComment.value = ''
  formIsTrial.value = false
  formCourseId.value = ''
  foundStudent.value = null
  foundTeacher.value = null
  studentError.value = ''
  teacherError.value = ''
  createError.value = ''
  showCreateModal.value = true
  
  // Загружаем список курсов при первом открытии
  if (props.onGetCourses && coursesList.value.length === 0) {
    try {
      const { data } = await props.onGetCourses()
      coursesList.value = Array.isArray(data) ? data : data.results || []
    } catch (_) {
      coursesList.value = []
    }
  }
  
  // Загружаем начальные списки для автодополнения
  if (props.onGetAutocomplete) {
    loadStudentAutocomplete('')
    if (canSelectTeacher.value) {
      loadTeacherAutocomplete('')
    }
  }
}

const closeCreate = () => {
  showCreateModal.value = false
}

const searchStudent = async () => {
  if (!formStudentEmail.value || !props.onSearchUser) return
  
  searchingStudent.value = true
  studentError.value = ''
  foundStudent.value = null

  try {
    const result = await props.onSearchUser(formStudentEmail.value, 'student')
    if (result && result.is_my_student !== false) {
      foundStudent.value = result
      // Подставляем курс по умолчанию из последнего занятия ученика
      if (props.onGetLastLessonForStudent && result.id) {
        try {
          const lastLesson = await props.onGetLastLessonForStudent(result.id)
          if (lastLesson?.course_id) {
            formCourseId.value = lastLesson.course_id
          }
        } catch (_) {
          // Игнорируем ошибку — курс останется пустым
        }
      }
    } else {
      studentError.value = 'Этот ученик не назначен вам. Обратитесь к менеджеру.'
    }
  } catch (err) {
    // Не логируем 404 как ошибку - это нормально, когда пользователь не найден
    if (err?.response?.status === 404) {
      studentError.value = 'Ученик не найден'
    } else {
      console.error('search student error:', err)
      const errorDetail = err?.response?.data?.detail
      if (errorDetail === 'this student is not assigned to you') {
        studentError.value = 'Этот ученик не назначен вам. Обратитесь к менеджеру.'
      } else {
        studentError.value = errorDetail || 'Ошибка поиска ученика'
      }
    }
  } finally {
    searchingStudent.value = false
  }
}

const searchTeacher = async () => {
  if (!formTeacherEmail.value || !props.onSearchUser) return
  
  searchingTeacher.value = true
  teacherError.value = ''
  foundTeacher.value = null

  try {
    const result = await props.onSearchUser(formTeacherEmail.value, 'teacher')
    foundTeacher.value = result
  } catch (err) {
    // Не логируем 404 как ошибку - это нормально, когда пользователь не найден
    if (err?.response?.status === 404) {
      teacherError.value = 'Учитель не найден'
    } else {
      console.error('search teacher error:', err)
      teacherError.value = err?.response?.data?.detail || 'Ошибка поиска учителя'
    }
  } finally {
    searchingTeacher.value = false
  }
}

const validateStudentEmail = () => {
  if (formStudentEmail.value && props.onSearchUser) {
    searchStudent()
  }
}

const validateTeacherEmail = () => {
  if (formTeacherEmail.value && props.onSearchUser) {
    searchTeacher()
  }
}

const clearStudentError = () => {
  studentError.value = ''
  foundStudent.value = null
}

const clearTeacherError = () => {
  teacherError.value = ''
  foundTeacher.value = null
}

// Загрузка списков для автодополнения
const loadStudentAutocomplete = async (search = '') => {
  if (!props.onGetAutocomplete) return
  
  try {
    autocompleteLoading.value = true
    const result = await props.onGetAutocomplete('student', search)
    studentAutocompleteList.value = Array.isArray(result) ? result : result.data || []
  } catch (err) {
    console.error('load student autocomplete error:', err)
    studentAutocompleteList.value = []
  } finally {
    autocompleteLoading.value = false
  }
}

const loadTeacherAutocomplete = async (search = '') => {
  if (!props.onGetAutocomplete || !canSelectTeacher.value) return
  
  try {
    autocompleteLoading.value = true
    const result = await props.onGetAutocomplete('teacher', search)
    teacherAutocompleteList.value = Array.isArray(result) ? result : result.data || []
  } catch (err) {
    console.error('load teacher autocomplete error:', err)
    teacherAutocompleteList.value = []
  } finally {
    autocompleteLoading.value = false
  }
}

// Обработка ввода для автодополнения (с debounce)
const handleStudentEmailInput = (event) => {
  const value = event.target.value.trim()
  clearStudentError()
  
  // Очищаем предыдущий таймер
  if (studentAutocompleteTimeout) {
    clearTimeout(studentAutocompleteTimeout)
  }
  
  // Загружаем подсказки при вводе (с задержкой 300ms)
  if (value.length >= 2) {
    studentAutocompleteTimeout = setTimeout(() => {
      loadStudentAutocomplete(value)
    }, 300)
  } else {
    studentAutocompleteList.value = []
  }
}

const handleTeacherEmailInput = (event) => {
  const value = event.target.value.trim()
  clearTeacherError()
  
  // Очищаем предыдущий таймер
  if (teacherAutocompleteTimeout) {
    clearTimeout(teacherAutocompleteTimeout)
  }
  
  // Загружаем подсказки при вводе (с задержкой 300ms)
  if (value.length >= 2) {
    teacherAutocompleteTimeout = setTimeout(() => {
      loadTeacherAutocomplete(value)
    }, 300)
  } else {
    teacherAutocompleteList.value = []
  }
}

const canCreateLesson = computed(() => {
  if (canSelectTeacher.value) {
    return foundStudent.value && foundTeacher.value
  } else if (isTeacher.value) {
    // Для учителя дополнительно проверяем, что ученик не абитуриент и имеет баланс
    if (!foundStudent.value) return false
    if (foundStudent.value.role === 'APPLICANT') return false
    const balance = foundStudent.value.lessons_available || 0
    if (balance === 0) return false
    return true
  }
  return false
})

const handleCreate = async () => {
  createError.value = ''

  // Проверяем, что найдены необходимые пользователи
  if (!foundStudent.value) {
    createError.value = 'Сначала найдите ученика по email и нажмите кнопку "Найти"'
    return
  }

  if (canSelectTeacher.value && !foundTeacher.value) {
    createError.value = 'Сначала найдите учителя по email и нажмите кнопку "Найти"'
    return
  }

  // Проверяем, что email'ы не пустые
  if (!formStudentEmail.value?.trim()) {
    createError.value = 'Введите email ученика'
    return
  }

  if (canSelectTeacher.value && !formTeacherEmail.value?.trim()) {
    createError.value = 'Введите email учителя'
    return
  }

  // Валидация для учителя: нельзя создать урок для ученика с нулевым балансом или абитуриента
  if (isTeacher.value && foundStudent.value) {
    // Проверяем роль ученика
    if (foundStudent.value.role === 'APPLICANT') {
      createError.value = 'Нельзя создать урок для абитуриента. Обратитесь к менеджеру.'
      return
    }
    
    // Проверяем баланс
    const balance = foundStudent.value.lessons_available || 0
    if (balance === 0) {
      createError.value = 'Нельзя создать урок для ученика с нулевым балансом. Обратитесь к менеджеру.'
      return
    }
  }

  // Формируем правильный формат даты и времени (ISO 8601 с секундами и часовым поясом)
  // formTime может быть в формате "HH:MM" или "HH:MM:SS", добавляем секунды если нужно
  let timeStr = formTime.value
  if (timeStr && timeStr.split(':').length === 2) {
    timeStr = `${timeStr}:00` // Добавляем секунды если их нет
  }
  
  // Создаем объект Date с локальной датой и временем
  const localDateTime = new Date(`${formDate.value}T${timeStr}`)
  
  // Получаем смещение часового пояса в формате +HH:MM или -HH:MM
  const timezoneOffset = -localDateTime.getTimezoneOffset()
  const offsetHours = Math.floor(Math.abs(timezoneOffset) / 60)
  const offsetMinutes = Math.abs(timezoneOffset) % 60
  const offsetSign = timezoneOffset >= 0 ? '+' : '-'
  const offsetStr = `${offsetSign}${String(offsetHours).padStart(2, '0')}:${String(offsetMinutes).padStart(2, '0')}`
  
  // Формируем ISO строку с часовым поясом
  const isoString = `${formDate.value}T${timeStr}${offsetStr}`
  
  const payload = {
    student_email: formStudentEmail.value.trim(),
    scheduled_at: isoString,
  }

  // Добавляем comment только если он не пустой (не отправляем пустую строку)
  if (formComment.value?.trim()) {
    payload.comment = formComment.value.trim()
  }

  // Ссылка обязательна; пустое значение — Discord по умолчанию
  payload.link = formLink.value?.trim() || 'Discord'

  // Для менеджера и админа добавляем teacher_email
  if (canSelectTeacher.value) {
    payload.teacher_email = formTeacherEmail.value.trim()
  }

  // Для менеджера и админа добавляем is_trial
  if (canCreateTrial.value && formIsTrial.value) {
    payload.is_trial = true
  }

  // Курс (становится курсом по умолчанию для ученика)
  if (formCourseId.value && formCourseId.value !== '') {
    payload.course = Number(formCourseId.value)
  }

  console.log('Creating lesson with payload:', payload)

  createLoading.value = true

  try {
    await props.onCreateLesson(payload)
    showCreateModal.value = false
    // Очищаем форму после успешного создания
    formStudentEmail.value = ''
    formTeacherEmail.value = ''
    formLink.value = 'Discord'
    formComment.value = ''
    formIsTrial.value = false
    foundStudent.value = null
    foundTeacher.value = null
  } catch (err) {
    console.error('create lesson error:', err)
    console.error('Error response data:', err?.response?.data)
    console.error('Payload that was sent:', payload)
    const errorData = err?.response?.data
    if (errorData) {
      // Приоритет обработки ошибок: сначала специфичные поля, потом общие
      if (errorData.student_email) {
        const errorMsg = Array.isArray(errorData.student_email) ? errorData.student_email[0] : errorData.student_email
        createError.value = `Ошибка с учеником: ${errorMsg}`
      } else if (errorData.teacher_email) {
        const errorMsg = Array.isArray(errorData.teacher_email) ? errorData.teacher_email[0] : errorData.teacher_email
        createError.value = `Ошибка с учителем: ${errorMsg}`
      } else if (errorData.student) {
        const errorMsg = Array.isArray(errorData.student) ? errorData.student[0] : errorData.student
        // Если ошибка "Either student or student_email is required", показываем более понятное сообщение
        if (errorMsg.includes('student_email is required') || errorMsg.includes('Either student')) {
          createError.value = 'Укажите email ученика и нажмите "Найти"'
        } else {
          createError.value = `Ошибка с учеником: ${errorMsg}`
        }
      } else if (errorData.teacher) {
        const errorMsg = Array.isArray(errorData.teacher) ? errorData.teacher[0] : errorData.teacher
        // Если ошибка "Either teacher or teacher_email is required", показываем более понятное сообщение
        if (errorMsg.includes('teacher_email is required') || errorMsg.includes('Either teacher')) {
          createError.value = 'Укажите email учителя и нажмите "Найти"'
        } else {
          createError.value = `Ошибка с учителем: ${errorMsg}`
        }
      } else if (errorData.scheduled_at) {
        const errorMsg = Array.isArray(errorData.scheduled_at) ? errorData.scheduled_at[0] : errorData.scheduled_at
        createError.value = `Ошибка с датой/временем: ${errorMsg}`
      } else if (errorData.detail) {
        createError.value = errorData.detail
      } else {
        // Показываем первую ошибку из объекта
        const firstErrorKey = Object.keys(errorData)[0]
        const firstError = errorData[firstErrorKey]
        const errorMsg = Array.isArray(firstError) ? firstError[0] : firstError
        createError.value = `${firstErrorKey}: ${errorMsg}`
      }
    } else {
      createError.value = 'Ошибка создания урока. Проверьте подключение к серверу.'
    }
  }

  createLoading.value = false
}

const selectLesson = (lesson) => {
  console.log('Selecting lesson:', lesson, 'ID:', lesson?.id)
  activeLesson.value = lesson
  emit('lesson-selected', lesson)
  // Сразу открываем форму редактирования
  if (canEditLesson.value) {
    openEditLesson()
  }
}

// =====================================
// РЕДАКТИРОВАНИЕ УРОКА
// =====================================

const showEditModal = ref(false)

const editForm = ref({
  status: '',
  date: '',
  time: '',
  link: '',
  comment: '',
  cancellation_reason: '',
  feedback: '',
    course_id: '' // '' или id курса
})

const updateLoading = ref(false)
const updateError = ref(null)

const openEditLesson = () => {
  if (!activeLesson.value) return
  
  const lesson = activeLesson.value
  console.log('[openEditLesson] Открываем урок для редактирования:', lesson)
  console.log('[openEditLesson] ID урока:', lesson.id)
  console.log('[openEditLesson] feedback:', lesson.feedback)
  console.log('[openEditLesson] cancellation_reason:', lesson.cancellation_reason)
  
  const scheduledDate = new Date(lesson.scheduled_at)
  
  editForm.value = {
    status: lesson.status,
    date: toISO(scheduledDate),
    time: `${String(scheduledDate.getHours()).padStart(2, '0')}:${String(scheduledDate.getMinutes()).padStart(2, '0')}`,
    link: lesson.link?.trim() || 'Discord',
    comment: lesson.comment || '',
    cancellation_reason: lesson.cancellation_reason || '',
    feedback: lesson.feedback || '',
    course_id: lesson.course_id ?? ''
  }
  
  console.log('[openEditLesson] Форма редактирования:', editForm.value)
  updateError.value = null
  showEditModal.value = true
}

const closeEdit = () => {
  showEditModal.value = false
  activeLesson.value = null
}

const handleUpdate = async () => {
  if (!activeLesson.value || !props.onUpdateLesson) return

  updateLoading.value = true
  updateError.value = null

  // Валидация на фронтенде
  if (editForm.value.status === 'CANCELLED' && !editForm.value.cancellation_reason?.trim()) {
    updateError.value = 'Причина отмены обязательна при отмене занятия'
    updateLoading.value = false
    return
  }

  if (editForm.value.status === 'DONE' && !editForm.value.feedback?.trim()) {
    updateError.value = 'Обратная связь обязательна при завершении занятия'
    updateLoading.value = false
    return
  }

  try {
    const payload = {
      status: editForm.value.status,
      link: editForm.value.link?.trim() || 'Discord',
      comment: editForm.value.comment || '',
    }

    // Курс (при смене станет курсом по умолчанию для ученика)
    if ('course_id' in editForm.value) {
      payload.course = (editForm.value.course_id && editForm.value.course_id !== '')
        ? Number(editForm.value.course_id)
        : null
    }

    // Всегда передаем cancellation_reason и feedback, если они есть в форме
    // Это позволяет обновлять их значения независимо от статуса
    // Важно: передаем даже пустые строки, чтобы можно было очистить поля
    if ('cancellation_reason' in editForm.value) {
      payload.cancellation_reason = editForm.value.cancellation_reason || ''
    }
    
    if ('feedback' in editForm.value) {
      payload.feedback = editForm.value.feedback || ''
    }

    if (canEditTime.value && editForm.value.date && editForm.value.time) {
      // Формируем правильный формат даты и времени (ISO 8601 с секундами и часовым поясом)
      let timeStr = editForm.value.time
      if (timeStr && timeStr.split(':').length === 2) {
        timeStr = `${timeStr}:00` // Добавляем секунды если их нет
      }
      
      // Создаем объект Date с локальной датой и временем
      const localDateTime = new Date(`${editForm.value.date}T${timeStr}`)
      
      // Получаем смещение часового пояса в формате +HH:MM или -HH:MM
      const timezoneOffset = -localDateTime.getTimezoneOffset()
      const offsetHours = Math.floor(Math.abs(timezoneOffset) / 60)
      const offsetMinutes = Math.abs(timezoneOffset) % 60
      const offsetSign = timezoneOffset >= 0 ? '+' : '-'
      const offsetStr = `${offsetSign}${String(offsetHours).padStart(2, '0')}:${String(offsetMinutes).padStart(2, '0')}`
      
      // Формируем ISO строку с часовым поясом
      payload.scheduled_at = `${editForm.value.date}T${timeStr}${offsetStr}`
    }

    // Проверяем что у урока есть ID
    if (!activeLesson.value.id) {
      console.error('Ошибка: у активного урока отсутствует ID', activeLesson.value)
      updateError.value = 'Ошибка: не удалось определить ID урока'
      updateLoading.value = false
      return
    }

    console.log('Updating lesson ID:', activeLesson.value.id, 'with payload:', payload)
    const updatedLesson = await props.onUpdateLesson(activeLesson.value.id, payload)
    
    console.log('[handleUpdate] Получен обновлённый урок:', updatedLesson)
    console.log('[handleUpdate] ID обновлённого урока:', updatedLesson?.id)
    console.log('[handleUpdate] feedback в обновлённом уроке:', updatedLesson?.feedback)
    console.log('[handleUpdate] cancellation_reason в обновлённом уроке:', updatedLesson?.cancellation_reason)
    
    // Обновляем activeLesson с новыми данными
    if (updatedLesson) {
      // Дополнительная проверка ID
      if (!updatedLesson.id) {
        console.error('[handleUpdate] КРИТИЧЕСКАЯ ОШИБКА: обновлённый урок не содержит ID!', updatedLesson)
        updateError.value = 'Ошибка: сервер вернул урок без ID'
        updateLoading.value = false
        return
      }
      
      activeLesson.value = updatedLesson
      console.log('[handleUpdate] activeLesson обновлён, новые данные:', activeLesson.value)
    } else {
      // Если обновленный урок не возвращен, обновляем из списка уроков
      const lessonId = activeLesson.value.id
      const refreshedLesson = props.lessons.find(l => l.id === lessonId)
      if (refreshedLesson) {
        activeLesson.value = refreshedLesson
        console.log('[handleUpdate] activeLesson обновлён из списка уроков:', activeLesson.value)
      } else {
        console.warn('[handleUpdate] Не удалось найти обновлённый урок в списке')
      }
    }
    
    showEditModal.value = false
    activeLesson.value = null
  } catch (err) {
    console.error('update lesson error:', err)
    console.error('error response:', err?.response?.data)
    const errorData = err?.response?.data
    if (errorData) {
      // Обрабатываем ошибки валидации
      if (errorData.cancellation_reason) {
        updateError.value = Array.isArray(errorData.cancellation_reason) 
          ? errorData.cancellation_reason[0] 
          : errorData.cancellation_reason
      } else if (errorData.feedback) {
        updateError.value = Array.isArray(errorData.feedback) 
          ? errorData.feedback[0] 
          : errorData.feedback
      } else if (errorData.detail) {
        updateError.value = errorData.detail
      } else {
        // Показываем первую ошибку из объекта или общее сообщение
        const errorKeys = Object.keys(errorData)
        if (errorKeys.length > 0) {
          const firstError = errorData[errorKeys[0]]
          updateError.value = `${errorKeys[0]}: ${Array.isArray(firstError) ? firstError[0] : firstError}`
        } else {
          updateError.value = 'Ошибка обновления урока'
        }
      }
    } else {
      updateError.value = 'Ошибка обновления урока'
    }
  } finally {
    updateLoading.value = false
  }
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

// Экспортируем функции для внешнего использования
defineExpose({
  weekStart,
  weekEnd: computed(() => addDays(weekStart.value, 6)),
  shiftWeek,
  goToday
})
</script>

<style scoped>
.schedule-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 100%;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  overflow-x: hidden;
  min-height: 100%;
}

.admin-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.calendar-wrapper {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.calendar-wrapper .status-text,
.calendar-wrapper .error {
  padding: 12px 16px;
  margin-top: 12px;
}

.controls-card {
  background: rgba(40, 40, 40, 0.8);
  border: none;
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}


.controls-row {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  align-items: center;
  margin: 0;
}

.controls-row button {
  margin-right: 0;
  padding: 8px 16px;
  background: transparent;
  border: 2px solid #FFD700;
  border-radius: 8px;
  cursor: pointer;
  color: #FFD700;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.controls-row button:hover {
  background: #FFD700;
  color: #1A1A1A;
}

.week-label {
  margin: 6px 0;
  color: #FFFFFF;
  font-size: 1rem;
  font-weight: 700;
}

.hint {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-top: 4px;
  font-weight: 500;
}

.calendar {
  --slot-height: 42px;
  --calendar-scrollbar: 12px;
  border: none;
  border-radius: 12px;
  overflow: hidden;
  font-size: 13px;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  background: rgba(40, 40, 40, 0.8);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 180px);
  min-height: 600px;
  max-height: calc(100vh - 180px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.calendar-header-row {
  display: grid;
  grid-template-columns: 45px repeat(7, 1fr);
  width: 100%;
  flex-shrink: 0;
  box-sizing: border-box;
  padding-right: var(--calendar-scrollbar);
}

.calendar-row {
  display: grid;
  grid-template-columns: 45px repeat(7, 1fr);
  width: 100%;
  box-sizing: border-box;
}

.time-col {
  background: rgba(50, 50, 50, 0.9);
  text-align: right;
  padding-right: 8px;
  padding-left: 6px;
  color: #FFFFFF;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: var(--slot-height);
  font-weight: 700;
  border-right: 2px solid rgba(255, 215, 0, 0.3);
  box-sizing: border-box;
}

.day-col {
  background: rgba(50, 50, 50, 0.9);
  text-align: center;
  border-right: 2px solid rgba(255, 215, 0, 0.3);
  padding: 10px 4px;
  min-width: 0;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
}

.day-name {
  font-weight: 700;
  color: rgba(255, 255, 255, 0.8);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1.2;
  margin-bottom: 2px;
}

.day-date {
  font-size: 18px;
  color: #FFFFFF;
  margin-top: 0;
  font-weight: 800;
  line-height: 1.2;
}

.calendar-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  background: rgba(35, 35, 35, 0.8);
  position: relative;
  box-sizing: border-box;
  /* Резервируем место под скроллбар для точного выравнивания колонок */
  scrollbar-gutter: stable;
}

.calendar-body::-webkit-scrollbar {
  width: 12px;
}

.calendar-body::-webkit-scrollbar-track {
  background: rgba(50, 50, 50, 0.6);
  border-radius: 6px;
  border: 1px solid rgba(255, 215, 0, 0.2);
}

.calendar-body::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.5);
  border-radius: 6px;
  border: 2px solid rgba(50, 50, 50, 0.5);
}

.calendar-body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.7);
}


.calendar-row {
  height: var(--slot-height);
}

.slot {
  position: relative;
  height: var(--slot-height);
  border-right: 2px solid rgba(255, 215, 0, 0.3);
  border-bottom: 2px solid rgba(255, 215, 0, 0.2);
  padding: 1px;
  display: flex;
  flex-direction: row;
  align-items: stretch;
  gap: 2px;
  overflow: hidden;
  box-sizing: border-box;
  background: rgba(45, 45, 45, 0.6);
  z-index: 1;
}

.current-time-indicator {
  position: absolute;
  height: 2px;
  background: #FFD700;
  z-index: 6;
  pointer-events: none;
  box-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
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
  box-shadow: 0 0 8px rgba(255, 215, 0, 0.8);
}

.slot::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 1px;
  background: rgba(255, 215, 0, 0.1);
  pointer-events: none;
  z-index: 1;
}

.slot-lessons-container {
  flex: 0 0 80%;
  max-width: 80%;
  display: flex;
  flex-direction: row;
  gap: 2px;
  overflow: hidden;
  align-items: stretch;
  min-width: 0;
  height: 100%;
  align-content: stretch;
  position: relative;
  z-index: 2;
}

.slot-lessons-container--scrollable {
  overflow-x: auto;
  overflow-y: hidden;
}

.slot-lessons-container--scrollable::-webkit-scrollbar {
  height: 4px;
}

.slot-lessons-container--scrollable::-webkit-scrollbar-track {
  background: rgba(50, 50, 50, 0.3);
  border-radius: 2px;
}

.slot-lessons-container--scrollable::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.5);
  border-radius: 2px;
}

.slot-lessons-container--scrollable::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.7);
}

.slot:hover {
  background: rgba(60, 60, 60, 0.8);
  z-index: 2;
}

.slot-empty-area {
  flex: 0 0 20%;
  min-width: 30px;
  height: 100%;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-radius: 4px;
  align-self: stretch;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed rgba(255, 215, 0, 0.4);
  background: rgba(50, 50, 50, 0.5);
  z-index: 1;
  box-sizing: border-box;
}

.slot-empty-area:hover {
  background-color: rgba(70, 70, 70, 0.8);
  border-color: rgba(255, 215, 0, 0.6);
  z-index: 3;
}

.slot-empty-area::before {
  content: '+';
  font-size: 20px;
  color: rgba(255, 215, 0, 0.6);
  font-weight: 400;
  line-height: 1;
}

.slot-empty-area:hover::before {
  color: #FFD700;
}

.lesson-card {
  color: #ffffff;
  border-radius: 4px;
  padding: 3px 5px;
  margin: 0;
  font-size: 12px;
  cursor: pointer;
  transition: box-shadow 0.2s ease;
  flex: 1 1 0;
  min-width: 0;
  height: 100%;
  min-height: 100%;
  max-height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  border-left: 3px solid transparent;
  align-self: stretch;
  position: relative;
  z-index: 2;
  isolation: isolate;
  box-sizing: border-box;
}

/* При ≤5 уроках: карточки адаптивно уменьшаются, занимая всю доступную ширину */
.slot-lessons-container:not(.slot-lessons-container--scrollable) .lesson-card {
  flex: 1 1 0;
  min-width: 0;
}

/* При >5 уроках: карточки фиксируются на размере, который был при 5 уроках */
/* calc((100% - 8px) / 5) = ширина одной карточки при 5 уроках (100% контейнера минус 4 промежутка по 2px) */
.slot-lessons-container--scrollable .lesson-card {
  flex: 0 0 calc((100% - 8px) / 5);
  width: calc((100% - 8px) / 5);
  min-width: calc((100% - 8px) / 5);
  max-width: calc((100% - 8px) / 5);
  flex-shrink: 0;
}

.lesson-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
  z-index: 5;
}

/* Запланировано - синий */
.lesson-card--planned {
  background: #3b82f6;
  border-left-color: #2563eb;
}

/* Проведено - зеленый */
.lesson-card--done {
  background: #22c55e;
  border-left-color: #16a34a;
}

/* Отменено - красный */
.lesson-card--cancelled {
  background: #ef4444;
  border-left-color: #dc2626;
}

/* Пробное занятие - ярче и с градиентом */
.lesson-card--trial {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border-left-color: #ea580c;
  box-shadow: 0 2px 12px rgba(245, 158, 11, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.lesson-card--trial:hover {
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* Комбинации пробного занятия со статусами */
.lesson-card--trial.lesson-card--planned {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #f59e0b 100%);
  border-left-color: #2563eb;
}

.lesson-card--trial.lesson-card--done {
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 50%, #f59e0b 100%);
  border-left-color: #16a34a;
}

.lesson-card--trial.lesson-card--cancelled {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 50%, #f59e0b 100%);
  border-left-color: #dc2626;
}

.lesson-trial-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(255, 255, 255, 0.95);
  color: #f59e0b;
  font-size: 9px;
  font-weight: 700;
  padding: 2px 4px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

/* Стили для абсолютно позиционированных карточек уроков */
.lesson-card-positioned {
  position: absolute;
  color: #ffffff;
  border-radius: 4px;
  padding: 3px 5px;
  margin: 0;
  font-size: 12px;
  cursor: pointer;
  transition: box-shadow 0.2s ease, z-index 0s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  border-left: 3px solid transparent;
  z-index: 3;
  isolation: isolate;
  box-sizing: border-box;
}

.lesson-card-positioned:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
  z-index: 100 !important;
}

/* Применяем стили статусов к позиционированным карточкам */
.lesson-card-positioned.lesson-card--planned {
  background: #3b82f6;
  border-left-color: #2563eb;
}

.lesson-card-positioned.lesson-card--done {
  background: #22c55e;
  border-left-color: #16a34a;
}

.lesson-card-positioned.lesson-card--cancelled {
  background: #ef4444;
  border-left-color: #dc2626;
}

.lesson-card-positioned.lesson-card--trial {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border-left-color: #ea580c;
  box-shadow: 0 2px 12px rgba(245, 158, 11, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.lesson-card-positioned.lesson-card--trial:hover {
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.lesson-card-positioned.lesson-card--trial.lesson-card--planned {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #f59e0b 100%);
  border-left-color: #2563eb;
}

.lesson-card-positioned.lesson-card--trial.lesson-card--done {
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 50%, #f59e0b 100%);
  border-left-color: #16a34a;
}

.lesson-card-positioned.lesson-card--trial.lesson-card--cancelled {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 50%, #f59e0b 100%);
  border-left-color: #dc2626;
}


.lesson-time {
  font-weight: 700;
  font-size: 11px;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 3px;
  color: #ffffff;
}

.lesson-student {
  font-size: 13px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #ffffff;
  font-weight: 600;
}

.lesson-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 2px solid #FFD700;
  cursor: pointer;
  background: #FFD700;
  color: #1A1A1A;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.btn.small {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.btn:hover:not(:disabled) {
  background: #FF8C00;
  border-color: #FF8C00;
  color: #FFFFFF;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
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
  width: 500px;
  background: rgba(40, 40, 40, 0.95);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  color: #FFFFFF;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.3rem;
  font-weight: 800;
  color: #FFFFFF;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.field span {
  margin-bottom: 6px;
  color: #FFFFFF;
  font-size: 0.9rem;
  font-weight: 600;
}

.email-input-wrapper {
  display: flex;
  gap: 8px;
}

.email-input-wrapper input {
  flex: 1;
}

.btn-search {
  padding: 8px 12px;
  background: #FFD700;
  color: #1A1A1A;
  border: 2px solid #FFD700;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.btn-search:hover:not(:disabled) {
  background: #FF8C00;
  border-color: #FF8C00;
  color: #FFFFFF;
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.found-user {
  color: #22c55e;
  font-size: 0.85rem;
  margin-top: 4px;
  font-weight: 600;
}

.error-text {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 4px;
  font-weight: 600;
}

.field input,
.field select,
.field textarea {
  background: rgba(50, 50, 50, 0.8);
  border: 2px solid rgba(255, 215, 0, 0.3);
  color: #FFFFFF;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.field input::placeholder,
.field textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.field textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.field-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.field--half {
  flex: 1;
  margin-bottom: 0;
}

.field--required span {
  color: #e8eaf6;
}

.required-mark {
  color: rgba(255, 107, 107, 0.9);
  margin-left: 2px;
  font-weight: 700;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(60, 60, 60, 0.9);
}

.field input:disabled,
.field select:disabled,
.field textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(30, 35, 50, 0.5);
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.modal-actions button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.modal-actions button[type="submit"],
.modal-actions .btn {
  background: #FFD700;
  color: #1A1A1A;
  border: 2px solid #FFD700;
}

.modal-actions button[type="submit"]:hover:not(:disabled),
.modal-actions .btn:hover:not(:disabled) {
  background: #FF8C00;
  border-color: #FF8C00;
  color: #FFFFFF;
}

.modal-actions .btn-secondary {
  background: transparent;
  color: #FFD700;
  border: 2px solid #FFD700;
}

.modal-actions .btn-secondary:hover {
  background: #FFD700;
  color: #1A1A1A;
}

.modal-actions button[type="submit"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-actions button[type="button"]:not(.btn-secondary) {
  background: transparent;
  color: #FFD700;
  border: 2px solid #FFD700;
}

.modal-actions button[type="button"]:not(.btn-secondary):hover {
  background: #FFD700;
  color: #1A1A1A;
}

.error {
  color: #ffffff;
  margin-top: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  background: rgba(220, 38, 38, 0.95);
  border: 2px solid rgba(220, 38, 38, 1);
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
}

.status-text {
  color: #FFFFFF;
  margin-top: 12px;
  font-size: 0.95rem;
  font-weight: 600;
}


.balance-zero {
  color: #ffffff;
  font-weight: 700;
  background: #ef4444;
  padding: 6px 12px;
  border-radius: 8px;
  border: 2px solid #dc2626;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
}

.balance-positive {
  color: #ffffff;
  font-weight: 700;
  background: #22c55e;
  padding: 6px 12px;
  border-radius: 8px;
  border: 2px solid #16a34a;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4);
}

.trial-badge {
  background: rgba(251, 191, 36, 0.95);
  padding: 8px 14px;
  border-radius: 8px;
  border: 2px solid rgba(251, 191, 36, 1);
  margin: 12px 0;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

.trial-badge strong {
  color: #1a1a1a;
  font-weight: 800;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  margin-left: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Запланировано - синий */
.status-badge--planned {
  background: #3b82f6;
  color: #ffffff;
  border: 1px solid #2563eb;
}

/* Проведено - зеленый */
.status-badge--done {
  background: #22c55e;
  color: #ffffff;
  border: 1px solid #16a34a;
}

/* Отменено - красный */
.status-badge--cancelled {
  background: #ef4444;
  color: #ffffff;
  border: 1px solid #dc2626;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .schedule-view {
    gap: 16px;
  }

  .calendar {
    height: auto;
    min-height: 500px;
    max-height: 70vh;
  }
}

@media (max-width: 768px) {
  .schedule-view {
    padding: 0;
    gap: 12px;
  }

  .admin-card {
    padding: 16px;
    border-radius: 12px;
  }

  .controls-card {
    padding: 8px 12px;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .controls-row {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .controls-row button {
    flex: 1;
    min-width: 100px;
    font-size: 0.7rem;
    padding: 6px 8px;
  }

  .week-label {
    font-size: 0.85rem;
  }

  .hint {
    font-size: 0.75rem;
  }

  .calendar {
    min-height: 400px;
    max-height: 60vh;
  }

  .calendar {
    font-size: 11px;
  }

  .calendar-header-row,
  .calendar-row {
    grid-template-columns: 35px repeat(7, minmax(60px, 1fr));
  }

  .time-col {
    font-size: 9px;
    padding-right: 4px;
    padding-left: 2px;
    height: 36px;
  }

  .day-col {
    padding: 6px 2px;
  }

  .day-name {
    font-size: 9px;
  }

  .day-date {
    font-size: 14px;
  }

  .calendar-row {
    height: 36px;
  }

  .slot {
    height: 36px;
  }

  .lesson-card {
    font-size: 10px;
    padding: 2px 4px;
  }

  .lesson-time {
    font-size: 9px;
  }

  .lesson-student {
    font-size: 11px;
  }


  .modal {
    width: 90%;
    max-width: 500px;
    padding: 20px;
    max-height: 85vh;
  }

  .modal h2 {
    font-size: 1.2rem;
  }

  .field {
    margin-bottom: 12px;
  }

  .field span {
    font-size: 0.85rem;
  }

  .email-input-wrapper {
    flex-direction: column;
    gap: 8px;
  }

  .btn-search {
    width: 100%;
  }

  .field-row {
    flex-direction: column;
    gap: 12px;
  }

  .field--half {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .schedule-view {
    gap: 8px;
  }

  .admin-card {
    padding: 12px;
  }

  .controls-card {
    padding: 6px 10px;
  }

  .controls-row button {
    font-size: 0.65rem;
    padding: 5px 6px;
    min-width: 80px;
  }

  .calendar {
    min-height: 350px;
    max-height: 55vh;
  }

  .calendar-header-row,
  .calendar-row {
    grid-template-columns: 30px repeat(7, minmax(50px, 1fr));
  }

  .time-col {
    font-size: 8px;
    height: 32px;
  }

  .day-col {
    padding: 4px 1px;
  }

  .day-name {
    font-size: 8px;
  }

  .day-date {
    font-size: 12px;
  }

  .calendar-row {
    height: 32px;
  }

  .slot {
    height: 32px;
  }

  .lesson-card {
    font-size: 9px;
    padding: 1px 3px;
  }

  .lesson-time {
    font-size: 8px;
  }

  .lesson-student {
    font-size: 10px;
  }

  .modal {
    width: 95%;
    padding: 16px;
  }

  .modal h2 {
    font-size: 1.1rem;
  }

  .field input,
  .field select,
  .field textarea {
    padding: 8px 10px;
    font-size: 13px;
  }
}
</style>
