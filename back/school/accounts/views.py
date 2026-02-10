# accounts/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import get_user_model

from .forms import RegistrationForm, LoginForm, AdminLoginForm

User = get_user_model()

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация успешна. Теперь войдите в систему.')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:login')  # можно перекинуть на дашборд

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли.')
            return redirect('accounts:login')  # смените на нужную страницу после входа
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def admin_login_view(request):
    """
    Спец-вход для первых двух админов.
    Разрешены только email'ы из settings.ADMIN_SEED_EMAILS.
    Если пользователь с таким email ещё не создан — создаём с ролью ADMIN и суперправами.
    Допускаем только первых ДВОИХ (суперпользователей) из белого списка.
    """
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email, password = form.get_credentials()

            # Пытаемся найти пользователя
            user = User.objects.filter(email=email).first()

            # Подсчёт уже существующих суперпользователей из белого списка
            whitelist = getattr(settings, 'ADMIN_SEED_EMAILS', [])
            current_whitelist_superusers = User.objects.filter(
                email__in=whitelist, is_superuser=True
            ).count()

            # Если пользователя ещё нет — создаём и назначаем ADMIN (но только если ещё есть "слоты")
            if user is None:
                if current_whitelist_superusers >= 2:
                    form.add_error(None, 'Лимит админов из белого списка исчерпан.')
                    return render(request, 'accounts/admin_login.html', {'form': form})

                # Создаём заготовку (требуется валидный пароль для входа)
                user = User.objects.create_user(
                    email=email,
                    username=email,
                    password=password,
                    role=User.Roles.ADMIN,
                    is_staff=True,
                    is_superuser=True,
                )
            else:
                # Если пользователь есть — проверяем пароль
                user_auth = authenticate(username=email, password=password)
                if not user_auth:
                    form.add_error(None, 'Неверный пароль.')
                    return render(request, 'accounts/admin_login.html', {'form': form})

                # Если он из белого списка и ещё есть лимит — повышаем при необходимости
                if user.email in whitelist and not user.is_superuser:
                    if current_whitelist_superusers >= 2:
                        form.add_error(None, 'Лимит админов из белого списка исчерпан.')
                        return render(request, 'accounts/admin_login.html', {'form': form})
                    user.is_superuser = True
                    user.is_staff = True
                    user.role = User.Roles.ADMIN
                    user.save()

            # Авторизуем
            login(request, user)
            messages.success(request, 'Админ-вход выполнен.')
            return redirect('accounts:login')  # направьте на админ-панель/дашборд
    else:
        form = AdminLoginForm()

    return render(request, 'accounts/admin_login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('accounts:login')
