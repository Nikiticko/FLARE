<!-- src/pages/admin/AdminLogsView.vue -->
<template>
  <div class="admin-page">
    <main class="admin-main">
      <div class="page-header">
        <div class="title-block">
          <h1 class="page-title">📋 Система логов</h1>
          <p class="subtitle">Аудит действий и backend-логирование</p>
        </div>
      </div>

      <section class="admin-card tabs-card">
        <div class="tabs-row">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'audit' }"
            @click="switchTab('audit')"
          >
            История действий
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'backend' }"
            @click="switchTab('backend')"
          >
            Backend-логи
          </button>
        </div>
      </section>

      <section class="admin-card filters-card">
        <div class="card-header">
          <div class="card-icon">🔍</div>
          <h2 class="card-title">Фильтры</h2>
        </div>

        <div class="filters-section">
          <div class="filters-grid">
            <div class="filter-group">
              <label class="form-label">
                <span class="label-icon">🔎</span>
                <span>Поиск</span>
              </label>
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="activeTab === 'audit' ? 'Email пользователя, тип действия...' : 'Текст ошибки, logger, сообщение...'"
                class="filter-input"
              />
            </div>

            <div v-if="activeTab === 'audit'" class="filter-group">
              <label class="form-label">
                <span class="label-icon">⚡</span>
                <span>Тип действия</span>
              </label>
              <select v-model="actionFilter" class="filter-select">
                <option value="">Все действия</option>
                <option
                  v-for="act in availableActions"
                  :key="act"
                  :value="act"
                >
                  {{ act }}
                </option>
              </select>
            </div>

            <div v-if="activeTab === 'audit'" class="filter-group">
              <label class="form-label">
                <span class="label-icon">📊</span>
                <span>Сортировка</span>
              </label>
              <select v-model="ordering" class="filter-select">
                <option value="-created_at">Новые сверху</option>
                <option value="created_at">Старые сверху</option>
              </select>
            </div>

            <div v-if="activeTab === 'backend'" class="filter-group">
              <label class="form-label">
                <span class="label-icon">🧰</span>
                <span>Лимит строк</span>
              </label>
              <select v-model.number="backendLimit" class="filter-select">
                <option :value="200">200</option>
                <option :value="500">500</option>
                <option :value="1000">1000</option>
                <option :value="2000">2000</option>
              </select>
            </div>

            <div v-if="activeTab === 'backend'" class="filter-group filter-actions-right">
              <button class="btn secondary" @click="loadBackendLogs" :disabled="backendLoading">
                {{ backendLoading ? 'Обновляем...' : 'Обновить backend-логи' }}
              </button>
              <button class="btn danger" @click="clearBackendLogs" :disabled="backendLoading">
                🧹 Очистить логи
              </button>
            </div>

            <div v-if="activeTab === 'backend'" class="filter-group full-width">
              <label class="form-label">
                <span class="label-icon">✅</span>
                <span>Уровни логов</span>
              </label>
              <div class="levels-grid">
                <label v-for="level in backendLevelOptions" :key="level" class="level-checkbox">
                  <input
                    type="checkbox"
                    :value="level"
                    v-model="backendSelectedLevels"
                  />
                  <span>{{ level }}</span>
                </label>
              </div>
            </div>

          </div>

          <div class="hint-box">
            <p v-if="activeTab === 'audit'" class="hint">
              <strong>💡 Подсказка:</strong> Лог фиксирует: создание/изменение/удаление пользователей, уроков,
              подтверждение оплат и другие важные действия. Поле
              <strong>actor_email</strong> — это кто именно сделал действие.
            </p>
            <p v-else class="hint">
              <strong>💡 Подсказка:</strong> Backend-логи выводятся компактно и поддерживают фильтр по уровням
              <strong>ERROR/WARNING/INFO/DEBUG/CRITICAL</strong>.
            </p>
          </div>
        </div>
      </section>

      <section v-if="activeTab === 'audit'" class="admin-card logs-card">
        <div class="card-header">
          <div class="card-icon">📜</div>
          <h2 class="card-title">История действий</h2>
          <button class="btn secondary card-action-btn" @click="loadLogs" :disabled="loading">
            {{ loading ? 'Обновляем...' : 'Обновить историю' }}
          </button>
        </div>

        <div v-if="error" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ error }}</span>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем логи...</p>
        </div>

        <div v-if="!loading && filteredLogs.length" class="table-container">
          <table class="logs-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Время</th>
                <th>Пользователь</th>
                <th>Действие</th>
                <th>Детали (meta)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in filteredLogs" :key="log.id">
                <td>{{ log.id }}</td>
                <td>{{ formatDateTime(log.created_at) }}</td>
                <td>
                  <div class="actor-email">
                    {{ log.actor_email || ('ID ' + log.actor) }}
                  </div>
                </td>
                <td>
                  <span class="action-tag">
                    {{ log.action }}
                  </span>
                </td>
                <td>
                  <pre class="meta-pre">{{ prettyMeta(log.meta) }}</pre>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="!loading && !filteredLogs.length" class="empty-state">
          <p>Логи не найдены (по текущим фильтрам).</p>
        </div>
      </section>

      <section v-else class="admin-card logs-card">
        <div class="card-header">
          <div class="card-icon">🧾</div>
          <h2 class="card-title">Backend-логирование</h2>
        </div>

        <div v-if="backendError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ backendError }}</span>
        </div>

        <div v-if="backendLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Загружаем backend-логи...</p>
        </div>

        <div v-if="!backendLoading && backendLogs.length" class="backend-log-window">
          <div v-for="(entry, index) in backendLogs" :key="entry.raw + index" class="backend-log-row">
            <span class="backend-ts">{{ entry.timestamp || '—' }}</span>
            <span class="backend-level" :class="levelClass(entry.level)">{{ entry.level || 'UNKNOWN' }}</span>
            <span class="backend-logger">{{ entry.logger || 'system' }}</span>
            <div class="backend-message-block">
              <div class="backend-message-line">
                <span v-if="entry.event" class="backend-event">{{ entry.event }}</span>
                <span v-if="entry.request_id" class="backend-request-id">req {{ shortRequestId(entry.request_id) }}</span>
                <span v-if="entry.status_code" class="backend-status">HTTP {{ entry.status_code }}</span>
                <span v-if="entry.duration_ms" class="backend-duration">{{ entry.duration_ms }} ms</span>
              </div>
              <span class="backend-message">{{ entry.message }}</span>
              <div v-if="entry.user_email || entry.path || entry.ip" class="backend-meta-line">
                <span v-if="entry.user_email">{{ entry.user_email }}</span>
                <span v-if="entry.user_role">{{ entry.user_role }}</span>
                <span v-if="entry.path">{{ entry.path }}</span>
                <span v-if="entry.ip">{{ entry.ip }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!backendLoading && !backendLogs.length" class="empty-state">
          <p>Backend-логи не найдены (по текущим фильтрам).</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminGetAuditLogs, adminGetBackendLogs, adminClearBackendLogs } from '../../api/admin'

