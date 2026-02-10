<!-- src/pages/common/AboutTeacherView.vue -->
<template>
  <div class="about-teacher-page">
    <main class="about-teacher-content">
      <!-- Шапка с фото и именем -->
      <section class="about-teacher-header">
        <h1 class="about-teacher-title">О преподавателе</h1>

        <div class="teacher-intro">
          <div class="teacher-photo-wrapper">
            <img src="/avatar.jpeg" alt="Семененко Никита" class="teacher-photo" />
          </div>
          <div class="teacher-main-info">
            <h2 class="teacher-name">Семененко Никита</h2>
            <p class="teacher-role">
              Преподаватель программирования и автор сервиса F.L.A.R.E.
            </p>
          </div>
        </div>
      </section>

      <hr class="about-teacher-divider" />

      <!-- Обо мне -->
      <section class="about-teacher-section">
        <h2 class="section-title">Обо мне</h2>
        <p class="section-text">
          Меня зовут Семененко Никита. Мне 20 лет, на данный момент я оканчиваю университет по направлению
          «Прикладная информатика».
        </p>
        <p class="section-text">
          Параллельно с обучением в университете я более года занимаюсь онлайн‑преподаванием программирования
          и продолжаю развиваться в этом направлении.
        </p>
      </section>

      <hr class="about-teacher-divider" />

      <!-- Опыт и формат работы -->
      <section class="about-teacher-section">
        <h2 class="section-title">Опыт и формат работы</h2>
        <p class="section-text">
          Я работаю с учениками на начальном уровне программирования.
        </p>
        <ul class="section-list">
          <li class="section-list-item">
            Основной возраст — от 10 до 16–17 лет.
          </li>
        </ul>
        <p class="section-text">
          Наиболее комфортно выстраивается работа с учениками 12–14 лет — в этом возрасте дети уже хорошо понимают
          материал, но при этом остаются открытыми к обучению и диалогу.
        </p>
        <p class="section-text">
          При необходимости я могу работать и с другими возрастными категориями — как с более младшими,
          так и со старшими учениками, если формат и задачи обучения подходят.
        </p>
      </section>

      <hr class="about-teacher-divider" />

      <!-- Подход к обучению -->
      <section class="about-teacher-section">
        <h2 class="section-title">Подход к обучению</h2>
        <p class="section-text">
          Для меня важно качество обучения и результат.
        </p>
        <ul class="section-list">
          <li class="section-list-item">
            Я не беру на себя задачи, в которых не уверен, и стараюсь работать только в тех случаях,
            где могу дать реальную пользу.
          </li>
          <li class="section-list-item">
            Перед началом обучения я провожу пробное занятие — на нём мы знакомимся, обсуждаем цели,
            уровень подготовки и формат работы.
          </li>
          <li class="section-list-item">
            По итогам пробного занятия я даю рекомендации и честную оценку ситуации, даже если мы не продолжаем
            обучение дальше.
          </li>
        </ul>
      </section>

      <hr class="about-teacher-divider" />

      <!-- Разработка и сервис F.L.A.R.E. -->
      <section class="about-teacher-section">
        <h2 class="section-title">Разработка и сервис F.L.A.R.E.</h2>
        <p class="section-text">
          Помимо преподавания, я занимаюсь разработкой и интересуюсь IT‑технологиями в целом. Сервис F.L.A.R.E.
          вырос из практического опыта преподавания и потребности в удобном и прозрачном учёте занятий.
        </p>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Footer from '../../components/Footer.vue'
</script>

<style scoped>
.about-teacher-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
}

.about-teacher-content {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 80px 32px 40px;
  width: 100%;
}

.about-teacher-header {
  margin-bottom: 32px;
}

.about-teacher-title {
  font-size: 2.6rem;
  font-weight: 900;
  margin: 0 0 32px 0;
  color: #FFFFFF;
}

.teacher-intro {
  display: flex;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}

.teacher-photo-wrapper {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  /* растушёванные края без чёткой обводки */
  box-shadow:
    0 0 28px rgba(0, 0, 0, 0.45),
    0 0 56px rgba(255, 215, 0, 0.08),
    0 0 80px rgba(0, 0, 0, 0.25);
  transition: transform 0.35s ease, box-shadow 0.35s ease;
}

.teacher-photo-wrapper:hover {
  transform: scale(1.3);
  box-shadow:
    0 0 36px rgba(0, 0, 0, 0.4),
    0 0 72px rgba(255, 215, 0, 0.12),
    0 0 100px rgba(0, 0, 0, 0.2);
}

.teacher-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.teacher-main-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.teacher-name {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0;
  color: #FFFFFF;
}

.teacher-role {
  margin: 0;
  font-size: 0.98rem;
  color: #FFD700;
}

.about-teacher-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  margin: 36px 0;
}

.about-teacher-section {
  margin-bottom: 8px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0 0 20px 0;
  color: #FFFFFF;
}

.section-text {
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 14px 0;
}

.section-list {
  list-style: none;
  margin: 0 0 12px 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-list-item {
  position: relative;
  padding-left: 26px;
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.9);
}

.section-list-item::before {
  content: '→';
  position: absolute;
  left: 0;
  top: 0;
  color: #FFD700;
}

@media (max-width: 768px) {
  .about-teacher-content {
    padding: 60px 20px 32px;
  }

  .about-teacher-title {
    font-size: 2.1rem;
    margin-bottom: 24px;
  }

  .teacher-name {
    font-size: 1.6rem;
  }

  .section-title {
    font-size: 1.35rem;
  }
}

@media (max-width: 480px) {
  .about-teacher-content {
    padding: 50px 16px 28px;
  }

  .about-teacher-title {
    font-size: 1.9rem;
  }

  .teacher-intro {
    align-items: flex-start;
  }
}
</style>

