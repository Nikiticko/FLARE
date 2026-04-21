import apiClient from './http'

export function applicantGetBalance() {
  return apiClient.get('/applicant/balance/')
}

export function applicantGetCourses() {
  return apiClient.get('/applicant/courses/')
}

export function applicantGetPublicCourses() {
  return apiClient.get('/applicant/courses/public/')
}

export function applicantGetPayments() {
  return apiClient.get('/applicant/payments/')
}

export function applicantCreateRequest(payload) {
  return apiClient.post('/applicant/requests/create/', payload)
}
