// src/api/lessons.js
import apiClient from './http'

// Получить список уроков для админ-панели
// params может содержать: date_from, date_to, status, student, teacher и т.д.
export function adminGetLessons(params = {}) {
  return apiClient.get('/admin/lessons/', { params })
}

// Создать новый урок
// payload:
// {
//   student_email: string,    // Email ученика (или student: number)
//   teacher_email: string,    // Email учителя (или teacher: number)
//   scheduled_at: string,     // 'YYYY-MM-DDTHH:MM:SS'
//   link?: string | null,
//   comment?: string
// }
export function adminCreateLesson(payload) {
  return apiClient.post('/admin/lessons/', payload)
}

// Обновить урок
export function adminUpdateLesson(id, payload) {
  return apiClient.patch(`/admin/lessons/${id}/`, payload)
}
