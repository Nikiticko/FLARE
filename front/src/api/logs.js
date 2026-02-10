// src/api/logs.js
import apiClient from './http'

// Получить список логов аудита
// Пока без жёстких параметров — забираем всё, что вернёт бэк (с учетом пагинации)
export function adminGetAuditLogs(params = {}) {
  return apiClient.get('/admin/audit/', { params })
}
