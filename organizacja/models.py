# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

import sys
TESTING = 'test' in sys.argv

class Budzet(models.Model):
    kwota = models.DecimalField(max_digits=20, decimal_places=2)
    id_wydatek = models.ForeignKey('Wydatek', models.DO_NOTHING, db_column='id_wydatek')
    id_przychod = models.ForeignKey('Przychod', models.DO_NOTHING, db_column='id_przychod')
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.kwota}"

    class Meta:
        managed = TESTING
        db_table = 'budzet'
        verbose_name = "Budżet"
        verbose_name_plural = "Budżety"


class Certyfikat(models.Model):
    id_czlonka = models.ForeignKey('Czlonek', models.DO_NOTHING, db_column='id_czlonka')
    id_projekt = models.ForeignKey('Projekt', models.DO_NOTHING, db_column='id_projekt', null=True, blank=True)
    id_sekcja = models.ForeignKey('Sekcja', models.DO_NOTHING, db_column='id_sekcja', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Certyfikat {self.id} dla czlonka {self.id_czlonka}"

    class Meta:
        managed = TESTING
        db_table = 'certyfikat'
        verbose_name = "Certyfikat"
        verbose_name_plural = "Certyfikaty"


class Czlonek(models.Model):
    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=70)
    e_mail = models.CharField(unique=True, max_length=70)
    indeks = models.IntegerField(unique=True, blank=True, null=True)
    telefon = models.IntegerField(blank=True, null=True)
    id_uzytkownika = models.ForeignKey('Uzytkownik', models.DO_NOTHING, db_column='id_uzytkownika', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)
    id_organizacja = models.ForeignKey('Organizacja', models.CASCADE, db_column='id_organizacja', null=True)

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"

    class Meta:
        managed = TESTING
        db_table = 'czlonek'
        verbose_name = "Członek"
        verbose_name_plural = "Członkowie"


class Czlonekkierunek(models.Model):
    id_czlonek = models.ForeignKey(Czlonek, models.DO_NOTHING, db_column='id_czlonek')
    id_kierunku = models.ForeignKey('Kierunek', models.DO_NOTHING, db_column='id_kierunku')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Członek {self.id_czlonek} kierunku {self.id_kierunku}"

    class Meta:
        managed = TESTING
        db_table = 'czlonekkierunek'
        verbose_name = "Członek Kierunku"
        verbose_name_plural = "Członkowie Kierunków"


class Czlonekprojektu(models.Model):
    id_czlonek = models.ForeignKey(Czlonek, models.DO_NOTHING, db_column='id_czlonek')
    id_projekt = models.ForeignKey('Projekt', models.DO_NOTHING, db_column='id_projekt')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Członek {self.id_czlonek} projektu {self.id_projekt}"

    class Meta:
        managed = TESTING
        db_table = 'czlonekprojektu'
        verbose_name = "Członek Projektu"
        verbose_name_plural = "Członkowie Projektów"


class Czloneksekcji(models.Model):
    id_czlonek = models.ForeignKey(Czlonek, models.DO_NOTHING, db_column='id_czlonek')
    id_sekcja = models.ForeignKey('Sekcja', models.DO_NOTHING, db_column='id_sekcja')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Członek {self.id_czlonek} sekcji {self.id_sekcja}"

    class Meta:
        managed = TESTING
        db_table = 'czloneksekcji'
        verbose_name = "Członek Sekcji"
        verbose_name_plural = "Członkowie Sekcji"


class Kierunek(models.Model):
    nazwa = models.CharField(max_length=50)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        managed = TESTING
        db_table = 'kierunek'
        verbose_name = "Kierunek"
        verbose_name_plural = "Kierunki"


class OdpowiedziSlownik(models.Model):
    nazwa = models.CharField(max_length=50)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        managed = TESTING
        db_table = 'odpowiedzi_slownik'
        verbose_name = "Odpowiedź Słownik"
        verbose_name_plural = "Odpowiedzi Słownik"


class Organizacja(models.Model):
    nazwa = models.CharField(unique=True, max_length=100)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        managed = TESTING
        db_table = 'organizacja'
        verbose_name = "Organizacja"
        verbose_name_plural = "Organizacje"


class Partner(models.Model):
    nazwa = models.CharField(max_length=100)
    numer_telefonu = models.IntegerField(blank=True, null=True)
    e_mail = models.CharField(max_length=70, blank=True, null=True)
    osoba_odpowiedzialna = models.IntegerField()
    przychod = models.DecimalField(max_digits=20, decimal_places=2)
    odpowiedz = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        managed = TESTING
        db_table = 'partner'
        verbose_name = "Partner"
        verbose_name_plural = "Partnerzy"


