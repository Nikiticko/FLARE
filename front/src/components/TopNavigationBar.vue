<!-- src/components/TopNavigationBar.vue -->
<template>
  <header class="top-navigation-bar">
    <!-- Левая часть - Название школы -->
    <div class="nav-left">
      <router-link :to="{ name: 'home' }" class="school-logo">
        <span class="logo-text">F.L.A.R.E.</span>
      </router-link>
    </div>

    <!-- Правая часть -->
    <div class="nav-right">
      <template v-if="auth.isAuthenticated && auth.user">
        <!-- Кнопка администрирования (для admin, manager и teacher) -->
        <div v-if="hasAdminAccess || isTeacher" class="admin-section">
          <button 
            class="admin-toggle-btn" 
            @click="toggleAdminMenu"
            :class="{ 'active': showAdminMenu }"
          >
            <span class="admin-icon">⚙️</span>
            <span class="admin-text">Администрирование</span>
            <span class="admin-arrow" :class="{ 'rotated': showAdminMenu }">▼</span>
          </button>

          <!-- Выпадающее меню администрирования -->
          <transition name="fade-slide">
            <div v-if="showAdminMenu" class="admin-dropdown" @click.stop>
              <template v-if="isAdmin">
                <router-link :to="{ name: 'admin-dashboard' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">👥</span>
                  <span>Управление пользователями</span>
                </router-link>
                <router-link :to="{ name: 'admin-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">📅</span>
                  <span>Расписание</span>
                </router-link>
                <router-link :to="{ name: 'admin-courses' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">📚</span>
                  <span>Курсы</span>
                </router-link>
                <router-link :to="{ name: 'admin-logs' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">📋</span>
                  <span>Логи</span>
                </router-link>
              </template>
              <template v-else-if="isManager">
                <router-link :to="{ name: 'manager-balance' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">💰</span>
                  <span>Управление балансами</span>
                </router-link>
                <router-link :to="{ name: 'manager-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">📅</span>
                  <span>Календарь занятий</span>
                </router-link>
                <router-link :to="{ name: 'manager-requests' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">💬</span>
                  <span>Сообщения клиентов</span>
                </router-link>
              </template>
              <template v-else-if="isTeacher">
                <router-link :to="{ name: 'teacher-students' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">👥</span>
                  <span>Список учеников</span>
                </router-link>
                <router-link :to="{ name: 'teacher-schedule' }" class="dropdown-item" @click="closeAdminMenu">
                  <span class="item-icon">📅</span>
                  <span>Расписание занятий</span>
                </router-link>
              </template>
            </div>
          </transition>
        </div>

        <!-- Кнопка с email -->
        <div class="role-section">
          <button 
            class="role-toggle-btn" 
            @click="toggleUserMenu"
            :class="{ 'active': showUserMenu }"
          >
            <span class="role-text">{{ auth.user.email }}</span>
            <span class="role-arrow" :class="{ 'rotated': showUserMenu }">▼</span>
          </button>

          <!-- Выпадающее меню пользователя -->
          <transition name="fade-slide">
            <div v-if="showUserMenu" class="user-dropdown" @click.stop>
              <div class="dropdown-item user-info">
                <div class="user-info-email">{{ auth.user.email }}</div>
                <div class="user-info-role">{{ roleDisplayName }}</div>
              </div>
              <div class="dropdown-divider"></div>
              <router-link 
                v-if="isStudent || isApplicant || isTeacher || isManager || isAdmin" 
                :to="{ name: 'dashboard' }" 
                class="dropdown-item" 
                @click="closeUserMenu"
              >
                <span class="item-icon">📊</span>
                <span>Личный кабинет</span>
              </router-link>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout-item" @click="handleLogout">
                <span class="item-icon">🚪</span>
                <span>Выйти</span>
              </button>
            </div>
          </transition>
        </div>
      </template>
      <template v-else>
        <!-- Кнопки входа и регистрации -->
        <div class="auth-buttons">
          <router-link :to="{ name: 'login' }" class="auth-btn login-btn">
            Войти
          </router-link>
          <router-link :to="{ name: 'register' }" class="auth-btn register-btn">
            Зарегистрироваться
          </router-link>
        </div>
      </template>
    </div>

    <!-- Overlay для закрытия меню при клике вне его -->
    <transition name="fade">
      <div 
        v-if="showAdminMenu || showUserMenu" 
        class="menu-overlay" 
        @click="closeAllMenus"
      ></div>
    </transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const showAdminMenu = ref(false)
