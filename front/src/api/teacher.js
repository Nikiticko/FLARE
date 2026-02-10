// src/api/teacher.js
import apiClient from './http'

// ===== УРОКИ =====

// Получить список уроков учителя
export function teacherGetLessons(params = {}) {
  return apiClient.get('/teacher/lessons/', { params })
}

// Создать урок для ученика
export function teacherCreateLesson(payload) {
  return apiClient.post('/teacher/lessons/', payload)
}

// Получить детали урока
export function teacherGetLesson(id) {
  return apiClient.get(`/teacher/lessons/${id}/`)
}

// Обновить урок
export function teacherUpdateLesson(id, payload) {
  return apiClient.patch(`/teacher/lessons/${id}/update/`, payload)
}

// ===== УЧЕНИКИ =====

// Получить список учеников учителя
export function teacherGetStudents(params = {}) {
  return apiClient.get('/teacher/students/', { params })
}

// Получить уроки конкретного ученика
export function teacherGetStudentLessons(studentId, params = {}) {
  return apiClient.get(`/teacher/students/${studentId}/lessons/`, { params })
}

// Поиск ученика по email (с проверкой, что это ученик учителя)
export function teacherSearchStudentByEmail(email) {
  return apiClient.get('/teacher/students/by-email/', { params: { email } })
}

// Автодополнение учеников учителя
export function teacherGetStudentsAutocomplete(search = '') {
  return apiClient.get('/teacher/students/autocomplete/', { params: { search } })
}

// Получить список email учеников учителя для автодополнения
export function teacherGetAutocomplete() {
  return apiClient.get('/teacher/autocomplete/')
}







