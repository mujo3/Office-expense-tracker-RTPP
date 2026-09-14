# Office Expense Tracker

Web aplikacija za vođenje evidencije potrošnje ureda, razvijena za kompaniju **HTEC** (ured u Tuzli) u sklopu predmeta **Razvoj telekomunikacijske programske podrške** na Fakultetu elektrotehnike Univerziteta u Tuzli.

Aplikacija omogućava unos faktura (uz automatsko očitavanje podataka sa slike putem OCR-a), praćenje potrošnje po kategorijama u odnosu na postavljene budžete, te generisanje mjesečnih, kvartalnih i godišnjih Excel izvještaja.

**Tehnologije:** Python · Flask · SQLAlchemy · PostgreSQL · Jinja2 · HTML · CSS · JavaScript

---

## Sadržaj

- [Funkcionalnosti](#funkcionalnosti)
- [Tehnologije](#tehnologije)
- [Struktura projekta](#struktura-projekta)
- [Model podataka](#model-podataka)
- [Pokretanje aplikacije](#pokretanje-aplikacije)
- [Pomoćne skripte](#pomoćne-skripte)
- [Testovi](#testovi)
- [Poznata ograničenja i dalji rad](#poznata-ograničenja-i-dalji-rad)
- [Tim i organizacija rada](#tim-i-organizacija-rada)
- [Dokumentacija](#dokumentacija)

---

## Funkcionalnosti

### Autentifikacija i korisnici
- Prijava putem e-maila i lozinke, sa heširanjem lozinki (`werkzeug.security`)
- Dvije uloge: **admin** i **employee**, sa kontrolom pristupa po rutama
- Obavezna promjena lozinke pri prvoj prijavi (`must_change_pwd`)
- Zaboravljena lozinka — slanje reset linka na e-mail sa vremenski ograničenim tokenom (`itsdangerous`), uz evidenciju iskorištenih tokena
- Sesija ističe nakon 60 minuta

### Unos troškova
- Unos fakture sa stavkama: proizvod, količina, mjerna jedinica, cijena, dobavljač, kategorija
- **OCR prepoznavanje faktura** — upload slike fakture, a aplikacija pomoću `invoice2data` i `pytesseract` pokušava automatski očitati broj fakture, datum, iznos i dobavljača te popuniti formu
- Prepoznavanje dobavljača poređenjem očitanog teksta sa dobavljačima u bazi

### Administracija
- Upravljanje korisnicima (dodavanje, brisanje, dodjela uloge)
- Upravljanje kategorijama troškova
- Postavljanje i uređivanje budžeta — ukupnih i po kategorijama, sa periodima i opcijom ponavljajućeg budžeta

### Izvještaji i analitika
- Dashboard sa pregledom potrošnje u odnosu na budžet
- Generisanje Excel izvještaja pomoću `pandas` / `xlsxwriter`:
  - mjesečni izvještaj o budžetu (sažeti ili detaljni, sa listom troškova i pregledom po dobavljačima)
  - kvartalni izvještaj
  - godišnji izvještaj sa analizom trendova
  - izvoz kompletnih podataka
- Grafikoni ugrađeni u generisane Excel radne listove

---

## Tehnologije

| Sloj | Tehnologija |
| --- | --- |
| Backend | Python, Flask 3, Blueprints |
| Baza | PostgreSQL (produkcija), SQLite (lokalni fallback) |
| ORM i migracije | SQLAlchemy 2, Flask-Migrate (Alembic) |
| Autentifikacija | Flask-Login, Werkzeug password hashing, itsdangerous |
| Forme | Flask-WTF, WTForms |
| E-mail | Flask-Mail (SMTP) |
| Frontend | Jinja2 templates, HTML5, CSS3, JavaScript |
| Izvještaji | pandas, xlsxwriter, openpyxl |
| OCR | pytesseract (Tesseract OCR), invoice2data, Pillow |
| Testovi | pytest |

---

## Struktura projekta

```
office-expense-tracker/
├── rtpp_app/                   # glavni Flask paket
│   ├── __init__.py             # application factory (create_app)
│   ├── extensions.py           # instance db, login_manager, mail, csrf
│   ├── forms.py                # WTForms forme
│   ├── models/                 # SQLAlchemy modeli
│   ├── routes/                 # blueprints: auth, main, expenses, admin, reports
│   ├── templates/              # Jinja2 templejti
│   ├── static/                 # CSS, JS, slike
│   └── tests/                  # pytest testovi
├── migrations/                 # Alembic migracije baze
├── scripts/                    # pomoćne razvojne skripte
├── docs/                       # projektna dokumentacija i retrospektive
├── config.py                   # konfiguracija (čita .env)
├── run.py                      # ulazna tačka aplikacije
├── requirements.txt
└── .env.example                # predložak za varijable okruženja
```

---

## Model podataka

| Tabela | Opis |
| --- | --- |
| `users` | korisnici sa ulogom (`admin` / `employee`) i heširanom lozinkom |
| `invoice` | zaglavlje fakture — broj, datum, dobavljač, ukupan iznos |
| `invoice_items` | stavke fakture — proizvod, količina, jedinična cijena |
| `products` | proizvodi i usluge koji se pojavljuju na fakturama |
| `vendor` | dobavljači |
| `category` | kategorije troškova |
| `budget` | ukupni budžeti po periodu |
| `category_budgets` | budžeti raspoređeni po kategorijama |
| `measuringUnits` | mjerne jedinice |
| `blackListTokens` | iskorišteni tokeni za reset lozinke |

Promjene šeme vode se kroz Alembic migracije u folderu `migrations/versions/`.

---

## Pokretanje aplikacije

### Preduslovi
- Python 3.12+
- PostgreSQL (opcionalno — bez `DATABASE_URL` koristi se lokalni SQLite)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — samo ako se koristi očitavanje faktura

### Koraci

```bash
# 1. Kloniraj repozitorij
git clone https://github.com/<username>/office-expense-tracker.git
cd office-expense-tracker

# 2. Virtuelno okruženje
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Zavisnosti
pip install -r requirements.txt

# 4. Varijable okruženja
cp .env.example .env            # Windows: copy .env.example .env
# otvori .env i popuni DATABASE_URL, SECRET_KEY i MAIL_* vrijednosti

# 5. Kreiraj šemu baze
flask db upgrade

# 6. Pokreni aplikaciju
python run.py
```

Aplikacija je dostupna na `http://127.0.0.1:5000`.

Prvog admin korisnika potrebno je ručno unijeti u bazu (sa heširanom lozinkom i `role = 'admin'`), nakon čega se ostali korisnici dodaju kroz administratorski panel.

---

## Pomoćne skripte

Pokreću se iz korijena projekta:

```bash
python -m scripts.init_db        # kreira tabele direktno iz modela (bez migracija)
python -m scripts.flush_data     # briše testne podatke, zadržava korisnike
python -m scripts.debug_smtp     # lokalni SMTP server na portu 8025 za testiranje e-maila
```

---

## Testovi

```bash
pytest rtpp_app/tests
```

Testovi koriste zasebnu konfiguraciju (`TestingConfig`) sa SQLite bazom u memoriji, pa ne diraju razvojnu bazu.

---

## Poznata ograničenja i dalji rad

Projekat je razvijan u okviru semestra i sljedeće stavke ostaju kao prostor za poboljšanje:

- CSRF zaštita je onemogućena u `create_app()` radi lakšeg testiranja tokom razvoja — treba je vratiti prije bilo kakve produkcijske upotrebe
- `SERVER_NAME` je fiksiran na `127.0.0.1:5000` u `config.py`, što treba prebaciti u varijablu okruženja
- Putanja do Tesseract izvršne datoteke je hardkodirana za Windows u `routes/expenses.py`
- Test pokrivenost obuhvata autentifikaciju; unos faktura i izvještaji nisu pokriveni testovima

---

## Tim i organizacija rada

Projekat je razvijen timski, po Scrum metodologiji, kroz sprintove sa retrospektivama (vidi `docs/`).

**Tim „Šoldy”**

| Član | Uloga |
| --- | --- |
| Mujo Alić | vođa tima |
| Hasan Avdić | član tima |
| Mahir Halilović | član tima |
| Haris Vikalo | član tima |
| Ehlimana Beganović | član tima |

Za Sprint 0 ulogu Product Ownera imao je Edin Ahmetbegović, a Scrum Mastera Emina Jusufović.

**Mentorstvo**

- Profesorica: vanr. prof. dr. Alma Šećerbegović
- Asistent: Admir Mustafić

**Alati:** Jira (backlog i sprintovi), Figma (dizajn sučelja), Discord i Messenger (komunikacija unutar tima).

- [Figma mockup]([https://www.figma.com/design/IV4r8BYNYd0j2BIlpiNvn1/Soldy?node-id=2-2&t=yzCT0D0PuiEwkXmX-1])

---

## Dokumentacija

U folderu `docs/`:

- `MVP - Tracking office spending.docx` — opis minimalno održivog proizvoda

---

## Napomena o podacima

Repozitorij ne sadrži `.env` fajl, backupe baze niti uploadovane fakture. Ti fajlovi sadrže pristupne podatke i lične podatke korisnika, pa su izuzeti kroz `.gitignore`. Za pokretanje je potrebno napraviti vlastiti `.env` prema predlošku `.env.example`.
