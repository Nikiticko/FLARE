// src/api/student.js
import apiClient from './http'

export function getDashboard() {
  return apiClient.get('/dashboard/')
}

export function studentGetDashboard() {
  return apiClient.get('/student/dashboard/')
}

export function studentGetCourses() {
  return apiClient.get('/student/courses/')
}

export function studentGetLessons(params = {}) {
  return apiClient.get('/student/lessons/', { params })
}

export function studentGetBalance() {
  return apiClient.get('/student/balance/')
}

export function studentGetPayments() {
  return apiClient.get('/student/payments/')
}

export function studentGetSeasonSummary() {
  return apiClient.get('/student/season/summary/')
}

export function studentCreateRequest(payload) {
  return apiClient.post('/student/requests/create/', payload)
}
