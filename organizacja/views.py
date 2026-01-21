from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework import viewsets, filters, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Czlonek, WidokBazyCzlonkow, Czlonekkierunek, Czloneksekcji, Sekcja, Kierunek, Projekt, \
    Czlonekprojektu, WidokPartnerow, Partner, OdpowiedziSlownik, Przychod, Budzet, Wydatek, Spotkanie, Spotkanieczlonek, \
    WidokObecnosci, Uzytkownikorganizacja, Certyfikat, UzytkownikOrganizacja, Uzytkownik
from .serializers import CzlonekSerializer, WidokBazyCzlonkowSerializer, CzlonekKierunekSerializer, \
    CzlonekSekcjiSerializer, SekcjaSerializer, KierunekSerializer, ProjektSerializer, CzlonekProjektuSerializer, \
    WidokPartnerowSerializer, PartnerSerializer, OdpowiedziSlownikSerializer, PrzychodSerializer, WydatekSerializer, \
    SpotkanieSerializer, SpotkanieCzlonekSerializer, WidokObecnosciSerializer, CzlonekObecnoscGridSerializer, \
    CertyfikatUploadSerializer, CertyfikatGenerujRequestSerializer, RejestracjaSerializer, LoginRequestSerializer, \
    StworzOrganizacjaSerializer, MojaAutentykacjaJWT
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes, authentication_classes
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
import io
import os
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.db import transaction
from rest_framework_simplejwt.tokens import AccessToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

