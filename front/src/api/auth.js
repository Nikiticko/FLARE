import apiClient, { ensureCsrfCookie } from './http'

export async function registerApi(payload) {
  await ensureCsrfCookie()
  return apiClient.post('/auth/register/', payload)
}

export async function loginApi({ email, password }) {
  await ensureCsrfCookie()
  return apiClient.post('/auth/login/', { email, password })
}

export function getMeApi() {
  return apiClient.get('/auth/me/')
}

export async function adminLoginApi({ email, password }) {
  await ensureCsrfCookie()
  return apiClient.post('/auth/admin-login/', { email, password })
}

export function updateMeApi(payload) {
  const config = payload instanceof FormData
    ? { headers: { 'Content-Type': 'multipart/form-data' } }
    : undefined
  return apiClient.patch('/auth/me/', payload, config)
}

export function verifyPasswordApi(payload) {
  return apiClient.post('/auth/verify-password/', payload)
}

export function changePasswordApi(payload) {
  return apiClient.post('/auth/change-password/', payload)
}

export function logoutApi() {
  return apiClient.post('/auth/logout/')
}

export function getCsrfApi() {
  return apiClient.get('/auth/csrf/')
}
