<template>
  <div class="cookie-page">
    <main class="cookie-content">
      <section class="cookie-section">
        <h1 class="cookie-title">Политика cookie</h1>
        <div class="cookie-document">
          <p class="cookie-paragraph">
            Настоящая политика объясняет, какие cookie и аналогичные технические данные
            используются на сайте F.L.A.R.E., для каких целей они применяются и как пользователь
            может управлять соответствующими настройками.
          </p>

          <h2 class="cookie-section-title">1. Какие cookie используются</h2>
          <p class="cookie-paragraph">
            На сайте используются обязательные cookie, необходимые для корректной авторизации,
            защиты запросов, поддержания сессии пользователя и безопасной работы личного кабинета.
          </p>
          <p class="cookie-paragraph">
            К таким cookie относятся cookie авторизации и cookie CSRF-защиты, без которых невозможно
            безопасно выполнить вход, изменить профиль, оплатить занятия или использовать защищенные
            разделы сайта.
          </p>

          <h2 class="cookie-section-title">2. Цели использования</h2>
          <p class="cookie-paragraph">
            Cookie применяются для технического функционирования сайта: идентификации авторизованного
            пользователя, предотвращения несанкционированных действий, сохранения активной сессии
            и обеспечения корректной работы API.
          </p>

          <h2 class="cookie-section-title">3. Срок хранения</h2>
          <p class="cookie-paragraph">
            Часть cookie действует только в течение активной сессии, другая часть хранится ограниченный
            период времени, необходимый для поддержки входа пользователя и безопасного обновления сессии.
          </p>

          <h2 class="cookie-section-title">4. Управление cookie</h2>
          <p class="cookie-paragraph">
            Пользователь может удалить cookie в настройках браузера или запретить их сохранение.
            При этом отключение обязательных cookie приведет к недоступности входа в личный кабинет
            и связанных с ним функций сайта.
          </p>

          <h2 class="cookie-section-title">5. Контакты</h2>
          <p class="cookie-paragraph">
            По вопросам обработки данных и использования cookie можно связаться с владельцем сервиса
            по адресу: nikitasemenenko3@gmail.com.
          </p>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Footer from '../../components/Footer.vue'
</script>

<style scoped>
.cookie-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1A1A1A;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  color: #FFFFFF;
}

.cookie-content {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 80px 32px 40px;
  width: 100%;
}

.cookie-title {
  font-size: 2.6rem;
  font-weight: 900;
  margin: 0 0 24px 0;
  color: #FFFFFF;
}

.cookie-document {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.cookie-section-title {
  font-size: 1.35rem;
  font-weight: 800;
  margin: 20px 0 6px 0;
  color: #FFFFFF;
}

.cookie-paragraph {
  font-size: 1rem;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.88);
  margin: 0;
}

@media (max-width: 768px) {
  .cookie-content {
    padding: 60px 20px 32px;
  }

  .cookie-title {
    font-size: 2.1rem;
  }
}

@media (max-width: 480px) {
  .cookie-content {
    padding: 50px 16px 28px;
  }

  .cookie-title {
    font-size: 1.8rem;
  }

  .cookie-section-title {
    font-size: 1.12rem;
  }
}
</style>