const showUserMenu = ref(false)

const normalizedRole = computed(() => auth.normalizedRole)
const isAdmin = computed(() => normalizedRole.value === 'admin')
const isManager = computed(() => normalizedRole.value === 'manager')
const isTeacher = computed(() => normalizedRole.value === 'teacher')
const isStudent = computed(() => normalizedRole.value === 'student')
const isApplicant = computed(() => normalizedRole.value === 'applicant')

const hasAdminAccess = computed(() => isAdmin.value || isManager.value)

const canEditProfile = computed(() => isApplicant.value || isStudent.value || isTeacher.value || isManager.value || isAdmin.value)

const roleDisplayName = computed(() => {
  const roleNames = {
    admin: 'ADMIN',
    manager: 'MANAGER',
    teacher: 'УЧИТЕЛЬ',
    student: 'УЧЕНИК',
    applicant: 'АБИТУРИЕНТ'
  }
  return roleNames[normalizedRole.value] || 'ПОЛЬЗОВАТЕЛЬ'
})

const toggleAdminMenu = () => {
  showAdminMenu.value = !showAdminMenu.value
  showUserMenu.value = false
}

const closeAdminMenu = () => {
  showAdminMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showAdminMenu.value = false
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const closeAllMenus = () => {
  showAdminMenu.value = false
  showUserMenu.value = false
}

const handleLogout = () => {
  closeAllMenus()
  auth.logout()
  router.push({ name: 'home' })
}

// Закрытие меню при клике вне области или при переходе на другую страницу
const handleClickOutside = (event) => {
  if (!event.target.closest('.admin-section') && !event.target.closest('.role-section')) {
    closeAllMenus()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.top-navigation-bar {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #222222;
  border-bottom: 2px solid #FFD700;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 64px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: visible;
  position: relative;
}

.nav-left {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  flex-shrink: 0;
  z-index: 1002;
  max-width: calc(100% - 200px);
  overflow: hidden;
}

@media (max-width: 1024px) {
  .nav-left {
    max-width: calc(100% - 180px);
  }
}

@media (max-width: 768px) {
  .nav-left {
    max-width: calc(100% - 140px);
  }
}

@media (max-width: 640px) {
  .nav-left {
    max-width: calc(100% - 120px);
  }
}

@media (max-width: 480px) {
  .nav-left {
    max-width: calc(100% - 100px);
  }
}

@media (max-width: 360px) {
  .nav-left {
    max-width: calc(100% - 90px);
  }
}

.school-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #FFFFFF;
  font-weight: 900;
  font-size: 1.5rem;
  transition: all 0.3s ease;
  padding: 8px 12px;
  letter-spacing: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.school-logo:hover {
  color: #FFD700;
}

.logo-text {
  letter-spacing: 2px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 1;
  min-width: 0;
  justify-content: flex-end;
  margin-left: auto;
  flex-wrap: nowrap;
  overflow: visible;
}


/* Кнопка администрирования */
.admin-section {
  position: relative;
  flex-shrink: 0;
}

.admin-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #222222;
  border: 1px solid #FFD700;
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-sizing: border-box;
}

.admin-toggle-btn:hover {
  background: rgba(255, 215, 0, 0.1);
}

.admin-toggle-btn.active {
  background: rgba(255, 215, 0, 0.15);
}

.admin-icon {
  font-size: 1.1rem;
  color: #9370DB;
}

.admin-text {
  color: #FFFFFF;
}

.admin-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s ease;
  color: #FFFFFF;
}

.admin-arrow.rotated {
  transform: rotate(180deg);
}

/* Выпадающее меню администрирования */
.admin-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  max-width: calc(100vw - 48px);
  background: rgba(40, 40, 40, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 1001;
  box-sizing: border-box;
  overflow: hidden;
}

@media (max-width: 768px) {
  .admin-dropdown {
    right: auto;
    left: 0;
    transform: translateX(0);
  }
}

@media (max-width: 480px) {
  .admin-dropdown {
    right: 0;
    left: auto;
    max-width: calc(100vw - 24px);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: rgba(255, 215, 0, 0.15);
  color: #FFD700;
}

.item-icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

/* Кнопка оплаты */
.payment-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #222222;
  border: 1px solid #FFD700;
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-sizing: border-box;
  flex-shrink: 0;
}

.payment-btn:hover {
  background: rgba(255, 215, 0, 0.1);
  color: #FFD700;
}

.payment-icon {
  font-size: 1.1rem;
}

.payment-text {
  color: #FFFFFF;
}

/* Кнопка роли */
.role-section {
  position: relative;
  flex-shrink: 0;
}

.role-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #FFD700;
  border: 1px solid #FFD700;
  border-radius: 8px;
  color: #1A1A1A;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-sizing: border-box;
  max-width: 250px;
  overflow: hidden;
}

