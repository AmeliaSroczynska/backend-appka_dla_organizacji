from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import filters, mixins, viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Czlonek, WidokBazyCzlonkow, Czlonekkierunek, Czloneksekcji, Sekcja, Kierunek, Projekt, \
    Czlonekprojektu, WidokPartnerow, Partner, OdpowiedziSlownik, Przychod, Budzet, Wydatek, Spotkanie, Spotkanieczlonek, \
    WidokObecnosci, Uzytkownikorganizacja, Certyfikat, Uzytkownik
from .serializers import CzlonekSerializer, WidokBazyCzlonkowSerializer, CzlonekKierunekSerializer, \
    CzlonekSekcjiSerializer, SekcjaSerializer, KierunekSerializer, ProjektSerializer, CzlonekProjektuSerializer, \
    WidokPartnerowSerializer, PartnerSerializer, OdpowiedziSlownikSerializer, PrzychodSerializer, WydatekSerializer, \
    SpotkanieSerializer, SpotkanieCzlonekSerializer, WidokObecnosciSerializer, CzlonekObecnoscGridSerializer, \
    CertyfikatGenerujRequestSerializer, RejestracjaSerializer, LoginRequestSerializer, \
    StworzOrganizacjaSerializer, MojaAutentykacjaJWT, PrzypiszUzytkownikaSerializer
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.decorators import action, permission_classes, authentication_classes
from drf_spectacular.utils import extend_schema_view
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
import io
import os
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from django.db import transaction
from rest_framework_simplejwt.tokens import AccessToken
from drf_spectacular.utils import extend_schema
from .permissions import CzySkarbnik, CzyKoordynator, UprawnieniaFinansowe, CzyDowolnaRola, CzyPrzewodniczacy
from django.db.models import Sum


class BaseOrgViewSet(viewsets.ModelViewSet):
    """
    Klasa bazowa dla wszystkich widoków danych.
    Zapewnia autentykację i automatyczne przypisanie id_organizacja.
    """
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [CzyDowolnaRola]

    def perform_create(self, serializer):
        org_id = self.request.auth.get('id_organizacja')
        serializer.save(id_organizacja_id=org_id)

