from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListaCzlonkowViewSet, CzlonekCRUDViewSet, CzlonekKierunekViewSet, SekcjaViewSet, KierunekViewSet, \
    CzlonekSekcjiViewSet, CzlonekProjektuViewSet, ProjektViewSet, PartnerViewSet, ListaPartnerowViewSet, \
    OdpowiedziSlownikViewSet, pobierz_saldo, PrzychodViewSet, WydatekViewSet, SpotkanieViewSet, SpotkanieCzlonekViewSet, \
    WidokObecnosciViewSet, ObecnoscGridViewSet, CertyfikatGeneratorViewSet, rejestracja_view, login_view, \
    stworz_organizacje_view, przypisz_uzytkownika_view

router = DefaultRouter()


#Słowniki
router.register(r'slownik-statusow', OdpowiedziSlownikViewSet, basename='slownik-statusow')


#Członkowie
router.register(r'lista-czlonkow', ListaCzlonkowViewSet, basename='lista-czlonkow')
router.register(r'czlonkowie', CzlonekCRUDViewSet)

router.register(r'przypisz-kierunek', CzlonekKierunekViewSet)
router.register(r'kierunki', KierunekViewSet, basename='kierunki')

router.register(r'przypisz-sekcje', CzlonekSekcjiViewSet, basename='przypisz-sekcje')
router.register(r'sekcje', SekcjaViewSet, basename='sekcje')

router.register(r'przypisz-projekt', CzlonekProjektuViewSet, basename='przypisz-projekt')
router.register(r'projekty', ProjektViewSet, basename='projekty')

#Partnerzy
router.register(r'partnerzy', PartnerViewSet, basename='partnerzy')
router.register(r'lista-partnerow', ListaPartnerowViewSet, basename='lista-partnerow')
router.register(r'partnerzy-statusy', OdpowiedziSlownikViewSet, basename='partnerzy-statusy')

#Budżet
router.register(r'przychody', PrzychodViewSet, basename='przychody')
router.register(r'wydatki', WydatekViewSet, basename='wydatki')

# Obecności
router.register(r'spotkania', SpotkanieViewSet, basename='spotkania')
router.register(r'obecnosci', SpotkanieCzlonekViewSet, basename='obecnosci')
router.register(r'widok-obecnosci', WidokObecnosciViewSet, basename='widok-obecnosci')
router.register(r'lista-obecnosc', ObecnoscGridViewSet, basename='obecnosc-grid')

# Certyfikaty
router.register(r'certyfikaty-generator', CertyfikatGeneratorViewSet, basename='certyfikaty-generator')




urlpatterns = [
    path('', include(router.urls)),
    path('budzet/saldo/', pobierz_saldo, name='pobierz-saldo'),
    path('auth/rejestracja/', rejestracja_view, name='rejestracja'),
    path('auth/login/', login_view, name='login'),
    path('auth/stworz-organizacje/', stworz_organizacje_view, name='stworz-organizacje'),
    path('auth/przypisz/', przypisz_uzytkownika_view, name='przypisz-uzytkownika'),
]