const auth = useAuthStore()
const router = useRouter()

const logs = ref([])
const loading = ref(false)
const error = ref(null)

const activeTab = ref('audit')

const searchQuery = ref('')
const actionFilter = ref('')
const ordering = ref('-created_at')

const backendLogs = ref([])
const backendLoading = ref(false)
const backendError = ref(null)
const backendLimit = ref(500)
const backendLevelOptions = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'CRITICAL']
const backendSelectedLevels = ref(['ERROR', 'WARNING'])

let searchDebounceTimer = null

// загрузка логов с бэка
const loadLogs = async () => {
  loading.value = true
  error.value = null

  try {
    const params = {
      ordering: ordering.value,
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const { data } = await adminGetAuditLogs(params)
    // если включена пагинация: data.results, если нет: список
    logs.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('Ошибка загрузки логов:', err)
    error.value =
      err?.response?.data?.detail ||
      'Не удалось загрузить логи. Проверьте права и токен.'
  } finally {
    loading.value = false
  }
}

const loadBackendLogs = async () => {
  backendLoading.value = true
  backendError.value = null

  try {
    const params = {
      limit: backendLimit.value,
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    if (backendSelectedLevels.value.length) {
      params.levels = backendSelectedLevels.value.join(',')
    }

    const { data } = await adminGetBackendLogs(params)
    backendLogs.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    console.error('Ошибка загрузки backend-логов:', err)
    backendError.value =
      err?.response?.data?.detail ||
      'Не удалось загрузить backend-логи.'
  } finally {
    backendLoading.value = false
  }
}

// доступные типы действий (на основе полученных логов)
const availableActions = computed(() => {
  const set = new Set()
  for (const log of logs.value) {
    if (log.action) set.add(log.action)
  }
  return Array.from(set).sort()
})

// фильтрация по типу действия (клиентская)
const filteredLogs = computed(() => {
  if (!actionFilter.value) return logs.value
  return logs.value.filter((log) => log.action === actionFilter.value)
})

// форматирование даты
const formatDateTime = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// красивый вывод meta
const prettyMeta = (meta) => {
  if (!meta) return '—'
  try {
    return JSON.stringify(meta, null, 2)
  } catch (e) {
    return String(meta)
  }
}

const switchTab = (tab) => {
  activeTab.value = tab
}

const levelClass = (level) => {
  const upper = (level || '').toUpperCase()
  if (upper === 'ERROR' || upper === 'CRITICAL') return 'is-error'
  if (upper === 'WARNING') return 'is-warning'
  if (upper === 'INFO') return 'is-info'
  if (upper === 'DEBUG') return 'is-debug'
  return ''
}

const shortRequestId = (value) => {
  if (!value) return ''
  return String(value).slice(0, 8)
}

const clearBackendLogs = async () => {
  const isConfirmed = window.confirm('Очистить backend-логи? По умолчанию очистятся обычные логи без ошибок (soft).')
  if (!isConfirmed) return

  const fullClear = window.confirm('Нужна полная очистка? OK = удалить также error-логи и архивы, Отмена = только обычные логи.')
  const mode = fullClear ? 'full' : 'soft'

  backendLoading.value = true
  backendError.value = null
  try {
    await adminClearBackendLogs(mode)
    backendLogs.value = []
    await loadBackendLogs()
  } catch (err) {
    console.error('Ошибка очистки backend-логов:', err)
    backendError.value = err?.response?.data?.detail || 'Не удалось очистить backend-логи.'
  } finally {
    backendLoading.value = false
  }
}

// При первом заходе: проверяем auth и грузим логи
onMounted(() => {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login' })
  } else {
    loadLogs()
  }
})

onUnmounted(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
})