# Słowniki
class OdpowiedziSlownikViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint zwracający opcje do dropdown dla statusy odpowiedzi partnerów"""
    queryset = OdpowiedziSlownik.objects.all().order_by('nazwa')
    serializer_class = OdpowiedziSlownikSerializer


# Moduł członków

@extend_schema_view(
    list=extend_schema(summary="Gotowy widok do modułu bazy członków", description="Wyświetla listę wszystkich członków wraz z pełnymi informacjami ze wszystkich tabel powiązanych."),
    retrieve=extend_schema(summary="Szczegóły danego członka", description="Wyświetla dane konkretnego członka po jego ID."),
)
class ListaCzlonkowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WidokBazyCzlonkow.objects.all()
    serializer_class = WidokBazyCzlonkowSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Wyszukiwanie po tych polach
    search_fields = ['czlonek_imie', 'czlonek_nazwisko', 'czlonek_email', 'indeks']

    # Sortowanie
    ordering_fields = ['czlonek_nazwisko', 'czlonek_imie', 'kierunek_nazwa', 'sekcja_nazwa']
    ordering = ['czlonek_nazwisko']                             # Domyślne sortowanie


@extend_schema_view(
    list=extend_schema(summary="Lista danych tabeli członek", description="Pobiera listę rekordów bezpośrednio z tabeli Czlonek."),
    create=extend_schema(summary="Dodaj nowego członka do tabeli członek", description="Tworzy nowy rekord członka. Wymaga podstawowych danych (imię, nazwisko, email)."),
    retrieve=extend_schema(summary="Szczegóły członka w tabeli członek", description="Pobiera surowe dane profilowe członka."),
    update=extend_schema(summary="Pełna edycja danych członka w tabeli członek", description="Nadpisuje wszystkie pola w tabeli Czlonek."),
    partial_update=extend_schema(summary="Szybka edycja danych członka w tabli członek", description="Pozwala na zmianę wybranych pól, np. tylko numeru telefonu."),
    destroy=extend_schema(summary="Usuń wiersz z tabeli członek", description="Usuwa rekord członka. Trigery w bazie SQL automatycznie wyczyszczą jego relacje.")
)
class CzlonekCRUDViewSet(viewsets.ModelViewSet):
    queryset = Czlonek.objects.all()
    serializer_class = CzlonekSerializer


@extend_schema_view(
    list=extend_schema(summary="Lista kierunków do dropdown", description="Pobiera listę kierunków studiów dostępnych w organizacji."),
    create=extend_schema(summary="Dodaj nowy kierunek"),
    retrieve=extend_schema(summary="Szczegóły kierunku",
                           description="Pobiera nazwę i opis konkretnego kierunku po ID."),
    update=extend_schema(summary="Pełna edycja kierunku"),
    partial_update=extend_schema(summary="Szybka edycja kierunku"),
    destroy=extend_schema(summary="Usuń kierunek")
)
class KierunekViewSet(viewsets.ModelViewSet):
    queryset = Kierunek.objects.all()
    serializer_class = KierunekSerializer


@extend_schema_view(
    list=extend_schema(summary="Lista sekcji do dropdown", description="Pobiera listę sekcji działających w organizacji (np. IT, Marketing)."),
    create=extend_schema(summary="Dodaj nową sekcję"),
    retrieve=extend_schema(summary="Szczegóły sekcji"),
    update=extend_schema(summary="Pełna edycja sekcji"),
    partial_update=extend_schema(summary="Szybka edycja sekcji"),
    destroy=extend_schema(summary="Usuń sekcję")
)
class SekcjaViewSet(viewsets.ModelViewSet):
    queryset = Sekcja.objects.all()
    serializer_class = SekcjaSerializer


@extend_schema_view(
    list=extend_schema(summary="Lista projektów do dropdown", description="Pobiera listę wszystkich projektów realizowanych przez organizację."),
    create=extend_schema(summary="Dodaj nowy projekt"),
    retrieve=extend_schema(summary="Szczegóły projektu", description="Pobiera dane konkretnego projektu po ID."),
    update=extend_schema(summary="Pełna edycja projektu"),
    partial_update=extend_schema(summary="Szybka edycja projektu"),
    destroy=extend_schema(summary="Usuń projekt")
)
class ProjektViewSet(viewsets.ModelViewSet):
    queryset = Projekt.objects.all()
    serializer_class = ProjektSerializer


@extend_schema_view(
    list=extend_schema(summary="Lista wszystkich przypisań do kierunków",
                       description="Pobiera listę ID członków i przypisanych im ID kierunków."),
    create=extend_schema(summary="Przypisz członka do kierunku",
                         description="Tworzy relację między członkiem a kierunkiem studiów."),
    retrieve=extend_schema(summary="Szczegóły przypisania kierunku",
                           description="Pobiera konkretne powiązanie członka z kierunkiem."),
    update=extend_schema(summary="Pełna edycja przypisania kierunku"),
    partial_update=extend_schema(summary="Szybka edycja przypisania kierunku"),
    destroy=extend_schema(summary="Usuń przypisanie do kierunku",
                          description="Usuwa powiązanie. Członek i kierunek pozostają w bazie, znika tylko ich relacja.")
)
class CzlonekKierunekViewSet(viewsets.ModelViewSet):
    queryset = Czlonekkierunek.objects.all()
    serializer_class = CzlonekKierunekSerializer


@extend_schema_view(
    list=extend_schema(summary="Lista wszystkich przypisań do sekcji",
                       description="Pobiera listę członków wraz z sekcjami, do których należą."),
    create=extend_schema(summary="Przypisz członka do sekcji",
                         description="Dodaje członka do wybranej sekcji (np. IT, Marketing)."),
    retrieve=extend_schema(summary="Szczegóły przypisania do sekcji"),
    update=extend_schema(summary="Pełna edycja przypisania do sekcji"),
    partial_update=extend_schema(summary="Szybka edycja przypisania do sekcji"),
    destroy=extend_schema(summary="Usuń członka z sekcji")
)
class CzlonekSekcjiViewSet(viewsets.ModelViewSet):
    queryset = Czloneksekcji.objects.all()
    serializer_class = CzlonekSekcjiSerializer


@extend_schema_view(
list=extend_schema(summary="Lista wszystkich przypisań do projektów", description="Pobiera listę pokazującą, kto bierze udział w jakich projektach."),
    create=extend_schema(summary="Przypisz członka do projektu", description="Dodaje członka jako uczestnika konkretnego projektu."),
    retrieve=extend_schema(summary="Szczegóły przypisania do projektu"),
    update=extend_schema(summary="Pełna edycja przypisania do projektu"),
    partial_update=extend_schema(summary="Szybka edycja przypisania do projektu"),
    destroy=extend_schema(summary="Usuń członka z projektu")
)
class CzlonekProjektuViewSet(viewsets.ModelViewSet):
    queryset = Czlonekprojektu.objects.all()
    serializer_class = CzlonekProjektuSerializer


# Moduł partnerów

@extend_schema_view(
    list=extend_schema(summary="Gotowy widok do modułu bazy partnerów", description="Wyświetla listę wszystkich partnerów wraz z pełnymi informacjami ze wszystkich tabel powiązanych."),
    retrieve=extend_schema(summary="Szczegóły danego partnera")
)
class ListaPartnerowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WidokPartnerow.objects.all()
    serializer_class = WidokPartnerowSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['partner_nazwa', 'osoba_odp_nazwisko']
    ordering_fields = ['partner_nazwa', 'przychod_kwota']


@extend_schema_view(
    list=extend_schema(summary="Lista danych tabeli partnerów"),
    create=extend_schema(summary="Dodaj partnera", description="Tworzy nowy wpis firmy partnerskiej."),
    retrieve=extend_schema(summary="Dane do formularza edycji"),
    update=extend_schema(summary="Pełna aktualizacja partnera"),
    partial_update=extend_schema(summary="Edytuj partnera", description="Pozwala na zmianę danych partnera (że ołówek)"),
    destroy=extend_schema(summary="Usuń partnera", description="Trwale usuwa firmę z bazy (że kosz)")
)
class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


@extend_schema_view(list=extend_schema(summary="Opcje odpowiedzi (Dropdown)"))
class OdpowiedziSlownikViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OdpowiedziSlownik.objects.all()
    serializer_class = OdpowiedziSlownikSerializer


# Moduł budżetu
@extend_schema_view(
    list=extend_schema(summary="Lista przychodów", description="Pobiera surowe dane z tabeli przychodów."),
    create=extend_schema(summary="Dodaj przychód", description="Tworzy rekord w tabeli Przychod i automatycznie wiąże go z tabelą Budzet."),
    destroy=extend_schema(summary="Usuń przychód", description="Usuwa przychód i powiązany wpis w tabeli Budzet.")
)
class PrzychodViewSet(viewsets.ModelViewSet):
    queryset = Przychod.objects.all()
    serializer_class = PrzychodSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            przychod = serializer.save()

            Budzet.objects.create(
                id_przychod=przychod,
                kwota=przychod.kwota,
                id_wydatek=None
            )


@extend_schema_view(
    list=extend_schema(summary="Lista wydatków", description="Pobiera dane z tabeli wydatków."),
    create=extend_schema(summary="Dodaj wydatek", description="Tworzy rekord w tabeli Wydatek i automatycznie wiąże go z tabelą Budzet."),
    destroy=extend_schema(summary="Usuń wydatek", description="Usuwa wydatek i powiązany wpis w tabeli Budzet.")
)
class WydatekViewSet(viewsets.ModelViewSet):
    queryset = Wydatek.objects.all()
    serializer_class = WydatekSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            wydatek = serializer.save()

            Budzet.objects.create(
                id_wydatek=wydatek,
                kwota=wydatek.kwota,
                id_przychod=None
            )


@extend_schema(summary="Pobierz aktualne saldo", description="Oblicza sumę przychodów minus sumę wydatków.")
@api_view(['GET'])
def pobierz_saldo(request):
    suma_przychodow = Przychod.objects.aggregate(total=Sum('kwota'))['total'] or 0
    suma_wydatkow = Wydatek.objects.aggregate(total=Sum('kwota'))['total'] or 0

    saldo = suma_przychodow - suma_wydatkow

    return Response({
        'saldo': saldo,
        'waluta': 'PLN',
        'suma_przychodow': suma_przychodow,
        'suma_wydatkow': suma_wydatkow
    })


# Moduł obecności
@extend_schema_view(
    list=extend_schema(summary="Lista spotkań", description="Pobiera listę wszystkich spotkań, które służą jako nagłówki kolumn w tabeli obecności."),
    create=extend_schema(summary="Dodaj nowe spotkanie", description="Tworzy nowe spotkanie. Trigger 'trg_generuj_obecnosci' automatycznie wygeneruje puste rekordy obecności dla wszystkich członków."),
    retrieve=extend_schema(summary="Szczegóły spotkania"),
    update=extend_schema(summary="Pełna edycja spotkania"),
    partial_update=extend_schema(summary="Szybka edycja spotkania (np. zmiana daty)"),
    destroy=extend_schema(summary="Usuń spotkanie", description="Usuwa spotkanie oraz kaskadowo wszystkie powiązane z nim rekordy obecności.")
)
class SpotkanieViewSet(viewsets.ModelViewSet):
    queryset = Spotkanie.objects.all().order_by('-data')
    serializer_class = SpotkanieSerializer


@extend_schema_view(
    partial_update=extend_schema(summary="Zaznacz obecność (checkbox)", description="Aktualizuje status 'czy_obecny' dla konkretnego członka na wybranym spotkaniu.")
)
class SpotkanieCzlonekViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    queryset = Spotkanieczlonek.objects.all()
    serializer_class = SpotkanieCzlonekSerializer


@extend_schema_view(
    list=extend_schema(summary="Gotowy widok obecności (SQL)", description="Wyświetla płaską listę obecności pobraną bezpośrednio z widoku 'Widok_Obecnosci'."),
    retrieve=extend_schema(summary="Szczegóły wpisu w widoku obecności")
)
class WidokObecnosciViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WidokObecnosci.objects.all()
    serializer_class = WidokObecnosciSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['czlonek_imie', 'czlonek_nazwisko', 'czlonek_email']


@extend_schema_view(
    list=extend_schema(summary="Główny widok siatki obecności", description="Zwraca listę członków wraz z ich statusami obecności przypisanymi do spotkań. Idealne do renderowania głównej tabeli modułu.")
)
class ObecnoscGridViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Czlonek.objects.all()
    serializer_class = CzlonekObecnoscGridSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['imie', 'nazwisko', 'e_mail']

# Moduł certyfikatów
@extend_schema_view(
    upload_tlo=extend_schema(summary="Krok 1: Prześlij tło",
                             description="Zapisuje grafikę tymczasowo i zwraca jej ID."),
    generuj=extend_schema(summary="Krok 2 i 3: Generuj PDF",
                          description="Pobiera członków, nakłada dane na tło, wysyła PDF i usuwa tło.")
)
class CertyfikatGeneratorViewSet(viewsets.ViewSet):
    @extend_schema(
        summary="Krok 1: Prześlij tło",
        description="Prześlij grafikę tła. Serwer zwróci identyfikator pliku.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Plik graficzny tła (PNG/JPG)'
                    }
                },
                'required': ['file']
            }
        },
    )
    @action(detail=False, methods=['post'], url_path='upload-tlo')
    def upload_tlo(self, request):
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({"error": "Nie przesłano pliku."}, status=400)

        ext = file_obj.name.split('.')[-1]
        temp_name = f"{uuid.uuid4()}.{ext}"
        path = default_storage.save(f'temp_tla/{temp_name}', file_obj)

        return Response({"temp_file_name": temp_name}, status=201)

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    @extend_schema(
        summary="Krok 2 i 3: Generuj PDF",
        description="Pobiera członków grupy, nakłada dane na tło i zwraca komunikat o sukcesie.",
        request=CertyfikatGenerujRequestSerializer,
    )
    @action(detail=False, methods=['post'], url_path='generuj')
    def generuj(self, request):
        serializer = CertyfikatGenerujRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        temp_name = serializer.validated_data['temp_file_name']
        grupa_id = serializer.validated_data['grupa_id']
        typ_grupy = serializer.validated_data['typ_grupy']

        full_path = os.path.join(settings.MEDIA_ROOT, 'temp_tla', temp_name)

        if not os.path.exists(full_path):
            return Response({"error": "Plik tła nie istnieje lub wygasł."}, status=404)

        czlonkowie = self._get_members(typ_grupy, grupa_id)

        buffer = io.BytesIO()

        # dokument zawsze na A4 w poziomie
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        for czlonek in czlonkowie:
            p.drawImage(full_path, 0, 0, width=width, height=height)

            font_size = 40
            p.setFont("Helvetica-Bold", font_size)
            p.setFillColorRGB(0, 0, 0)

            tekst = f"{czlonek.imie} {czlonek.nazwisko}"
            text_width = p.stringWidth(tekst, "Helvetica-Bold", font_size)

            x_centered = (width - text_width) / 2
            y_centered = height / 2

            p.drawString(x_centered, y_centered, tekst)

            Certyfikat.objects.create(
                id_czlonka=czlonek,
                id_projekt=Projekt.objects.get(id=grupa_id) if typ_grupy == 'projekt' else None,
                id_sekcja=Sekcja.objects.get(id=grupa_id) if typ_grupy == 'sekcja' else None,
                opis=f"Wygenerowano automatycznie: {typ_grupy} ID {grupa_id}"
            )

            p.showPage()

        p.save()
        buffer.seek(0)

        if os.path.exists(full_path):
            os.remove(full_path)

        return FileResponse(buffer, as_attachment=True, filename="certyfikaty_zbiorcze.pdf")

    def _get_members(self, typ, g_id):
        """Pomocnicza funkcja do filtrowania członków wg Twoich grup"""
        if typ == 'wszyscy':
            return Czlonek.objects.all()
        elif typ == 'sekcja':
            return Czlonek.objects.filter(czloneksekcji__id_sekcja=g_id)
        elif typ == 'projekt':
            return Czlonek.objects.filter(czlonekprojektu__id_projekt=g_id)
        return []


# Moduł autoryzacji
@extend_schema(
    summary="Logowanie i generowanie JWT",
    request=LoginRequestSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    haslo_raw = request.data.get('haslo')
    org_id = request.data.get('id_organizacja')

    try:
        uzytkownik = Uzytkownik.objects.get(email=email)
    except Uzytkownik.DoesNotExist:
        return Response({"error": "Niepoprawne dane (użytkownik nie istnieje)"}, status=401)

    if not check_password(haslo_raw, uzytkownik.haslo):
        return Response({"error": "Błędne hasło"}, status=401)

    try:
        powiazanie = Uzytkownikorganizacja.objects.get(
            id_uzytkownik=uzytkownik,
            id_organizacja=org_id
        )
    except Uzytkownikorganizacja.DoesNotExist:
        return Response({
            "error": "Nie należysz do tej organizacji",
            "has_organization": False
        }, status=403)

    access = AccessToken()
    access['user_id'] = uzytkownik.id
    access['rola'] = powiazanie.rola
    access['id_organizacja'] = org_id

    refresh = RefreshToken()
    refresh['user_id'] = uzytkownik.id

    return Response({
        'access': str(access),
        'refresh': str(refresh),
        'role': powiazanie.rola,
        'user_id': uzytkownik.id
    })


@extend_schema(
    summary="Rejestracja użytkownika",
    description="Tworzy nowe konto i haszuje hasło Argon2 przed zapisem.",
    request=RejestracjaSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def rejestracja_view(request):
    serializer = RejestracjaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Użytkownik został zarejestrowany pomyślnie."}, status=201)
    return Response(serializer.errors, status=400)


@extend_schema(
    summary="Krok 2: Utwórz nową organizację",
    request=StworzOrganizacjaSerializer,
)
@api_view(['POST'])
@authentication_classes([MojaAutentykacjaJWT])
@permission_classes([AllowAny])
def stworz_organizacje_view(request):
    uzytkownik = request.user

    if not isinstance(uzytkownik, Uzytkownik):
        return Response({"error": "Brak autoryzacji - zaloguj się i podaj token Bearer"}, status=401)

    serializer = StworzOrganizacjaSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                nowa_org = serializer.save()

                Uzytkownikorganizacja.objects.create(
                    id_uzytkownik=uzytkownik,
                    id_organizacja=nowa_org,
                    rola='Przewodniczacy'
                )

            return Response({"message": f"Organizacja '{nowa_org.nazwa}' utworzona!"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    return Response(serializer.errors, status=400)


