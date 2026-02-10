<!-- src/pages/common/PaymentCalculatorView.vue -->
<template>
  <div class="payment-page">
    <div class="payment-content">
      <h1 class="page-title">Оплата занятий</h1>

      <!-- Основные блоки -->
      <div class="main-blocks">
        <!-- Блок: Стоимость одного занятия -->
        <div class="card price-card">
          <h2 class="card-title">Стоимость одного занятия</h2>
          <div class="price-block">
            <div class="price-value">800 ₽</div>
            <div class="price-label">за 1 урок</div>
          </div>
        </div>

        <!-- Блок: Важная информация -->
        <div class="card info-card">
          <h2 class="card-title">Важная информация</h2>
          <div class="info-block warning">
            <div class="info-icon">⚠️</div>
            <div class="info-text">
              На данный момент на платформе нет менеджеров. Чек об оплате необходимо отправлять лично преподавателю, по совместительству менеджеру и администратору.
            </div>
          </div>
        </div>
      </div>

      <!-- Кнопка для раскрытия инструкции -->
      <div class="instruction-toggle">
        <button
          type="button"
          class="instruction-btn"
          :class="{ 'instruction-btn--open': showInstructions }"
          @click="showInstructions = !showInstructions"
        >
          <span class="instruction-btn-text">
            {{ showInstructions ? 'Скрыть инструкцию' : 'Инструкция по оплате' }}
          </span>
          <span class="instruction-btn-icon">{{ showInstructions ? '▲' : '▼' }}</span>
        </button>
      </div>

      <!-- Раскрываемые блоки -->
      <Transition name="expand">
        <div v-if="showInstructions" class="expandable-blocks">
          <!-- Реквизиты для оплаты -->
          <div class="card payment-card">
            <h2 class="card-title">Реквизиты для оплаты</h2>
            <div class="payment-info">
              <div class="payment-row">
                <span class="payment-label">Способ оплаты:</span>
                <span class="payment-value">СБП (Система быстрых платежей)</span>
              </div>
              <div class="payment-row">
                <span class="payment-label">Банк:</span>
                <span class="payment-value">ВТБ</span>
              </div>
              <div class="payment-row">
                <span class="payment-label">Номер телефона:</span>
                <span class="payment-value phone-number">+7 978 474 13 26</span>
              </div>
              <div class="payment-row">
                <span class="payment-label">Получатель:</span>
                <span class="payment-value">Семененко Никита Сергеевич</span>
              </div>
            </div>
          </div>

          <!-- Отправка чека -->
          <div class="card contact-card">
            <h2 class="card-title">Отправка чека</h2>
            <p class="contact-description">
              После оплаты отправьте скриншот или фото чека преподавателю для подтверждения и начисления занятий на ваш баланс.
            </p>
            <div class="contact-info">
              <div class="contact-row">
                <span class="contact-label">Telegram:</span>
                <a href="https://t.me/nikiticko" target="_blank" class="contact-link">@nikiticko</a>
              </div>
              <div class="contact-row">
                <span class="contact-label">Телефон:</span>
                <span class="contact-value">+7 978 474 13 26</span>
              </div>
            </div>
          </div>

          <!-- Как оплатить -->
          <div class="card instructions-card">
            <h2 class="card-title">Как оплатить</h2>
            <div class="steps">
              <div class="step">
                <div class="step-number">1</div>
                <div class="step-text">Откройте приложение вашего банка и выберите оплату по СБП</div>
              </div>
              <div class="step">
                <div class="step-number">2</div>
                <div class="step-text">Введите номер телефона <strong>+7 978 474 13 26</strong> и выберите банк <strong>ВТБ</strong></div>
              </div>
              <div class="step">
                <div class="step-number">3</div>
                <div class="step-text">Укажите сумму (800₽ × количество уроков) и выполните перевод</div>
              </div>
              <div class="step">
                <div class="step-number">4</div>
                <div class="step-text">Отправьте скриншот чека в Telegram <strong>@nikiticko</strong></div>
              </div>
              <div class="step">
                <div class="step-number">5</div>
                <div class="step-text">После подтверждения занятия будут начислены на ваш баланс</div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Footer from '../../components/Footer.vue'