watch(activeTab, (tab) => {
  if (tab === 'backend') {
    loadBackendLogs()
    return
  }

  loadLogs()
})

watch(ordering, () => {
  if (activeTab.value === 'audit') {
    loadLogs()
  }
})

watch(searchQuery, () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    if (activeTab.value === 'audit') {
      loadLogs()
      return
    }
    loadBackendLogs()
  }, 450)
})

watch(backendLimit, () => {
  if (activeTab.value === 'backend') {
    loadBackendLogs()
  }
})

watch(
  () => backendSelectedLevels.value.join(','),
  () => {
    if (activeTab.value === 'backend') {
      loadBackendLogs()
    }
  }
)

// Если меняем строку поиска — просто не автоматически дергаем бэкенд каждую букву.
// Можно сделать debounce, но пока — ручная кнопка "Обновить".

// Если хочешь автообновление при изменении search — раскомментируй:
// watch(search, () => {
//   loadLogs()
// })
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.admin-page {
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  padding: 0;
  margin: 0;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.page-header {
  padding: 20px 24px 0;
  margin-bottom: 24px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.title-block {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: #FFFFFF;
  letter-spacing: -1px;
}

.subtitle {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  flex-shrink: 0;
  box-sizing: border-box;
}

.btn.primary {
  background: #FFD700;
  color: #1A1A1A;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.btn.secondary {
  background: transparent;
  color: #FFD700;
  border: 1px solid #FFD700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn.danger {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
  border: 1px solid rgba(255, 68, 68, 0.4);
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn.primary:hover:not(:disabled) {
  background: #FF8C00;
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FF8C00;
  color: #FF8C00;
}

.btn.danger:hover:not(:disabled) {
  background: rgba(255, 68, 68, 0.3);
  border-color: rgba(255, 68, 68, 0.6);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.admin-main {
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px 32px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  overflow-y: visible;
  overflow-x: hidden;
  box-sizing: border-box;
}

.admin-card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.4s ease-out;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

.card-icon {
  font-size: 2rem;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

.card-title {
  font-size: 1.75rem;
  font-weight: 900;
  margin: 0;
  color: #FFFFFF;
  letter-spacing: -0.5px;
}

.card-action-btn {
  margin-left: auto;
}

.filters-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  align-items: end;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.tabs-card {
  padding: 12px 16px;
}

.tabs-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tab-btn {
  border: 2px solid rgba(255, 215, 0, 0.35);
  background: rgba(35, 35, 35, 0.9);
  color: #fff;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
}

.tab-btn.active {
  background: #FFD700;
  color: #1A1A1A;
  border-color: #FFD700;
}

.filter-actions-right {
  justify-content: flex-end;
  align-self: end;
}

.full-width {
  grid-column: 1 / -1;
}

.levels-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.level-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.95);
}

.backend-log-window {
  max-height: 65vh;
  overflow: auto;
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 8px;
  background: rgba(18, 18, 18, 0.9);
}

.backend-log-row {
  display: grid;
  grid-template-columns: 170px 100px 220px 1fr;
  gap: 10px;
  padding: 8px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.82rem;
  line-height: 1.35;
}

.backend-ts,
.backend-logger {
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.backend-level {
  font-weight: 700;
}

.backend-message {
  color: rgba(255, 255, 255, 0.95);
  word-break: break-word;
}

.backend-message-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.backend-message-line,
.backend-meta-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.backend-event,
.backend-request-id,
.backend-status,
.backend-duration {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 0.72rem;
  line-height: 1.2;
  border: 1px solid rgba(255, 215, 0, 0.22);
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.82);
}

.backend-event {
  border-color: rgba(255, 215, 0, 0.35);
  color: #ffd866;
}

.backend-meta-line {
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.74rem;
}

.backend-level.is-error {
  color: #ff7d7d;
}

.backend-level.is-warning {
  color: #ffcf66;
}

.backend-level.is-info {
  color: #8ed7ff;
}

.backend-level.is-debug {
  color: #b9a7ff;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.label-icon {
  font-size: 1.1rem;
}

.filter-input,
.filter-select {
  width: 100%;
  min-width: 0;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid rgba(255, 215, 0, 0.3);
  background: rgba(40, 45, 60, 0.8);
  color: #FFFFFF;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: inherit;
  box-sizing: border-box;
}

.filter-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(40, 45, 60, 1);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
  transform: translateY(-2px);
}

.filter-select {
  cursor: pointer;
}

.hint-box {
  padding: 16px;
  background: rgba(255, 215, 0, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 215, 0, 0.2);
}

.hint {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.hint strong {
  color: #FFD700;
  font-weight: 700;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(255, 107, 107, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 107, 107, 0.4);
  border-radius: 12px;
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  margin-bottom: 20px;
}

.error-icon {
  font-size: 1.2rem;
}

.table-container {
  overflow-x: auto;
  overflow-y: visible;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  -webkit-overflow-scrolling: touch;
}

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: rgba(40, 40, 40, 0.5);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.5);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.7);
}

