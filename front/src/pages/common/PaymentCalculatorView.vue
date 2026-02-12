<!-- src/pages/common/PaymentCalculatorView.vue -->
<template>
  <div class="payment-page">
    <div class="payment-content">
      <h1 class="page-title">Оплата занятий</h1>
      <div class="card calculator-card">
        <div class="calculator-header">
          <h2 class="card-title">Калькулятор оплаты</h2>
          <div class="price-row">
            <span class="price-label">Цена за занятие</span>
            <span class="price-value">800 ₽</span>
          </div>
        </div>

        <div class="preset-options">
          <button
            type="button"
            class="preset-option"
            :class="{ 'preset-option--active': selectedOption === 1 }"
            @click="selectOption(1)"
          >
            1 занятие
          </button>
          <button
            type="button"
            class="preset-option"
            :class="{ 'preset-option--active': selectedOption === 5 }"
            @click="selectOption(5)"
          >
            5 занятий
          </button>
          <button
            type="button"
            class="preset-option"
            :class="{ 'preset-option--active': selectedOption === 10 }"
            @click="selectOption(10)"
          >
            10 занятий
          </button>
        </div>

        <div class="custom-input">
          <label class="input-label" for="customCount">Свой вариант</label>
          <input
            id="customCount"
            v-model.trim="customCount"
            class="input-field"
            type="number"
            inputmode="numeric"
            min="1"
            step="1"
            placeholder="Введите количество занятий"
            @input="selectOption('custom')"
          />
          <p class="input-hint">Только целое положительное число</p>
        </div>

        <div class="total-row">
          <span class="total-label">Итого</span>
          <span class="total-value">{{ totalAmount }} ₽</span>
        </div>

        <button
          type="button"
          class="pay-button"
          :disabled="!isValid"
          @click="handlePay"
        >
          Оплатить
        </button>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Footer from '../../components/Footer.vue'

const lessonPrice = 800
const selectedOption = ref(1)
const customCount = ref('')

const isCustomSelected = computed(() => selectedOption.value === 'custom')
const parsedCustomCount = computed(() => {
  const value = customCount.value.trim()
  if (!value) {
    return null
  }

  if (!/^\d+$/.test(value)) {
    return null
  }

  const parsed = Number.parseInt(value, 10)
  return parsed > 0 ? parsed : null
})

const lessonCount = computed(() => {
  if (isCustomSelected.value) {
    return parsedCustomCount.value
  }

  return selectedOption.value
})

const isValid = computed(() => lessonCount.value !== null && lessonCount.value > 0)

const totalAmount = computed(() => {
  if (!isValid.value) {
    return 0
  }

  return lessonCount.value * lessonPrice
})

function selectOption(option) {
  selectedOption.value = option
}

function handlePay() {
  if (!isValid.value) {
    return
  }

  // Заглушка до подключения Робокассы
}
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
  max-width: 880px;
  margin: 0 auto;
  padding: 48px 32px 32px;
  width: 100%;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 900;
  color: #FFFFFF;
  text-align: center;
  margin: 0 0 32px 0;
}

.card {
  background: rgba(36, 36, 36, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 28px;
}

.calculator-card {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.calculator-header {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.card-title {
  font-size: 1.4rem;
  font-weight: 800;
  margin: 0;
}

.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
}

.price-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.72);
}

.price-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: #FFD700;
}

.preset-options {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.preset-option {
  padding: 14px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.preset-option--active {
  border-color: #FFD700;
  background: rgba(255, 215, 0, 0.12);
  color: #FFD700;
}

.custom-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-label {
  font-weight: 700;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
}

.input-field {
  background: rgba(20, 20, 20, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 1rem;
  color: #FFFFFF;
  outline: none;
}

.input-field:focus {
  border-color: #FFD700;
}

.input-hint {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

.total-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.total-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

.total-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: #FFD700;
}

.pay-button {
  width: 100%;
  padding: 14px 16px;
  border-radius: 12px;
  border: none;
  background: #FFD700;
  color: #1A1A1A;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

.pay-button:hover:enabled {
  background: #FFC700;
  transform: translateY(-1px);
}

.pay-button:disabled {
  background: rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.6);
  cursor: not-allowed;
}

.pay-note {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
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
    padding: 40px 20px 24px;
  }

  .page-title {
    font-size: 1.5rem;
  }


  .preset-options {
    grid-template-columns: 1fr;
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