.role-toggle-btn:hover {
  background: #FF8C00;
  border-color: #FF8C00;
}

.role-toggle-btn.active {
  background: #FF8C00;
  border-color: #FF8C00;
}

.role-text {
  color: #1A1A1A;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.role-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s ease;
  color: #1A1A1A;
}

.role-arrow.rotated {
  transform: rotate(180deg);
}

/* Выпадающее меню пользователя */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 240px;
  max-width: calc(100vw - 48px);
  background: rgba(40, 40, 40, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 1001;
  box-sizing: border-box;
  overflow: hidden;
}

@media (max-width: 768px) {
  .user-dropdown {
    right: 0;
    left: auto;
  }
}

@media (max-width: 480px) {
  .user-dropdown {
    right: 0;
    max-width: calc(100vw - 24px);
  }
}

.user-info {
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 12px 16px;
  cursor: default;
}

.user-info:hover {
  background: transparent;
}

.user-info-email {
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.user-info-role {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  font-weight: 500;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 8px 0;
}

.logout-item {
  color: rgba(255, 255, 255, 0.8);
}

.logout-item:hover {
  background: rgba(255, 68, 68, 0.2);
  color: #ffaaaa;
}

/* Кнопки входа и регистрации */
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.auth-btn {
  padding: 8px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  white-space: nowrap;
  box-sizing: border-box;
  flex-shrink: 0;
}

.login-btn {
  color: #FFD700;
  background: transparent;
  border-color: #FFD700;
}

.login-btn:hover {
  background: rgba(255, 215, 0, 0.1);
  color: #FF8C00;
  border-color: #FF8C00;
}

.register-btn {
  color: #1A1A1A;
  background: #FFD700;
  border-color: #FFD700;
}

.register-btn:hover {
  background: #FF8C00;
  border-color: #FF8C00;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
}

/* Overlay */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: transparent;
}

/* Анимации */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Адаптивность */

/* Планшеты и средние экраны */
@media (max-width: 1024px) {
  .top-navigation-bar {
    padding: 10px 20px;
    gap: 16px;
  }

  .nav-left {
    left: 20px;
  }

  .school-logo {
    font-size: 1.3rem;
  }

  .role-text {
    max-width: 150px;
  }
}

/* Планшеты (портретная ориентация) */
@media (max-width: 768px) {
  .top-navigation-bar {
    padding: 10px 16px;
    gap: 12px;
    min-height: 60px;
  }

  .nav-left {
    left: 16px;
  }

  .school-logo {
    font-size: 1.2rem;
    padding: 6px 10px;
  }

  .logo-text {
    font-size: 1.1rem;
    letter-spacing: 1px;
  }

  .admin-toggle-btn {
    padding: 7px 14px;
    font-size: 0.85rem;
  }

  .admin-text {
    display: none;
  }

  .role-toggle-btn {
    max-width: 180px;
  }

  .role-text {
    max-width: 120px;
    font-size: 0.8rem;
  }

  .payment-btn {
    padding: 7px 14px;
    font-size: 0.85rem;
  }

  .payment-text {
    display: none;
  }

  .role-toggle-btn {
    padding: 7px 14px;
    font-size: 0.85rem;
  }

  .auth-buttons {
    gap: 8px;
  }

  .auth-btn {
    padding: 7px 14px;
    font-size: 0.85rem;
  }

  .admin-dropdown,
  .user-dropdown {
    right: 0;
    max-width: calc(100vw - 32px);
    min-width: 200px;
  }

  .nav-right {
    gap: 10px;
  }
}

