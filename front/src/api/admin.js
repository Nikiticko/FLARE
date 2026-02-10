// src/api/admin.js
import apiClient from './http'

// ===== USERS =====

// список пользователей (фильтры: role, search)
export function adminGetUsers(params = {}) {
  return apiClient.get('/admin/users/', { params })
}

// Поиск пользователя по email
export function adminSearchUserByEmail(email) {
  return apiClient.get('/admin/users/by-email/', { params: { email } })
}

// Автодополнение пользователей
// Используем эндпоинт менеджера, так как он доступен для админа
export function adminGetUsersAutocomplete(role, search = '') {
  return apiClient.get('/manager/users/autocomplete/', { params: { role, search } })
}

// обновление данных пользователя (email, phone, ФИО и т.п.)
export function adminUpdateUser(id, payload) {
  return apiClient.patch(`/admin/users/${id}/`, payload)
}

// удаление пользователя
export function adminDeleteUser(id) {
  return apiClient.delete(`/admin/users/${id}/`)
}

// смена роли пользователя
export function adminSetUserRole(id, role) {
  return apiClient.patch(`/admin/users/${id}/set-role/`, { role })
}

// сброс пароля пользователя на базовый "12345678"
export function adminResetPassword(id) {
  return apiClient.post(`/admin/users/${id}/reset-password/`)
}

// ===== AUDIT LOGS =====

// получить список логов (поддерживает search, ordering, page — если включена пагинация)
export function adminGetAuditLogs(params = {}) {
  return apiClient.get('/admin/audit/', { params })
}

// ===== COURSES =====

// получить список курсов
export function adminGetCourses() {
  return apiClient.get('/admin/courses/')
}

// получить детали курса
export function adminGetCourse(id) {
  return apiClient.get(`/admin/courses/${id}/`)
}

// создать курс
export function adminCreateCourse(payload) {
  return apiClient.post('/admin/courses/', payload)
}

// обновить курс
export function adminUpdateCourse(id, payload) {
  return apiClient.patch(`/admin/courses/${id}/`, payload)
}

// удалить курс
export function adminDeleteCourse(id) {
  return apiClient.delete(`/admin/courses/${id}/`)
}
