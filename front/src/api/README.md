# API Client

## Базовая схема

```javascript
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})
```

- `baseURL` уже содержит `/api`
- авторизация теперь работает через `HttpOnly` cookie
- для `POST/PUT/PATCH/DELETE` клиент автоматически добавляет `X-CSRFToken`

## Правило путей

Используйте пути без префикса `/api`.

```javascript
apiClient.post('/auth/login/', data)
```

Нельзя:

```javascript
apiClient.post('/api/auth/login/', data)
```

## Текущее поведение auth

- `loginApi` и `registerApi` получают CSRF cookie и отправляют запрос с `withCredentials`
- `getMeApi` определяет текущую сессию пользователя
- refresh access-токена выполняется через cookie endpoint `/token/refresh/`
- фронт не хранит `access` и `refresh` в `localStorage`
