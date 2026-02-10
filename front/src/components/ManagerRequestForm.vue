<!-- src/components/ManagerRequestForm.vue -->
<template>
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Обратиться к менеджеру</h2>
        <button class="close-btn" @click="closeModal">×</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="request-form">
        <div class="form-group">
          <label for="comment">Комментарий (необязательно)</label>
          <textarea
            id="comment"
            v-model="comment"
            rows="5"
            placeholder="Опишите ваш вопрос или проблему..."
            class="form-textarea"
          ></textarea>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="closeModal">
            Отмена
          </button>
          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? 'Отправка...' : 'Отправить запрос' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  onSubmit: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['close', 'success'])

const showModal = ref(props.show)
const comment = ref('')
const submitting = ref(false)
const error = ref(null)

watch(() => props.show, (newVal) => {
  showModal.value = newVal
  if (!newVal) {
    comment.value = ''
    error.value = null
  }
})

const closeModal = () => {
  showModal.value = false
  emit('close')
}

const handleSubmit = async () => {
  error.value = null
  submitting.value = true
  
  try {
    await props.onSubmit({ comment: comment.value })
    closeModal()
    emit('success')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Ошибка при отправке запроса'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: rgba(40, 40, 40, 0.95);
  border: 3px solid #FFD700;
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 2px solid rgba(255, 215, 0, 0.3);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #FFFFFF;
  font-weight: 700;
}

.close-btn {
  background: transparent;
  border: none;
  color: #FFFFFF;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: auto;
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  line-height: 1;
}

.close-btn:hover {
  color: #FFD700;
}

.request-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.95rem;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #FFD700;
  border-radius: 8px;
  background: rgba(50, 50, 50, 0.6);
  color: #FFFFFF;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #FFD700;
  background: rgba(60, 60, 60, 0.7);
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.2);
}

.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.error-message {
  padding: 12px;
  background: rgba(255, 68, 68, 0.2);
  border: 2px solid rgba(255, 68, 68, 0.6);
  border-radius: 8px;
  color: #ffaaaa;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-submit {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.btn-cancel {
  background: transparent;
  color: #FFFFFF;
  border: 1px solid #FFD700;
}

.btn-cancel:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: #FFD700;
}

.btn-submit {
  background: transparent;
  color: #FFFFFF;
  border: 1px solid #FFD700;
}

.btn-submit:hover:not(:disabled) {
  background: #FFD700;
  color: #1A1A1A;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Адаптивность */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 16px;
  }

  .modal-content {
    max-width: 100%;
    border-radius: 12px;
    border-width: 2px;
  }

  .modal-header {
    padding: 20px;
  }

  .modal-header h2 {
    font-size: 1.3rem;
  }

  .request-form {
    padding: 20px;
  }

  .form-actions {
    flex-direction: column;
    gap: 10px;
  }

  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 12px;
  }

  .modal-content {
    border-width: 2px;
  }

  .modal-header {
    padding: 16px;
  }

  .modal-header h2 {
    font-size: 1.2rem;
  }

  .request-form {
    padding: 16px;
  }

  .form-textarea {
    font-size: 0.9rem;
    padding: 10px;
    border-width: 2px;
  }
}
</style>



