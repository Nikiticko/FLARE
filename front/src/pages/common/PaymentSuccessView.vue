<template>
  <div class="payment-result-page">
    <div class="payment-result-card">
      <h1 class="title">Оплата обрабатывается</h1>
      <p class="subtitle">{{ statusText }}</p>
      <RouterLink class="back-btn" to="/dashboard">Вернуться в личный кабинет</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPaymentStatus } from '../../api/payments'

const route = useRoute()
const router = useRouter()

const pollTimer = ref(null)
const status = ref('pending')
const statusError = ref('')

const localPaymentId = computed(() => route.query.local_payment_id || null)
const statusToken = computed(() => route.query.status_token || null)

const statusText = computed(() => {
  if (statusError.value) {
    return statusError.value
  }
  if (status.value === 'succeeded') {
    return 'Платёж успешно получен, уроки начислены на ваш баланс.'
  }
  if (status.value === 'canceled') {
    return 'Платёж отменён. Вы можете попробовать ещё раз.'
  }
  if (status.value === 'failed') {
    return 'Платёж не прошёл. Попробуйте снова или используйте другой способ оплаты.'
  }
  return 'Ожидаем подтверждение оплаты от ЮKassa...'
})

async function checkStatus() {
  if (!localPaymentId.value) {
    statusError.value = 'Не найден идентификатор платежа. Проверьте историю оплат в личном кабинете.'
    stopPolling()
    return
  }

  try {
    const { data } = await getPaymentStatus(localPaymentId.value, statusToken.value)
    status.value = (data?.status || 'pending').toLowerCase()

    if (status.value === 'succeeded') {
      stopPolling()
      return
    }

    if (status.value === 'canceled') {
      stopPolling()
      router.replace({ name: 'payment-cancel' })
    }
  } catch (error) {
    if (error?.response?.status === 401) {
      stopPolling()
      router.replace({ name: 'login', query: { redirect: window.location.pathname + window.location.search } })
      return
    }
    // оставляем polling; временные ошибки сети возможны
  }
}

function startPolling() {
  stopPolling()
  pollTimer.value = setInterval(checkStatus, 3000)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

onMounted(async () => {
  await checkStatus()
  startPolling()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.payment-result-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1A1A1A;
  color: #FFFFFF;
  padding: 24px;
}

.payment-result-card {
  width: 100%;
  max-width: 620px;
  background: rgba(36, 36, 36, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 900;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.55;
}

.back-btn {
  margin-top: 8px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  text-decoration: none;
  background: #FFD700;
  color: #1A1A1A;
  border-radius: 10px;
  padding: 12px 16px;
  font-weight: 800;
}
</style>