const showInstructions = ref(false)
</script>

<style scoped>
.payment-page {
  min-height: 100vh;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
}

/* Контент */
.payment-content {
  flex: 1;
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px;
  width: 100%;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 900;
  color: #FFFFFF;
  text-align: center;
  margin: 0 0 32px 0;
}

/* Основные блоки */
.main-blocks {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

/* Карточки */
.card {
  background: rgba(40, 40, 40, 0.8);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 24px;
}

.card-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

/* Карточка с ценой */
.price-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.price-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.price-value {
  font-size: 3.5rem;
  font-weight: 900;
  color: #FFD700;
  text-shadow: 0 4px 20px rgba(255, 215, 0, 0.4);
}

.price-label {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

/* Информационная карточка */
.info-block {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
  border-radius: 8px;
}

.info-block.warning {
  background: rgba(255, 193, 7, 0.15);
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-text {
  font-size: 1rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
}

/* Кнопка инструкции */
.instruction-toggle {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.instruction-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1A1A1A;
  background: #FFD700;
  border: 2px solid #FFD700;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.instruction-btn:hover {
  background: #FFC700;
  border-color: #FFC700;
  transform: translateY(-2px);
}

.instruction-btn--open {
  background: rgba(255, 215, 0, 0.3);
  color: #FFD700;
  border-color: #FFD700;
}

.instruction-btn--open:hover {
  background: rgba(255, 215, 0, 0.4);
}

.instruction-btn-icon {
  font-size: 0.9rem;
}

/* Раскрываемые блоки */
.expandable-blocks {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Карточка с реквизитами */
.payment-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.payment-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.payment-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.payment-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #FFFFFF;
}

.phone-number {
  font-size: 1.3rem;
  color: #FFD700;
  font-weight: 700;
}

/* Карточка с контактами */
.contact-description {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(50, 50, 50, 0.6);
  border: 2px solid #FFD700;
  border-radius: 8px;
  padding: 16px;
}

.contact-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.contact-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.contact-value {
  font-size: 1rem;
  font-weight: 600;
  color: #FFFFFF;
}

.contact-link {
  font-size: 1.1rem;
  font-weight: 700;
  color: #FFD700;
  text-decoration: none;
  transition: all 0.3s ease;
}

.contact-link:hover {
  color: #FF8C00;
  text-decoration: underline;
}

/* Карточка с инструкцией */
.steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.step-number {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: rgba(255, 215, 0, 0.2);
  border: 2px solid #FFD700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  color: #FFD700;
}

.step-text {
  font-size: 1rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
  padding-top: 6px;
}

.step-text strong {
  color: #FFD700;
}

/* Анимация раскрытия */
.expand-enter-active,
.expand-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Адаптивность */
@media (max-width: 768px) {
  .payment-content {
    padding: 20px 16px;
  }

  .page-title {
    font-size: 1.8rem;
    margin-bottom: 24px;
  }

  .main-blocks {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .card {
    padding: 20px;
  }

  .card-title {
    font-size: 1.1rem;
    margin-bottom: 16px;
  }

  .price-value {
    font-size: 2.5rem;
  }

  .price-label {
    font-size: 1rem;
  }

  .instruction-btn {
    padding: 12px 20px;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .payment-content {
    padding: 16px 12px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .card {
    padding: 16px;
  }

  .price-value {
    font-size: 2rem;
  }

  .step {
    gap: 12px;
  }

  .step-number {
    width: 30px;
    height: 30px;
    font-size: 0.9rem;
  }

  .step-text {
    font-size: 0.9rem;
  }
}
</style>