.logs-table {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
  font-size: 0.9rem;
  table-layout: auto;
}

.logs-table thead {
  background: rgba(255, 215, 0, 0.1);
}

.logs-table th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 700;
  color: #FFFFFF;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  box-sizing: border-box;
}

.logs-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 215, 0, 0.1);
  color: rgba(255, 255, 255, 0.9);
  vertical-align: top;
  box-sizing: border-box;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.logs-table tbody tr {
  transition: background 0.2s;
}

.logs-table tbody tr:hover {
  background: rgba(255, 215, 0, 0.1);
}

.actor-email {
  word-break: break-word;
  overflow-wrap: break-word;
  font-weight: 500;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 215, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 215, 0, 0.3);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #FFD700;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  letter-spacing: 0.5px;
}

.meta-pre {
  margin: 0;
  font-size: 0.75rem;
  max-height: 120px;
  overflow: auto;
  overflow-x: auto;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid rgba(255, 215, 0, 0.2);
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Courier New', monospace;
  line-height: 1.5;
  max-width: 400px;
  min-width: 0;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  box-sizing: border-box;
}

.meta-pre::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.meta-pre::-webkit-scrollbar-track {
  background: rgba(40, 40, 40, 0.5);
  border-radius: 3px;
}

.meta-pre::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.5);
  border-radius: 3px;
}

