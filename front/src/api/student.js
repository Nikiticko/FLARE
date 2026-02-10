// src/api/student.js
import apiClient from './http'

// Получить унифицированный дашборд (работает для STUDENT и APPLICANT)
export function getDashboard() {
  return apiClient.get('/dashboard/')
}

// Получить данные личного кабинета ученика (legacy)
export function studentGetDashboard() {
  return apiClient.get('/student/dashboard/')
}

// Получить список курсов
export function studentGetCourses() {
  return apiClient.get('/student/courses/')
}

// Получить список уроков
export function studentGetLessons(params = {}) {
  return apiClient.get('/student/lessons/', { params })
}

// Получить баланс
export function studentGetBalance() {
  return apiClient.get('/student/balance/')
}

// Получить историю платежей
export function studentGetPayments() {
  return apiClient.get('/student/payments/')
}

// Создать платеж
export function studentCreatePayment(payload) {
  return apiClient.post('/student/payments/create/', payload)
}

// Получить краткую информацию о сезоне
export function studentGetSeasonSummary() {
  return apiClient.get('/student/season/summary/')
}

// Создать обращение к менеджеру
export function studentCreateRequest(payload) {
  return apiClient.post('/student/requests/create/', payload)
}





