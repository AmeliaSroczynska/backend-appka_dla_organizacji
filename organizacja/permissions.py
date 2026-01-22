from rest_framework import permissions


class CzyPrzewodniczacy(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.auth and request.auth.get('rola') == 'Przewodniczacy'


class CzySkarbnik(permissions.BasePermission):
    """Skarbnik lub Przewodniczący"""
    def has_permission(self, request, view):
        rola = request.auth.get('rola') if request.auth else None
        return rola in ['Skarbnik', 'Przewodniczacy']


class CzyKoordynator(permissions.BasePermission):
    """Koordynator lub Przewodniczący"""
    def has_permission(self, request, view):
        rola = request.auth.get('rola') if request.auth else None
        return rola in ['Koordynator', 'Przewodniczacy']


class CzyDowolnaRola(permissions.BasePermission):
    """Dostęp dla każdej z 3 ról (używane np. w Bazie Członków)"""
    def has_permission(self, request, view):
        rola = request.auth.get('rola') if request.auth else None
        return rola in ['Skarbnik', 'Przewodniczacy', 'Koordynator']


class UprawnieniaFinansowe(permissions.BasePermission):
    """
    Skarbnik i Przewodniczący: Pełny dostęp (W, T, E, U).
    Koordynator: Tylko odczyt (W).
    """
    def has_permission(self, request, view):
        rola = request.auth.get('rola') if request.auth else None
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return rola in ['Skarbnik', 'Przewodniczacy', 'Koordynator']
        return rola in ['Skarbnik', 'Przewodniczacy']