.meta-pre::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.7);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

@media (max-width: 1200px) {
  .admin-main {
    padding: 0 24px 32px;
  }

  .filters-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 16px 0;
    margin-bottom: 20px;
  }

  .page-title {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 0.9rem;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .admin-main {
    padding: 0 16px 24px;
    gap: 16px;
  }

  .admin-card {
    padding: 20px;
  }

  .card-header {
    margin-bottom: 20px;
    padding-bottom: 16px;
  }

  .card-icon {
    font-size: 1.5rem;
  }

  .card-title {
    font-size: 1.5rem;
  }

  .filters-section {
    gap: 16px;
  }

  .filters-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .filter-group.filter-actions-right {
    flex-direction: column;
    align-items: stretch;
  }

  .hint-box {
    padding: 12px;
  }

  .hint {
    font-size: 0.85rem;
  }

  .table-container {
    overflow-x: auto;
    margin-top: 12px;
  }

  .logs-table {
    min-width: 900px;
    font-size: 0.85rem;
  }

  .logs-table th,
  .logs-table td {
    padding: 10px 12px;
  }

  .logs-table th {
    font-size: 0.8rem;
  }

  .actor-email {
    max-width: 200px;
  }

  .meta-pre {
    max-width: 250px;
    max-height: 100px;
    font-size: 0.7rem;
    padding: 10px;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 12px 0;
    margin-bottom: 16px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 0.85rem;
  }

  .admin-main {
    padding: 0 12px 20px;
    gap: 12px;
  }

  .admin-card {
    padding: 16px;
    border-width: 2px;
  }

  .card-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    gap: 10px;
  }

  .card-icon {
    font-size: 1.3rem;
  }

  .card-title {
    font-size: 1.2rem;
  }

  .filters-section {
    gap: 12px;
  }

  .filters-grid {
    gap: 12px;
  }

  .filter-group {
    gap: 6px;
  }

  .form-label {
    font-size: 0.85rem;
  }

  .label-icon {
    font-size: 1rem;
  }

  .filter-input,
  .filter-select {
    font-size: 0.9rem;
    padding: 10px 12px;
  }

  .btn {
    padding: 10px 16px;
    font-size: 0.85rem;
  }

  .hint-box {
    padding: 10px;
  }

  .hint {
    font-size: 0.8rem;
    line-height: 1.5;
  }

  .table-container {
    margin-top: 10px;
    margin-left: -16px;
    margin-right: -16px;
    padding: 0 16px;
  }

  .logs-table {
    min-width: 800px;
    font-size: 0.8rem;
  }

  .logs-table th,
  .logs-table td {
    padding: 8px 10px;
  }

  .logs-table th {
    font-size: 0.75rem;
  }

  .logs-table td {
    font-size: 0.75rem;
  }

  .actor-email {
    max-width: 150px;
    font-size: 0.75rem;
  }

  .action-tag {
    font-size: 0.7rem;
    padding: 4px 8px;
  }

  .meta-pre {
    max-width: 200px;
    max-height: 80px;
    font-size: 0.65rem;
    padding: 8px;
    line-height: 1.4;
  }

  .error-message {
    padding: 10px 12px;
    font-size: 0.85rem;
    margin-bottom: 16px;
  }

  .loading-state {
    padding: 30px 20px;
  }

  .spinner {
    width: 36px;
    height: 36px;
    border-width: 3px;
  }

  .empty-state {
    padding: 30px 20px;
    font-size: 0.9rem;
  }
}
</style>
