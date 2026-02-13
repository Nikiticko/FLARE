import apiClient from './http'

export function getPublicPaymentConfig() {
  return apiClient.get('/payments/config/')
}

export function createYookassaPayment(payload) {
  return apiClient.post('/payments/create/', payload)
}

export function getPaymentStatus(localPaymentId, statusToken = null) {
  const params = statusToken ? { status_token: statusToken } : undefined
  return apiClient.get(`/payments/${localPaymentId}/status/`, { params })
}
