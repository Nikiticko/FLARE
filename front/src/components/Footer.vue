<!-- src/components/Footer.vue -->
<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-column">
        <h4 class="footer-column-title">О сервисе</h4>
        <ul class="footer-links">
          <li>
            <RouterLink :to="{ name: 'about-service' }" class="footer-link">
              О сервисе
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'payment-calculator' }" class="footer-link">
              Оплата занятий
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'about-teacher' }" class="footer-link">
              О преподавателе
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'public-offer' }" class="footer-link">
              Договор публичной оферты
            </RouterLink>
          </li>
        </ul>
      </div>
      <div class="footer-column">
        <h4 class="footer-column-title">Контакты</h4>
        <ul class="footer-links">
          <li>
            <a href="https://t.me/nikiticko" class="footer-link">
              Telegram
            </a>
          </li>
          
        </ul>
      </div>
      <div class="footer-column">
        <h4 class="footer-column-title">F.L.A.R.E.</h4>
        <p class="footer-description">
          Создан для удобства клиентов с любовью ❤️
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.footer {
  background: rgba(20, 20, 20, 0.95);
  padding: 60px 32px 30px;
  margin-top: 60px;
  box-sizing: border-box;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  box-sizing: border-box;
}

.footer-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.footer-column-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
}

.footer-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-link:hover {
  color: #FFD700;
}

.footer-link-icon {
  font-size: 1rem;
}

.footer-description {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
  padding: 0;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .footer-content {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .footer {
    padding: 50px 20px 25px;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }
}

@media (max-width: 480px) {
  .footer {
    padding: 40px 16px 20px;
  }
}
</style>