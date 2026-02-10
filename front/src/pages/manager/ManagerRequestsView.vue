<!-- src/pages/manager/ManagerRequestsView.vue -->
<template>
  <div class="manager-requests-page">
    <main class="main-container">
      <div class="page-header">
        <h1>Связь с клиентами</h1>
        <div class="tabs">
          <button
            :class="['tab', { active: activeTab === 'active' }]"
            @click="activeTab = 'active'"
          >
            Новые обращения
          </button>
          <button
            :class="['tab', { active: activeTab === 'archive' }]"
            @click="activeTab = 'archive'"
          >
            Архив
          </button>
        </div>
      </div>

      <div class="content-section">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Загрузка обращений...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <span class="error-icon">⚠️</span>
          <span>{{ error }}</span>
        </div>

        <div v-else-if="requests.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p>{{ activeTab === 'active' ? 'Нет новых обращений' : 'Архив пуст' }}</p>
        </div>

        <div v-else class="requests-list">
          <div
            v-for="request in requests"
            :key="request.id"
            class="request-card"
          >
            <div class="request-header">
              <div class="request-client">
                <div class="client-email">{{ request.client_email }}</div>
                <div class="request-date">{{ formatDate(request.created_at) }}</div>
              </div>
              <div class="request-status" :class="request.status.toLowerCase()">
                {{ getStatusText(request.status) }}
              </div>
            </div>

            <div v-if="request.comment" class="request-comment">
              {{ request.comment }}
            </div>
            <div v-else class="request-comment empty">
              Комментарий не указан
            </div>

            <div v-if="request.status === 'RESPONDED'" class="request-response-info">
              <div class="response-manager">
                <strong>Менеджер:</strong> {{ request.manager_email }}
              </div>
              <div class="response-date">
                <strong>Дата реакции:</strong> {{ formatDate(request.responded_at) }}
              </div>
            </div>

            <div v-if="request.status === 'SENT'" class="request-actions">
              <button
                class="btn-respond"
                @click="handleRespond(request.id)"
                :disabled="responding"
              >
                {{ responding ? 'Обработка...' : 'Отметить как обработанное' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { managerGetClientRequests, managerUpdateClientRequest } from '../../api/manager'

const auth = useAuthStore()
const router = useRouter()

const activeTab = ref('active')
const requests = ref([])
const loading = ref(false)
const error = ref(null)
const responding = ref(false)

const loadRequests = async () => {
  loading.value = true
  error.value = null

  try {
    const status = activeTab.value === 'archive' ? 'RESPONDED' : 'SENT'
    const { data } = await managerGetClientRequests({ status })
    requests.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('load requests error:', err)
    error.value = 'Не удалось загрузить обращения'
  } finally {
    loading.value = false
  }
}

const handleRespond = async (requestId) => {
  responding.value = true
  try {
    await managerUpdateClientRequest(requestId, { status: 'RESPONDED' })
    // Если мы в активных, перезагружаем список
    if (activeTab.value === 'active') {
      await loadRequests()
    }
  } catch (err) {
    console.error('respond error:', err)
    error.value = 'Не удалось обновить статус обращения'
  } finally {
    responding.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusText = (status) => {
  const statusMap = {
    'SENT': 'Отправлено',
    'RESPONDED': 'Есть реакция на обращение',
  }
  return statusMap[status] || status
}

watch(activeTab, () => {
  loadRequests()
})

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
    return
  }
  loadRequests()
})
</script>

<style scoped>
.manager-requests-page {
  min-height: 100vh;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  position: relative;
}

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  position: relative;
  z-index: 1;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 3rem;
  font-weight: 900;
  color: #FFFFFF;
  margin: 0 0 24px 0;
  letter-spacing: -1px;
}

.tabs {
  display: flex;
  gap: 12px;
}

.tab {
  padding: 12px 24px;
  background: transparent;
  border: 1px solid #FFD700;
  border-radius: 8px;
  color: #FFD700;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-family: inherit;
}

.tab:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.tab.active {
  background: #FFD700;
  color: #1A1A1A;
  border-color: #FFD700;
}

.content-section {
  min-height: 400px;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.9);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  color: #ffb3b3;
}

.error-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 12px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  opacity: 0.7;
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.request-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.request-card:hover {
  box-shadow: 0 12px 30px rgba(255, 215, 0, 0.3);
  transform: translateY(-2px);
  border-color: #FF8C00;
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

.request-client {
  flex: 1;
}

.client-email {
  font-size: 1.1rem;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 4px;
}

.request-date {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
}

.request-status {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.request-status.sent {
  background: rgba(255, 152, 0, 0.3);
  color: #ffcc80;
  border: 1px solid rgba(255, 152, 0, 0.5);
}

.request-status.responded {
  background: rgba(76, 175, 80, 0.3);
  color: #a5d6a7;
  border: 1px solid rgba(76, 175, 80, 0.5);
}

.request-comment {
  margin-bottom: 16px;
  padding: 16px;
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  white-space: pre-wrap;
}

.request-comment.empty {
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

.request-response-info {
  margin-bottom: 16px;
  padding: 16px;
  background: rgba(76, 175, 80, 0.15);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 12px;
  color: #ffffff;
  font-size: 0.9rem;
}

.response-manager,
.response-date {
  margin-bottom: 8px;
}

.response-manager:last-child,
.response-date:last-child {
  margin-bottom: 0;
}

.request-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-respond {
  padding: 10px 20px;
  background: #FFD700;
  color: #1A1A1A;
  border: 1px solid #FFD700;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-family: inherit;
}

.btn-respond:hover:not(:disabled) {
  background: #FF8C00;
  border-color: #FF8C00;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn-respond:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }

  .request-header {
    flex-direction: column;
    gap: 12px;
  }

  .request-status {
    align-self: flex-start;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.5rem;
  }

  .request-card {
    padding: 12px;
  }

  .request-header {
    gap: 8px;
  }

  .request-email {
    font-size: 0.9rem;
  }

  .request-date {
    font-size: 0.8rem;
  }

  .request-comment {
    font-size: 0.85rem;
    padding: 10px;
  }

  .btn-respond {
    padding: 8px 16px;
    font-size: 0.85rem;
  }
}
</style>



