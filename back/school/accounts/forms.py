# accounts/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.conf import settings

from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text='Минимум 8 символов'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'student_full_name',
            'parent_full_name',
        ]

        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'your@mail.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7...'}),
            'student_full_name': forms.TextInput(attrs={'placeholder': 'ФИО ученика'}),
            'parent_full_name': forms.TextInput(attrs={'placeholder': 'ФИО родителя'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if len(pwd) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов')
        return pwd

    def save(self, commit=True):
        data = self.cleaned_data
        user = User(
            email=data['email'],
            phone=data.get('phone', ''),
            student_full_name=data.get('student_full_name', ''),
            parent_full_name=data.get('parent_full_name', ''),
            role=User.Roles.APPLICANT,  # по умолчанию абитуриент
        )
        user.username = user.email  # логинимся по email
        user.set_password(data['password'])

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email', '').lower().strip()
        password = cleaned.get('password')

        if email and password:
            # аутентифицируем через username=email
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError('Неверный email или пароль.')
            self.user = user
        return cleaned

    def get_user(self):
        return getattr(self, 'user', None)


class AdminLoginForm(forms.Form):
    email = forms.EmailField(label='Email (только для вшитых админов)')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if email not in getattr(settings, 'ADMIN_SEED_EMAILS', []):
            raise forms.ValidationError('Этот email не разрешён для админ-входа.')
        return email

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            # Допускаем вход и для ещё не созданного пользователя из белого списка:
            # если нет — создадим в view при успешной проверке.
            # Здесь просто запоминаем введённые данные.
            self._email = email
            self._password = password
        return cleaned

    def get_credentials(self):
        return getattr(self, '_email', None), getattr(self, '_password', None)
