// src/api/applicant.js
import apiClient from './http'

// Получить баланс
export function applicantGetBalance() {
  return apiClient.get('/applicant/balance/')
}

// Получить список курсов
export function applicantGetCourses() {
  return apiClient.get('/applicant/courses/')
}

// Получить публичные курсы (без авторизации)
export function applicantGetPublicCourses() {
  return apiClient.get('/applicant/courses/public/')
}

// Получить историю платежей
export function applicantGetPayments() {
  return apiClient.get('/applicant/payments/')
}

// Создать платеж
export function applicantCreatePayment(payload) {
  return apiClient.post('/applicant/payments/create/', payload)
}

// Создать обращение к менеджеру
export function applicantCreateRequest(payload) {
  return apiClient.post('/applicant/requests/create/', payload)
}



