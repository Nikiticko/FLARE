from django.conf import settings
from rest_framework.permissions import BasePermission


def is_root_admin(user):
    """
    Проверка встроенного (root) администратора через settings.ROOT_ADMIN_EMAIL.
    """
    root = getattr(settings, "ROOT_ADMIN_EMAIL", None)
    if not root:
        return False
    return user.email.lower() == root.lower()


class IsAdminRole(BasePermission):
    """
    Даёт доступ:
    - ROOT ADMIN (вшитый админ)
    - роль ADMIN
    - superuser Django
    """

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        if is_root_admin(u):
            return True

        if getattr(u, "role", None) == "ADMIN":
            return True

        if u.is_superuser:
            return True

        return False


class IsManagerOrAdmin(BasePermission):

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        if is_root_admin(u):
            return True

        role = getattr(u, "role", None)
        return bool(role in ("MANAGER", "ADMIN") or u.is_superuser)


class IsTeacherOrAdmin(BasePermission):

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        if is_root_admin(u):
            return True

        role = getattr(u, "role", None)
        return bool(role in ("TEACHER", "ADMIN") or u.is_superuser)


class IsApplicantOrAdmin(BasePermission):

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        if is_root_admin(u):
            return True

        role = getattr(u, "role", None)
        return bool(role in ("APPLICANT", "ADMIN") or u.is_superuser)


class IsStudentOrAdmin(BasePermission):

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        if is_root_admin(u):
            return True

        role = getattr(u, "role", None)
        return bool(role in ("STUDENT", "ADMIN") or u.is_superuser)


class IsStudentOrApplicantOrAdmin(BasePermission):
    """
    Даёт доступ STUDENT, APPLICANT и ADMIN.
    Используется для API, которые должны быть доступны и ученикам, и абитуриентам
    (например, просмотр своих занятий).
    """

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        if is_root_admin(u):
            return True

        role = getattr(u, "role", None)
        return bool(role in ("STUDENT", "APPLICANT", "ADMIN") or u.is_superuser)


class IsStudentOrApplicantOrTeacherOrManagerOrAdmin(BasePermission):
    """
    Даёт доступ STUDENT, APPLICANT, TEACHER, MANAGER и ADMIN.
    Используется для унифицированных API, доступных всем этим ролям.
    """

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        if is_root_admin(u):
            return True

        role = getattr(u, "role", None)
        return bool(role in ("STUDENT", "APPLICANT", "TEACHER", "MANAGER", "ADMIN") or u.is_superuser)