class Projekt(models.Model):
    nazwa = models.CharField(max_length=80)
    opis = models.CharField(max_length=255, blank=True, null=True)
    id_organizacja = models.ForeignKey('Organizacja', models.CASCADE, db_column='id_organizacja', null=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        managed = TESTING
        db_table = 'projekt'
        verbose_name = "Projekt"
        verbose_name_plural = "Projekty"


class Przychod(models.Model):
    kwota = models.DecimalField(max_digits=20, decimal_places=2)
    nazwa = models.CharField(max_length=60)
    data = models.DateTimeField()
    osoba_odpowiedzialna = models.ForeignKey(Czlonek, models.DO_NOTHING, db_column='osoba_odpowiedzialna')
    id_partner = models.ForeignKey(Partner, models.DO_NOTHING, db_column='id_partner', blank=True, null=True, related_name='partner_przychody')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)
    id_organizacja = models.ForeignKey('Organizacja', models.CASCADE, db_column='id_organizacja', null=True)

    def __str__(self):
        return f"{self.nazwa} - {self.kwota}zł"

    class Meta:
        managed = TESTING
        db_table = 'przychod'
        verbose_name = "Przychód"
        verbose_name_plural = "Przychody"


class Sekcja(models.Model):
    nazwa = models.CharField(max_length=50)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        managed = TESTING
        db_table = 'sekcja'
        verbose_name = "Sekcja"
        verbose_name_plural = "Sekcje"


class Spotkanie(models.Model):
    id_organizatora = models.ForeignKey(Czlonek, models.DO_NOTHING, db_column='id_organizatora')
    nazwa = models.CharField(max_length=100)
    data = models.DateTimeField(blank=True, null=True)
    opis = models.CharField(max_length=255, blank=True, null=True)
    id_organizacja = models.ForeignKey('Organizacja', models.CASCADE, db_column='id_organizacja', null=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        managed = TESTING
        db_table = 'spotkanie'
        verbose_name = "Spotkanie"
        verbose_name_plural = "Spotkania"


class Spotkanieczlonek(models.Model):
    id_spotkania = models.ForeignKey(Spotkanie, models.DO_NOTHING, db_column='id_spotkania')
    id_czlonka = models.ForeignKey(Czlonek, models.DO_NOTHING, db_column='id_czlonka')
    czy_obecny = models.BooleanField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Członek {self.id_czlonka} na spotkaniu {self.id_spotkania}"

    class Meta:
        managed = TESTING
        db_table = 'spotkanieczlonek'
        verbose_name = "Spotkanie Członek"
        verbose_name_plural = "Spotkania Członkowie"


class Uzytkownik(models.Model):
    email = models.CharField(unique=True, max_length=70)
    haslo = models.CharField(max_length=255)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Użytkownik {self.id} "

    class Meta:
        managed = TESTING
        db_table = 'uzytkownik'
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"


class Uzytkownikorganizacja(models.Model):
    id_uzytkownik = models.ForeignKey(Uzytkownik, models.DO_NOTHING, db_column='id_uzytkownik')
    id_organizacja = models.ForeignKey(Organizacja, models.DO_NOTHING, db_column='id_organizacja')
    rola = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"UżytkownikOrganizacja {self.id} - jako {self.rola}"

    class Meta:
        managed = TESTING
        db_table = 'uzytkownikorganizacja'
        verbose_name = "Użytkownik Organizacja"
        verbose_name_plural = "Użytkownicy Organizacje"


class Wydatek(models.Model):
    kwota = models.DecimalField(max_digits=20, decimal_places=2)
    nazwa = models.CharField(max_length=60)
    data = models.DateTimeField()
    osoba_odpowiedzialna = models.ForeignKey(Czlonek, models.DO_NOTHING, db_column='osoba_odpowiedzialna')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opis = models.CharField(max_length=255, blank=True, null=True)
    id_organizacja = models.ForeignKey('Organizacja', models.CASCADE, db_column='id_organizacja', null=True)

    def __str__(self):
        return f"{self.nazwa} - {self.kwota}zł"

    class Meta:
        managed = TESTING
        db_table = 'wydatek'
        verbose_name = "Wydatek"
        verbose_name_plural = "Wydatki"


class WidokBazyCzlonkow(models.Model):
    id = models.IntegerField(primary_key=True)
    czlonek_imie = models.CharField(max_length=50, blank=True, null=True)
    czlonek_nazwisko = models.CharField(max_length=70, blank=True, null=True)
    czlonek_email = models.CharField(max_length=70, blank=True, null=True)
    indeks = models.IntegerField(blank=True, null=True)
    telefon = models.IntegerField(blank=True, null=True)
    data_aktualizacji = models.DateTimeField()
    kierunek_nazwa = models.CharField(max_length=50, blank=True, null=True)
    projekt_nazwa = models.CharField(max_length=80, blank=True, null=True)
    sekcja_nazwa = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.czlonek_imie} {self.czlonek_nazwisko}"

    class Meta:
        managed = TESTING
        db_table = 'widok_bazy_czlonkow'
        verbose_name = "Widok Bazy Członków"
        verbose_name_plural = "Widoki Bazy Członków"


