<!-- src/pages/common/AboutServiceView.vue -->
<template>
  <div class="about-page">
    <main class="about-content">
      <section class="about-section">
        <h1 class="about-title">О сервисе</h1>

        <h2 class="about-subtitle">F.L.A.R.E. — персональный сервис учёта занятий</h2>
        <p class="about-text">
          F.L.A.R.E. — это сервис для сопровождения индивидуального обучения. Он фиксирует занятия, оплаченный баланс,
          историю уроков и обратную связь в одном личном кабинете.
        </p>
        <p class="about-text">
          Сервис создавался не как массовая онлайн‑школа, а как удобный инструмент для прозрачной и понятной работы
          с учениками и их родителями.
        </p>
      </section>

      <hr class="about-divider" />

      <section class="about-section">
        <h2 class="about-subtitle">Почему появился F.L.A.R.E.</h2>
        <p class="about-text">
          Идея сервиса появилась из практики индивидуального репетиторства. Когда занятия оплачиваются заранее,
          вести учёт вручную становится сложно: нужно помнить, сколько уроков уже прошло, сколько осталось на балансе,
          что было на занятии и какую обратную связь дать.
        </p>
        <p class="about-text">
          Со временем стало понятно, что без системы легко допустить ошибки и потерять прозрачность процесса.
          Поэтому был создан сервис, который берёт на себя учёт занятий и хранение всей информации о процессе обучения.
        </p>
      </section>

      <hr class="about-divider" />

      <section class="about-section">
        <h2 class="about-subtitle">Что отображается в личном кабинете</h2>
        <ul class="about-list">
          <li class="about-list-item">
            Вы регистрируетесь — создаётся личный кабинет.
          </li>
          <li class="about-list-item">
            В личном кабинете отображается вся информация о занятиях.
          </li>
          <li class="about-list-item">
            По мере обучения туда добавляются уроки, баланс и обратная связь.
          </li>
          <li class="about-list-item">
            Вся история совместной работы сохраняется и доступна в любое время.
          </li>
          <li class="about-list-item">
            Никаких дополнительных сервисов или сторонних таблиц — всё хранится в одном месте.
          </li>
        </ul>
      </section>

      <hr class="about-divider" />

      <section class="about-section">
        <h2 class="about-subtitle">Кому подходит F.L.A.R.E.</h2>
        <ul class="about-list">
          <li class="about-list-item">
            Родителям учеников, которые хотят видеть прогресс и понимать, как идёт обучение.
          </li>
          <li class="about-list-item">
            Тем, кто оплачивает занятия заранее и хочет понимать текущий баланс.
          </li>
          <li class="about-list-item">
            Тем, кому важно знать, что изучалось на занятиях и какая была обратная связь.
          </li>
          <li class="about-list-item">
            Ученикам, которым нужен понятный и структурированный формат обучения.
          </li>
        </ul>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Footer from '../../components/Footer.vue'
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
}

.about-content {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 80px 32px 40px;
  width: 100%;
}

.about-title {
  font-size: 2.6rem;
  font-weight: 900;
  margin: 0 0 40px 0;
  color: #FFFFFF;
}

.about-subtitle {
  font-size: 1.6rem;
  font-weight: 800;
  margin: 0 0 20px 0;
  color: #FFFFFF;
}

.about-text {
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.88);
  margin: 0 0 16px 0;
}

.about-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  margin: 40px 0;
}

.about-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.about-list-item {
  position: relative;
  padding-left: 26px;
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.9);
}

.about-list-item::before {
  content: '→';
  position: absolute;
  left: 0;
  top: 0;
  color: #FFD700;
}

@media (max-width: 768px) {
  .about-content {
    padding: 60px 20px 32px;
  }

  .about-title {
    font-size: 2.1rem;
    margin-bottom: 28px;
  }

  .about-subtitle {
    font-size: 1.4rem;
  }
}

@media (max-width: 480px) {
  .about-content {
    padding: 50px 16px 28px;
  }

  .about-title {
    font-size: 1.8rem;
  }

  .about-subtitle {
    font-size: 1.25rem;
  }
}
</style>

