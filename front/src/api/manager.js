// src/api/manager.js
import apiClient from './http'

// ===== КЛИЕНТЫ =====

// Получить список клиентов (учеников/абитуриентов)
export function managerGetClients(params = {}) {
  return apiClient.get('/manager/clients/', { params })
}

// ===== УРОКИ =====

// Получить список уроков
export function managerGetLessons(params = {}) {
  return apiClient.get('/manager/lessons/', { params })
}

// Создать урок
export function managerCreateLesson(payload) {
  return apiClient.post('/manager/lessons/', payload)
}

// Обновить урок
export function managerUpdateLesson(id, payload) {
  return apiClient.patch(`/manager/lessons/${id}/`, payload)
}

// Отменить урок
export function managerCancelLesson(id, cancellationReason) {
  return apiClient.post(`/manager/lessons/${id}/cancel/`, {
    cancellation_reason: cancellationReason,
  })
}

// Списать урок с баланса
export function managerDebitLesson(id, markDone = true) {
  return apiClient.post(`/manager/lessons/${id}/debit/`, { mark_done: markDone })
}

// ===== ПЛАТЕЖИ =====

// Получить список платежей
export function managerGetPayments(params = {}) {
  return apiClient.get('/manager/payments/', { params })
}

// Создать платеж
export function managerCreatePayment(payload) {
  return apiClient.post('/manager/payments/', payload)
}

// Подтвердить платеж и начислить уроки
export function managerConfirmPayment(id, lessonsToAdd) {
  return apiClient.post(`/manager/payments/${id}/confirm/`, { lessons_to_add: lessonsToAdd })
}

// ===== БАЛАНС =====

// Получить баланс ученика
export function managerGetStudentBalance(studentId) {
  return apiClient.get(`/manager/students/${studentId}/balance/`)
}

// Изменить баланс ученика
// payload: { lessons_available: 10 } или { delta: 5 }
export function managerUpdateStudentBalance(studentId, payload) {
  return apiClient.patch(`/manager/students/${studentId}/balance/update/`, payload)
}

// Поиск пользователя по email
export function managerSearchUserByEmail(email) {
  return apiClient.get('/manager/users/by-email/', { params: { email } })
}

// Автодополнение пользователей
export function managerGetUsersAutocomplete(role, search = '') {
  return apiClient.get('/manager/users/autocomplete/', { params: { role, search } })
}

// Получить список email для автодополнения
// type: 'students' | 'teachers'
export function managerGetAutocomplete(type) {
  return apiClient.get('/manager/autocomplete/', { params: { type } })
}

// ===== ОБРАЩЕНИЯ КЛИЕНТОВ =====

// Получить список обращений клиентов
// params: { status: 'SENT' | 'RESPONDED' }
export function managerGetClientRequests(params = {}) {
  return apiClient.get('/manager/requests/', { params })
}

// Изменить статус обращения
// payload: { status: 'RESPONDED' }
export function managerUpdateClientRequest(id, payload) {
  return apiClient.patch(`/manager/requests/${id}/`, payload)
}