# Słowniki
class OdpowiedziSlownikViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint zwracający opcje do dropdown dla statusy odpowiedzi partnerów"""
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [AllowAny]
    authentication_classes = [MojaAutentykacjaJWT]
    queryset = OdpowiedziSlownik.objects.all().order_by('nazwa')
    serializer_class = OdpowiedziSlownikSerializer


# Moduł członków

@extend_schema_view(
    list=extend_schema(summary="Gotowy widok do modułu bazy członków", description="Wyświetla listę wszystkich członków wraz z pełnymi informacjami ze wszystkich tabel powiązanych."),
    retrieve=extend_schema(summary="Szczegóły danego członka", description="Wyświetla dane konkretnego członka po jego ID."),
)
class ListaCzlonkowViewSet(BaseOrgViewSet):
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [CzyDowolnaRola]
    queryset = WidokBazyCzlonkow.objects.all()
    serializer_class = WidokBazyCzlonkowSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Wyszukiwanie po tych polach
    search_fields = ['czlonek_imie', 'czlonek_nazwisko', 'czlonek_email', 'indeks']

    # Sortowanie
    ordering_fields = ['czlonek_nazwisko', 'czlonek_imie', 'kierunek_nazwa', 'sekcja_nazwa']
    ordering = ['czlonek_nazwisko']                             # Domyślne sortowanie


@extend_schema_view(
    list=extend_schema(summary="Lista kierunków do dropdown", description="Pobiera listę kierunków studiów dostępnych w organizacji."),
    create=extend_schema(summary="Dodaj nowy kierunek"),
    retrieve=extend_schema(summary="Szczegóły kierunku",
                           description="Pobiera nazwę i opis konkretnego kierunku po ID."),
    update=extend_schema(summary="Pełna edycja kierunku"),
    partial_update=extend_schema(summary="Szybka edycja kierunku"),
    destroy=extend_schema(summary="Usuń kierunek")
)
class KierunekViewSet(BaseOrgViewSet):
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
class SekcjaViewSet(BaseOrgViewSet):
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
class ProjektViewSet(BaseOrgViewSet):
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
class CzlonekKierunekViewSet(BaseOrgViewSet):
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
class CzlonekSekcjiViewSet(BaseOrgViewSet):
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
class CzlonekProjektuViewSet(BaseOrgViewSet):
    queryset = Czlonekprojektu.objects.all()
    serializer_class = CzlonekProjektuSerializer


# Moduł partnerów

@extend_schema_view(
    list=extend_schema(summary="Gotowy widok do modułu bazy partnerów", description="Wyświetla listę wszystkich partnerów wraz z pełnymi informacjami ze wszystkich tabel powiązanych."),
    retrieve=extend_schema(summary="Szczegóły danego partnera")
)
class ListaPartnerowViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [CzySkarbnik]
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
class PartnerViewSet(BaseOrgViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CzyKoordynator()]
        return [CzyDowolnaRola()]


@extend_schema_view(list=extend_schema(summary="Opcje odpowiedzi (Dropdown)"))
class OdpowiedziSlownikViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [AllowAny]
    queryset = OdpowiedziSlownik.objects.all()
    serializer_class = OdpowiedziSlownikSerializer


# Moduł budżetu
class PrzychodViewSet(BaseOrgViewSet):
    queryset = Przychod.objects.all()
    serializer_class = PrzychodSerializer
    permission_classes = [UprawnieniaFinansowe]

    def perform_create(self, serializer):
        org_id = self.request.auth.get('id_organizacja')

        with transaction.atomic():
            przychod = serializer.save(id_organizacja_id=org_id)

            Budzet.objects.create(
                id_przychod=przychod,
                kwota=przychod.kwota,
                id_wydatek=None,
            )


class WydatekViewSet(BaseOrgViewSet):
    queryset = Wydatek.objects.all()
    serializer_class = WydatekSerializer
    permission_classes = [UprawnieniaFinansowe]

    def perform_create(self, serializer):
        org_id = self.request.auth.get('id_organizacja')

        with transaction.atomic():
            wydatek = serializer.save(id_organizacja_id=org_id)

            Budzet.objects.create(
                id_wydatek=wydatek,
                kwota=wydatek.kwota,
                id_przychod=None
            )


@extend_schema(
    summary="Pobierz aktualne saldo organizacji",
    description="Oblicza sumę przychodów minus sumę wydatków tylko dla organizacji zalogowanego użytkownika.",
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
@authentication_classes([MojaAutentykacjaJWT])
@permission_classes([UprawnieniaFinansowe])
def pobierz_saldo(request):
    org_id = request.auth.get('id_organizacja')

    suma_przychodow = Przychod.objects.filter(id_organizacja=org_id).aggregate(total=Sum('kwota'))['total'] or 0
    suma_wydatkow = Wydatek.objects.filter(id_organizacja=org_id).aggregate(total=Sum('kwota'))['total'] or 0

    saldo = suma_przychodow - suma_wydatkow

    return Response({
        'id_organizacja': org_id,
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
class SpotkanieViewSet(BaseOrgViewSet):
    queryset = Spotkanie.objects.all().order_by('-data')
    serializer_class = SpotkanieSerializer
    permission_classes = [CzyKoordynator]


@extend_schema_view(
    partial_update=extend_schema(summary="Zaznacz obecność (checkbox)", description="Aktualizuje status 'czy_obecny' dla konkretnego członka na wybranym spotkaniu.")
)
class SpotkanieCzlonekViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [CzyKoordynator]
    queryset = Spotkanieczlonek.objects.all()
    serializer_class = SpotkanieCzlonekSerializer


@extend_schema_view(
    list=extend_schema(summary="Gotowy widok obecności (SQL)", description="Wyświetla płaską listę obecności pobraną bezpośrednio z widoku 'Widok_Obecnosci'."),
    retrieve=extend_schema(summary="Szczegóły wpisu w widoku obecności")
)

class WidokObecnosciViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [CzyKoordynator]

    queryset = WidokObecnosci.objects.all()
    serializer_class = WidokObecnosciSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['czlonek_imie', 'czlonek_nazwisko', 'czlonek_email']


@extend_schema_view(
    list=extend_schema(summary="Główny widok siatki obecności", description="Zwraca listę członków wraz z ich statusami obecności przypisanymi do spotkań. Idealne do renderowania głównej tabeli modułu.")
)
class ObecnoscGridViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [CzyKoordynator]
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
    authentication_classes = [MojaAutentykacjaJWT]
    permission_classes = [CzyKoordynator]
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
    summary="Logowanie do aplikacji lub do organizacji",
    description="Jeśli nie podasz id_organizacja, otrzymasz listę swoich organizacji. "
                "Jeśli podasz id_organizacja, otrzymasz token z uprawnieniami RLS.",
    request=LoginRequestSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    email = serializer.validated_data.get('email')
    haslo_raw = serializer.validated_data.get('haslo')
    org_id = serializer.validated_data.get('id_organizacja')

    try:
        uzytkownik = Uzytkownik.objects.get(email=email)
    except Uzytkownik.DoesNotExist:
        return Response({"error": "Niepoprawne dane"}, status=401)

    if not check_password(haslo_raw, uzytkownik.haslo):
        return Response({"error": "Niepoprawne dane"}, status=401)

    powiazania = Uzytkownikorganizacja.objects.filter(id_uzytkownik=uzytkownik)
    lista_org = [
        {"id": p.id_organizacja.id, "nazwa": p.id_organizacja.nazwa, "rola": p.rola}
        for p in powiazania
    ]

    # Logowanie bez wybranej organizacji
    if org_id is None:
        access = AccessToken()
        access['user_id'] = uzytkownik.id
        access['id_organizacja'] = 0
        access['rola'] = 'Gosc'

        return Response({
            "message": "Zalogowano globalnie",
            "access": str(access),
            "user_id": uzytkownik.id,
            "moje_organizacje": lista_org
        }, status=200)

    # Logowanie do konkretnej organizacji
    try:
        aktywne_powiazanie = powiazania.get(id_organizacja=org_id)

        access = AccessToken()
        access['user_id'] = uzytkownik.id
        access['id_organizacja'] = org_id
        access['rola'] = aktywne_powiazanie.rola

        return Response({
            "message": f"Zalogowano do organizacji {aktywne_powiazanie.id_organizacja.nazwa}",
            "access": str(access),
            "role": aktywne_powiazanie.rola,
            "id_organizacja": org_id
        }, status=200)

    except Uzytkownikorganizacja.DoesNotExist:
        return Response({"error": "Nie należysz do tej organizacji"}, status=403)

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
    summary="Tworzenie nowej organizacji",
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


@extend_schema(
    summary="Przypisanie osoby do organizacji",
    description="Pozwala Przewodniczącemu dodać innego użytkownika do swojej organizacji.",
    request=PrzypiszUzytkownikaSerializer,
)
@api_view(['POST'])
@authentication_classes([MojaAutentykacjaJWT])
@permission_classes([CzyPrzewodniczacy])
def przypisz_uzytkownika_view(request):
    uzytkownik_wykonujacy = request.user
    aktywne_org_id = request.auth.get('id_organizacja')
    serializer = PrzypiszUzytkownikaSerializer(data=request.data)

    if serializer.is_valid():
        email_zapraszanego = serializer.validated_data['email']
        nowa_rola = serializer.validated_data['rola']

        try:
            twoje_powiazanie = Uzytkownikorganizacja.objects.get(
                id_uzytkownik=uzytkownik_wykonujacy,
                id_organizacja_id=aktywne_org_id,
                rola='Przewodniczacy'
            )
            organizacja = twoje_powiazanie.id_organizacja

            try:
                zapraszany = Uzytkownik.objects.get(email=email_zapraszanego)
            except Uzytkownik.DoesNotExist:
                return Response({"error": "Użytkownik o tym e-mailu nie ma jeszcze konta w aplikacji."}, status=404)

            if Uzytkownikorganizacja.objects.filter(id_uzytkownik=zapraszany, id_organizacja=organizacja).exists():
                return Response({"error": "Ten użytkownik już należy do Twojej organizacji."}, status=400)

            Uzytkownikorganizacja.objects.create(
                id_uzytkownik=zapraszany,
                id_organizacja=organizacja,
                rola=nowa_rola
            )

            return Response({"message": f"Użytkownik {email_zapraszanego} został dodany jako {nowa_rola}."}, status=201)

        except Uzytkownikorganizacja.DoesNotExist:
            return Response({"error": "Nie masz uprawnień Przewodniczącego, aby dodawać osoby."}, status=403)

    return Response(serializer.errors, status=400)


class CzlonekCRUDViewSet(BaseOrgViewSet):
    """Baza członków: Wszyscy mają dostęp."""
    queryset = Czlonek.objects.all()
    serializer_class = CzlonekSerializer
    permission_classes = [CzyDowolnaRola]



