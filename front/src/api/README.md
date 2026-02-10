# API Client - Каноничная схема

## 🎯 Правила использования API

### 1. **Базовая конфигурация (http.js)**

```javascript
// baseURL настроен автоматически:
// DEV: http://127.0.0.1:8000/api
// PROD: /api (проксируется через Nginx)

const apiClient = axios.create({
  baseURL: API_BASE_URL,  // уже содержит /api
  withCredentials: false,
})
```

### 2. **ЗОЛОТОЕ ПРАВИЛО: Пути БЕЗ `/api`**

❌ **НЕПРАВИЛЬНО:**
```javascript
apiClient.post('/api/auth/login/', data)  // ❌ Будет /api/api/auth/login/
```

✅ **ПРАВИЛЬНО:**
```javascript
apiClient.post('/auth/login/', data)  // ✅ Будет /api/auth/login/
```

### 3. **Архитектура**

```
Компонент/Vue
    ↓
API функция (из src/api/*.js)
    ↓
apiClient (baseURL='/api')
    ↓
Финальный URL: /api/auth/login/
    ↓
Nginx (проксирует /api → gunicorn)
    ↓
Django
```

## 📁 Структура API файлов

### `auth.js` - Авторизация
- `loginApi({ email, password })` → POST `/auth/login/`
- `registerApi(payload)` → POST `/auth/register/`
- `getMeApi()` → GET `/auth/me/`
- `updateMeApi(payload)` → PATCH `/auth/me/`
- `adminLoginApi({ email, password })` → POST `/auth/admin-login/`

### `admin.js` - Админка
- `adminGetUsers(params)` → GET `/admin/users/`
- `adminGetCourses()` → GET `/admin/courses/`
- `adminGetAuditLogs(params)` → GET `/admin/audit/`
- ... и т.д. (все пути БЕЗ `/api`)

### `manager.js` - Менеджер
- `managerGetLessons(params)` → GET `/manager/lessons/`
- `managerGetClients(params)` → GET `/manager/clients/`
- ... и т.д.

### `teacher.js` - Учитель
- `teacherGetLessons(params)` → GET `/teacher/lessons/`
- `teacherGetStudents(params)` → GET `/teacher/students/`
- ... и т.д.

### `student.js` - Ученик
- `studentGetDashboard()` → GET `/student/dashboard/`
- `studentGetCourses()` → GET `/student/courses/`
- ... и т.д.

### `applicant.js` - Абитуриент
- `applicantGetBalance()` → GET `/applicant/balance/`
- `applicantGetPublicCourses()` → GET `/applicant/courses/public/`
- ... и т.д.

## ⚠️ Важно

1. **НЕ используйте прямой `apiClient` в компонентах** - всегда через API функции
2. **НЕ добавляйте `/api` в пути** - baseURL уже содержит его
3. **Все пути начинаются с `/`** - относительные пути от baseURL

## 🔍 Проверка ошибок

Если получаете **404** или **400**:

1. Проверьте, что путь начинается с `/` и НЕ содержит `/api`
2. Проверьте, что используете функцию из `src/api/*.js`, а не прямой `apiClient`
3. Проверьте Network в DevTools - финальный URL должен быть `/api/...` (один раз)

## 📝 Пример правильного использования

```javascript
// ✅ ПРАВИЛЬНО
import { loginApi } from '../api/auth'

const handleLogin = async () => {
  const result = await loginApi({ email, password })
}
```

```javascript
// ❌ НЕПРАВИЛЬНО
import apiClient from '../api/http'

const handleLogin = async () => {
  const result = await apiClient.post('/api/auth/login/', { email, password })
}
```