class WidokBudzetu(models.Model):
    id = models.IntegerField(primary_key=True)
    przychod_kwota = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    przychod_nazwa = models.CharField(max_length=60, blank=True, null=True)
    przychod_updated_at = models.DateTimeField(blank=True, null=True)
    osoba_przychod_imie = models.CharField(max_length=50, blank=True, null=True)
    osoba_przychod_nazwisko = models.CharField(max_length=70, blank=True, null=True)
    wydatek_kwota = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    wydatek_nazwa = models.CharField(max_length=60, blank=True, null=True)
    wydatek_updated_at = models.DateTimeField(blank=True, null=True)
    osoba_wydatek_imie = models.CharField(max_length=50, blank=True, null=True)
    osoba_wydatek_nazwisko = models.CharField(max_length=70, blank=True, null=True)

    def __str__(self):
        return f"Przychód: {self.przychod_nazwa} - Wydatek: {self.wydatek_nazwa}"

    class Meta:
        managed = TESTING
        db_table = 'widok_budzetu'
        verbose_name = "Widok Budżetu"
        verbose_name_plural = "Widoki Budżetu"


class WidokCertyfikatow(models.Model):
    id = models.IntegerField(primary_key=True)
    czlonek_imie = models.CharField(max_length=50, blank=True, null=True)
    czlonek_nazwisko = models.CharField(max_length=70, blank=True, null=True)
    projekt_nazwa = models.CharField(max_length=80, blank=True, null=True)
    projekt_data_rozpoczecia = models.DateTimeField(blank=True, null=True)
    certyfikat_data_wystawienia = models.DateTimeField(blank=True, null=True)
    sekcja_nazwa = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Certyfikat dla {self.czlonek_imie} {self.czlonek_nazwisko} w projekcie {self.projekt_nazwa}"

    class Meta:
        managed = TESTING
        db_table = 'widok_certyfikatow'
        verbose_name = "Widok Certyfikatów"
        verbose_name_plural = "Widoki Certyfikatów"


class WidokObecnosci(models.Model):
    id = models.IntegerField(primary_key=True)
    czlonek_imie = models.CharField(max_length=50, blank=True, null=True)
    czlonek_nazwisko = models.CharField(max_length=70, blank=True, null=True)
    czlonek_email = models.CharField(max_length=70, blank=True, null=True)
    spotkanie_data = models.DateTimeField(blank=True, null=True)
    sekcja_nazwa = models.CharField(max_length=50, blank=True, null=True)
    czy_obecny = models.BooleanField()

    def __str__(self):
        return f"Obecność {self.czlonek_imie} {self.czlonek_nazwisko} na spotkaniu {self.spotkanie_data}"

    class Meta:
        managed = TESTING
        db_table = 'widok_obecnosci'
        verbose_name = "Widok Obecności"
        verbose_name_plural = "Widoki Obecności"


class WidokPartnerow(models.Model):
    id = models.IntegerField(primary_key=True)
    partner_nazwa = models.CharField(max_length=100, blank=True, null=True)
    numer_telefonu = models.IntegerField(blank=True, null=True)
    e_mail = models.CharField(max_length=70, blank=True, null=True)
    odpowiedz = models.CharField(max_length=50, blank=True, null=True)
    osoba_odp_imie = models.CharField(max_length=50, blank=True, null=True)
    osoba_odp_nazwisko = models.CharField(max_length=70, blank=True, null=True)
    osoba_odp_e_mail = models.CharField(max_length=70, blank=True, null=True)
    przychod_kwota = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    id_organizacja = models.ForeignKey('Organizacja', models.CASCADE, db_column='id_organizacja', null=True)

    def __str__(self):
        return f"Partner: {self.partner_nazwa}"

    class Meta:
        managed = TESTING
        db_table = 'widok_partnerow'
        verbose_name = "Widok Partnerów"
        verbose_name_plural = "Widoki Partnerów"


class UzytkownikOrganizacja:
    pass