// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../pages/auth/LoginView.vue'
import RegisterView from '../pages/auth/RegisterView.vue'
import LandingPage from '../pages/common/LandingPage.vue'
import EditProfileView from '../pages/common/EditProfileView.vue'
import DashboardView from '../pages/common/DashboardView.vue'
import AdminDashboardView from '../pages/admin/AdminDashboardView.vue'
import AdminScheduleView from '../pages/admin/AdminScheduleView.vue'
import AdminLogsView from '../pages/admin/AdminLogsView.vue'
import AdminCoursesView from '../pages/admin/AdminCoursesView.vue'
import ManagerScheduleView from '../pages/manager/ManagerScheduleView.vue'
import ManagerBalanceView from '../pages/manager/ManagerBalanceView.vue'
import ManagerRequestsView from '../pages/manager/ManagerRequestsView.vue'
import TeacherStudentsView from '../pages/teacher/TeacherStudentsView.vue'
import TeacherScheduleView from '../pages/teacher/TeacherScheduleView.vue'
import PaymentCalculatorView from '../pages/common/PaymentCalculatorView.vue'
import AboutServiceView from '../pages/common/AboutServiceView.vue'
import AboutTeacherView from '../pages/common/AboutTeacherView.vue'
import PublicOfferView from '../pages/common/PublicOfferView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: LandingPage,
    meta: { guestOnly: false },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guestOnly: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, roles: ['applicant', 'student', 'teacher', 'manager', 'admin'] },
  },
  {
    path: '/applicant',
    name: 'applicant-dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, roles: ['applicant'] },
  },
  {
    path: '/student',
    name: 'student-dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
  {
    path: '/edit-profile',
    name: 'edit-profile',
    component: EditProfileView,
    meta: { requiresAuth: true, roles: ['applicant', 'student', 'teacher', 'manager', 'admin'] },
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/schedule',
    name: 'admin-schedule',
    component: AdminScheduleView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/logs',
    name: 'admin-logs',
    component: AdminLogsView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/courses',
    name: 'admin-courses',
    component: AdminCoursesView,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/manager/schedule',
    name: 'manager-schedule',
    component: ManagerScheduleView,
    meta: { requiresAuth: true, roles: ['manager'] },
  },
  {
    path: '/manager/balance/:studentId?',
    name: 'manager-balance',
    component: ManagerBalanceView,
    meta: { requiresAuth: true, roles: ['manager'] },
  },
  {
    path: '/manager/requests',
    name: 'manager-requests',
    component: ManagerRequestsView,
    meta: { requiresAuth: true, roles: ['manager'] },
  },
  {
    path: '/teacher/students',
    name: 'teacher-students',
    component: TeacherStudentsView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/teacher/schedule',
    name: 'teacher-schedule',
    component: TeacherScheduleView,
    meta: { requiresAuth: true, roles: ['teacher'] },
  },
  {
    path: '/student',
    name: 'student-dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, roles: ['student'] },
  },
  {
    path: '/payment',
    name: 'payment-calculator',
    component: PaymentCalculatorView,
    meta: { guestOnly: false },
  },
  {
    path: '/about',
    name: 'about-service',
    component: AboutServiceView,
    meta: { guestOnly: false },
  },
  {
    path: '/teacher',
    name: 'about-teacher',
    component: AboutTeacherView,
    meta: { guestOnly: false },
  },
  {
    path: '/public-offer',
    name: 'public-offer',
    component: PublicOfferView,
    meta: { guestOnly: false },
  },
  // Catch-all маршрут для 404 - перенаправляет на главную
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    redirect: { name: 'home' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Названия страниц для title
const pageTitles = {
  'home': 'F.L.A.R.E. — Главная',
  'about-service': 'О сервисе — F.L.A.R.E.',
  'about-teacher': 'О преподавателе — F.L.A.R.E.',
  'login': 'Вход — F.L.A.R.E.',
  'register': 'Регистрация — F.L.A.R.E.',
  'dashboard': 'Личный кабинет — F.L.A.R.E.',
  'applicant-dashboard': 'Личный кабинет — F.L.A.R.E.',
  'student-dashboard': 'Личный кабинет — F.L.A.R.E.',
  'edit-profile': 'Редактирование профиля — F.L.A.R.E.',
  'admin-dashboard': 'Панель администратора — F.L.A.R.E.',
  'admin-schedule': 'Расписание — Админ — F.L.A.R.E.',
  'admin-logs': 'Логи — Админ — F.L.A.R.E.',
  'admin-courses': 'Курсы — Админ — F.L.A.R.E.',
  'manager-schedule': 'Расписание — Менеджер — F.L.A.R.E.',
  'manager-balance': 'Балансы — Менеджер — F.L.A.R.E.',
  'manager-requests': 'Запросы — Менеджер — F.L.A.R.E.',
  'teacher-students': 'Ученики — Учитель — F.L.A.R.E.',
  'teacher-schedule': 'Расписание — Учитель — F.L.A.R.E.',
  'payment-calculator': 'Калькулятор оплаты — F.L.A.R.E.',
  'public-offer': 'Договор публичной оферты — F.L.A.R.E.',
}

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // страница только для гостей (login/register)
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return next({ name: 'home' })
  }

  // требуется авторизация
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Если требуется авторизация и есть токен, но пользователь еще не загружен
  // дожидаемся загрузки пользователя перед проверкой роли
  if (to.meta.requiresAuth && auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchMe()
    } catch (err) {
      // Если не удалось загрузить пользователя, редиректим на логин
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
  }

  // ограничение по ролям
  if (to.meta.roles && to.meta.roles.length > 0) {
    const role = auth.normalizedRole
    const allowed = to.meta.roles.map((r) => r.toLowerCase())
    if (!allowed.includes((role || '').toLowerCase())) {
      return next({ name: 'home' })
    }
  }

  return next()
})

// Обновление title при переходе на страницу
router.afterEach((to) => {
  const title = pageTitles[to.name] || 'F.L.A.R.E.'
  document.title = title
  
  // Обновление favicon (можно менять для разных страниц, но пока оставим один)
  let favicon = document.querySelector("link[rel='icon']")
  if (!favicon) {
    favicon = document.createElement('link')
    favicon.rel = 'icon'
    favicon.type = 'image/png'
    document.head.appendChild(favicon)
  }
  favicon.href = '/logo.png'
})

export default router
