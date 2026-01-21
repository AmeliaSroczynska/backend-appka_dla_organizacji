from rest_framework import serializers
from django.contrib.auth.hashers import make_password
import re

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

from .models import Czlonek, WidokBazyCzlonkow, Kierunek, Czlonekkierunek, Sekcja, Czloneksekcji, Czlonekprojektu, \
    Projekt, Partner, WidokPartnerow, OdpowiedziSlownik, Przychod, WidokBudzetu, Wydatek, Spotkanie, Spotkanieczlonek, \
    WidokObecnosci, Uzytkownikorganizacja, Uzytkownik, Organizacja


# Słowniki
class OdpowiedziSlownikSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdpowiedziSlownik
        fields = ['id', 'nazwa']


# Moduł członków
class WidokBazyCzlonkowSerializer(serializers.ModelSerializer):
    class Meta:
        model = WidokBazyCzlonkow
        fields = '__all__'


class CzlonekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Czlonek
        fields = ['id', 'imie', 'nazwisko', 'e_mail', 'indeks', 'telefon', 'opis']

    def validate(self, data):
        imie = data.get('imie')
        nazwisko = data.get('nazwisko')

        if imie and nazwisko:
            if imie.strip() == "Antek" and nazwisko.strip() == "Czaplicki":
                raise serializers.ValidationError(
                    "Nie można dodać tego użytkownika: debil."
                )

        return data


class CzlonekKierunekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Czlonekkierunek
        fields = '__all__'


class KierunekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kierunek
        fields = '__all__'


class SekcjaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sekcja
        fields = '__all__'


class CzlonekSekcjiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Czloneksekcji
        fields = '__all__'


class ProjektSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projekt
        fields = '__all__'


class CzlonekProjektuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Czlonekprojektu
        fields = '__all__'


# Moduł partnerów
class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

    def validate_osoba_odpowiedzialna(self, value):
        if not Czlonek.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Nie można przypisać osoby o ID {value}, ponieważ taki członek nie istnieje."
            )
        return value


class WidokPartnerowSerializer(serializers.ModelSerializer):
    class Meta:
        model = WidokPartnerow
        fields = '__all__'

class OdpowiedziSlownikSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdpowiedziSlownik
        fields = '__all__'



# Moduł budżetu
class CzlonekSzczegolySerializer(serializers.ModelSerializer):
    """Pomocniczy serializer do wyświetlania danych osoby w budżecie"""
    class Meta:
        model = Czlonek
        fields = ['imie', 'nazwisko', 'e_mail']


class PrzychodSerializer(serializers.ModelSerializer):
    osoba_dane = CzlonekSzczegolySerializer(source='osoba_odpowiedzialna', read_only=True)

    class Meta:
        model = Przychod
        fields = ['id', 'kwota', 'nazwa', 'data', 'osoba_odpowiedzialna', 'osoba_dane', 'id_partner', 'opis']


class WydatekSerializer(serializers.ModelSerializer):
    osoba_dane = CzlonekSzczegolySerializer(source='osoba_odpowiedzialna', read_only=True)

    class Meta:
        model = Wydatek
        fields = ['id', 'kwota', 'nazwa', 'data', 'osoba_odpowiedzialna', 'osoba_dane', 'opis']


class WidokBudzetuSerializer(serializers.ModelSerializer):
    class Meta:
        model = WidokBudzetu
        fields = '__all__'

# Moduł obecności
class SpotkanieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spotkanie
        fields = '__all__'

class SpotkanieCzlonekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spotkanieczlonek
        fields = ['id', 'czy_obecny']

class WidokObecnosciSerializer(serializers.ModelSerializer):
    class Meta:
        model = WidokObecnosci
        fields = '__all__'

class CzlonekObecnoscGridSerializer(serializers.ModelSerializer):
    obecnosci = SpotkanieCzlonekSerializer(source='obecnosci_czlonka', many=True, read_only=True)

    class Meta:
        model = Czlonek
        fields = ['id', 'imie', 'nazwisko', 'e_mail', 'obecnosci']


# Moduł certyfikatów
class CertyfikatGenerujRequestSerializer(serializers.Serializer):
    temp_file_name = serializers.CharField()
    grupa_id = serializers.IntegerField()
    typ_grupy = serializers.ChoiceField(choices=['wszyscy', 'sekcja', 'projekt'])


class CertyfikatUploadSerializer(serializers.Serializer):
    file = serializers.ImageField()


# Autoryzacja
class RejestracjaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uzytkownik
        fields = ['email', 'haslo']
        extra_kwargs = {
            'haslo': {'write_only': True}
        }

    def validate_email(self, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Błędny format e-mail.")

        if Uzytkownik.objects.filter(email=value).exists():
            raise serializers.ValidationError("Użytkownik o tym adresie e-mail już istnieje.")
        return value

    def create(self, validated_data):
        validated_data['haslo'] = make_password(validated_data['haslo'])
        return super().create(validated_data)


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Twój adres e-mail")
    haslo = serializers.CharField(help_text="Twoje hasło")
    id_organizacja = serializers.IntegerField(help_text="ID organizacji, do której się logujesz")


class StworzOrganizacjaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizacja
        fields = ['nazwa']


class MojaAutentykacjaJWT(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get('Authorization')

        if not header or not header.startswith('Bearer '):
            return None

        try:
            token_str = header.split(' ')[1]
            token = AccessToken(token_str)
            user_id = token['user_id']
            uzytkownik = Uzytkownik.objects.get(id=user_id)
            return (uzytkownik, token)
        except Exception:
            raise AuthenticationFailed('Nieprawidłowy token lub użytkownik nie istnieje')