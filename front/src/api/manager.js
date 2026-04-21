import apiClient from './http'

export function managerGetClients(params = {}) {
  return apiClient.get('/manager/clients/', { params })
}

export function managerGetLessons(params = {}) {
  return apiClient.get('/manager/lessons/', { params })
}

export function managerCreateLesson(payload) {
  return apiClient.post('/manager/lessons/', payload)
}

export function managerUpdateLesson(id, payload) {
  return apiClient.patch(`/manager/lessons/${id}/`, payload)
}

export function managerCancelLesson(id, cancellationReason) {
  return apiClient.post(`/manager/lessons/${id}/cancel/`, {
    cancellation_reason: cancellationReason,
  })
}

export function managerDebitLesson(id, markDone = true) {
  return apiClient.post(`/manager/lessons/${id}/debit/`, { mark_done: markDone })
}

export function managerGetPayments(params = {}) {
  return apiClient.get('/manager/payments/', { params })
}

export function managerGetStudentBalance(studentId) {
  return apiClient.get(`/manager/students/${studentId}/balance/`)
}

export function managerUpdateStudentBalance(studentId, payload) {
  return apiClient.patch(`/manager/students/${studentId}/balance/update/`, payload)
}

export function managerSearchUserByEmail(email) {
  return apiClient.get('/manager/users/by-email/', { params: { email } })
}

export function managerGetUsersAutocomplete(role, search = '') {
  return apiClient.get('/manager/users/autocomplete/', { params: { role, search } })
}

export function managerGetAutocomplete(type) {
  return apiClient.get('/manager/autocomplete/', { params: { type } })
}

export function managerGetClientRequests(params = {}) {
  return apiClient.get('/manager/requests/', { params })
}

export function managerUpdateClientRequest(id, payload) {
  return apiClient.patch(`/manager/requests/${id}/`, payload)
}
