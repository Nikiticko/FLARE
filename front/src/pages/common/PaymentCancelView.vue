<template>
  <div class="payment-result-page">
    <div class="payment-result-card">
      <h1 class="title">Оплата отменена</h1>
      <p class="subtitle">Платёж не был завершён. Вы можете вернуться и попробовать снова.</p>
      <div class="actions">
        <RouterLink class="btn btn-primary" to="/payment">Вернуться к оплате</RouterLink>
        <RouterLink class="btn btn-secondary" to="/dashboard">В личный кабинет</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
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

.actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.btn {
  text-decoration: none;
  border-radius: 10px;
  padding: 12px 16px;
  font-weight: 800;
}

.btn-primary {
  background: #FFD700;
  color: #1A1A1A;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.12);
  color: #FFFFFF;
}
</style>
