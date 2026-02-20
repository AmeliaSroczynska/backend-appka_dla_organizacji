# Backend do Aplikacji dla Organizacji Studenckich

## Opis projektu

Projekt stanowi **backend aplikacji webowej** napisany w **Pythonie z wykorzystaniem frameworka Django**.  
Backend obsługuje frontend aplikacji do **zarządzania organizacją studencką**, dostępny pod adresem:

➡️ https://hubert.antek.page

Aplikacja umożliwia:

- zarządzanie **listą członków organizacji**
- rejestrowanie **obecności**
- obsługę **budżetu**
- zarządzanie **partnerami**
- automatyzację generowania wielu **certyfikatów**

Repozytorium kodu frontendowego znajduje się pod adresem:  
➡️ https://github.com/NeoNeq5/front

---

## Technologie

Projekt w części backendowej wykorzystuje:

- Python 3
- Django
- Baza danych PostgreSQL

---

## Uruchomienie projektu lokalnie

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/AmeliaSroczynska/backend-appka_dla_organizacji.git
cd backend-appka_dla_organizacji
```

### 2. Utworzenie środowiska wirtualnego
```bash
python -m venv venv
```

Aktywacja środowiska:
```bash
Windows:
venv\Scripts\activate

Linux / macOS:
source venv/bin/activate
```

### 3. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 4. Konfiguracja zmiennych środowiskowych

Skopiuj plik konfiguracyjny:
```bash
cp .env.example .env
```
Następnie uzupełnij plik .env

### 5. Migracje bazy danych

Utwórz strukturę bazy danych:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Uruchomienie serwera
```bash
python manage.py runserver
```

Aplikacja będzie dostępna pod adresem:

➡️ http://127.0.0.1:8000