/* Мобильные устройства (большие) */
@media (max-width: 640px) {
  .top-navigation-bar {
    padding: 8px 14px;
    gap: 10px;
    min-height: 56px;
  }

  .nav-left {
    left: 14px;
  }

  .school-logo {
    font-size: 1.1rem;
    padding: 5px 8px;
  }

  .logo-text {
    font-size: 1rem;
    letter-spacing: 0.5px;
  }

  .admin-toggle-btn,
  .payment-btn,
  .role-toggle-btn {
    padding: 6px 12px;
    font-size: 0.8rem;
    gap: 6px;
  }

  .admin-icon {
    font-size: 1rem;
  }

  .payment-icon {
    font-size: 1rem;
  }

  .payment-text {
    display: none;
  }

  .role-toggle-btn {
    max-width: 150px;
  }

  .role-text {
    font-size: 0.8rem;
    max-width: 100px;
  }

  .auth-btn {
    padding: 6px 12px;
    font-size: 0.8rem;
  }

  .admin-dropdown,
  .user-dropdown {
    right: 0;
    max-width: calc(100vw - 28px);
    min-width: 180px;
    padding: 6px;
  }

  .dropdown-item {
    padding: 10px 12px;
    font-size: 0.85rem;
    gap: 10px;
  }

  .item-icon {
    font-size: 1rem;
    width: 18px;
  }

  .nav-right {
    gap: 8px;
  }
}

/* Мобильные устройства (малые) */
@media (max-width: 480px) {
  .top-navigation-bar {
    padding: 8px 12px;
    gap: 8px;
    min-height: 52px;
  }

  .nav-left {
    left: 12px;
  }

  .school-logo {
    font-size: 1rem;
    padding: 4px 6px;
  }

  .logo-text {
    font-size: 0.95rem;
    letter-spacing: 0;
  }

  .admin-toggle-btn,
  .payment-btn,
  .role-toggle-btn {
    padding: 5px 10px;
    font-size: 0.75rem;
    gap: 5px;
  }

  .admin-icon {
    font-size: 0.95rem;
  }

  .payment-icon {
    font-size: 0.95rem;
  }

  .payment-text {
    display: none;
  }

  .admin-arrow,
  .role-arrow {
    font-size: 0.6rem;
  }

  .role-toggle-btn {
    max-width: 120px;
  }

  .role-text {
    font-size: 0.75rem;
    max-width: 80px;
  }

  .auth-buttons {
    gap: 6px;
  }

  .auth-btn {
    padding: 5px 10px;
    font-size: 0.75rem;
  }

  .admin-dropdown,
  .user-dropdown {
    right: 0;
    max-width: calc(100vw - 24px);
    min-width: 160px;
    padding: 5px;
    top: calc(100% + 6px);
  }

  .dropdown-item {
    padding: 8px 10px;
    font-size: 0.8rem;
    gap: 8px;
  }

  .item-icon {
    font-size: 0.95rem;
    width: 16px;
  }

  .user-info {
    padding: 10px 12px;
  }

  .user-info-email {
    font-size: 0.85rem;
  }

  .user-info-role {
    font-size: 0.75rem;
  }

  .nav-right {
    gap: 6px;
  }
}

/* Очень маленькие экраны */
@media (max-width: 360px) {
  .top-navigation-bar {
    padding: 6px 10px;
    gap: 6px;
    min-height: 48px;
  }

  .nav-left {
    left: 10px;
  }

  .school-logo {
    font-size: 0.9rem;
    padding: 3px 5px;
  }

  .logo-text {
    font-size: 0.85rem;
  }

  .admin-toggle-btn,
  .payment-btn,
  .role-toggle-btn {
    padding: 4px 8px;
    font-size: 0.7rem;
    gap: 4px;
  }

  .admin-icon {
    font-size: 0.9rem;
  }

  .payment-icon {
    font-size: 0.9rem;
  }

  .payment-text {
    display: none;
  }

  .role-toggle-btn {
    max-width: 100px;
  }

  .role-text {
    font-size: 0.7rem;
    max-width: 60px;
  }

  .auth-btn {
    padding: 4px 8px;
    font-size: 0.7rem;
  }

  .admin-dropdown,
  .user-dropdown {
    max-width: calc(100vw - 20px);
    min-width: 140px;
  }

  .dropdown-item {
    padding: 6px 8px;
    font-size: 0.75rem;
  }

  .nav-right {
    gap: 4px;
  }
}

/* Горизонтальная ориентация на мобильных */
@media (max-width: 768px) and (orientation: landscape) {
  .top-navigation-bar {
    min-height: 50px;
    padding: 6px 16px;
  }

  .school-logo {
    font-size: 1.1rem;
  }

  .admin-toggle-btn,
  .payment-btn,
  .role-toggle-btn {
    padding: 5px 12px;
  }
}

/* Очень большие экраны */
@media (min-width: 1920px) {
  .top-navigation-bar {
    padding: 14px 32px;
    max-width: 1920px;
    margin: 0 auto;
  }

  .nav-left {
    left: 32px;
  }

  .school-logo {
    font-size: 1.6rem;
  }
}
</style>
