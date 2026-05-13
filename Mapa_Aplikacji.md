# Mapa Aplikacji - Projekt Darka

Niniejszy dokument definiuje standardowe nazewnictwo elementów interfejsu użytkownika. Będziemy się nimi posługiwać przy wszelkich poprawkach i modyfikacjach. W kodzie elementy te są oznaczone tagami `[WIDOK]` oraz `[Element X]`.

---

## Widok: Rejestracja Treningu
**(Tag w kodzie: `[WIDOK: REJESTRACJA]`)**

| Numer | Nazwa Elementu | Opis / Lokalizacja |
| :--- | :--- | :--- |
| **1** | **Kalendarz Główny** | Panel "DOWODZENIE" (boczna sekcja - globalny). |
| **2** | **Lista Podopieczny** | Pole wyboru (Selectbox) do wskazania klienta. |
| **3** | **Data Treningu** | Pole wyboru daty (Date Input) pod nagłówkiem "Data". |
| **4** | **Godzina Treningu** | Pole wyboru (Selectbox) pod nagłówkiem "Godzina". |
| **5** | **Lista Główna Partia** | Pole wyboru (Selectbox) dla głównej partii mięśniowej. |
| **6** | **Lista Partia Uzupełniająca** | Pole wyboru (Selectbox) dla partii uzupełniającej. |
| **7** | **Przyciski dla Ćwiczeń** | Interaktywne wiersze (Row Style) do zaznaczania ćwiczeń i wpisywania ciężarów. |
| **8** | **Przyciski Dolne** | Pasek akcji na dole (POWRÓT, WYCZYŚĆ, ZAPISZ TRENING). |
| **9** | **Menu** | Kafelki Bento w bocznej sekcji (ADMINISTRACJA, ANALITYKA, itd. - globalny). |

---

## Widok: Grafik (Ekran Główny)
**(Tag w kodzie: `[WIDOK: GRAFIK]`)**

| Numer | Nazwa Elementu | Opis / Lokalizacja |
| :--- | :--- | :--- |
| **1** | **Kalendarz Główny** | Panel "DOWODZENIE" (boczna sekcja - globalny). |
| **2** | **Przyciski górne** | Pasek sterowania (DZIEŃ, TYDZIEŃ, EDYTUJ). *Możliwość ukrycia (show_upper_buttons).* |
| **3** | **Kalendarz Zapisów** | Główna siatka grafikowa z godzinami i zapisanymi treningami. |
| **4** | **Menu** | Kafelki Bento w bocznej sekcji (ADMINISTRACJA, ANALITYKA, itd. - globalny). |

---

## Zasady Współpracy
1. **Precyzja zmian**: Zmieniamy TYLKO ten element, o który prosi użytkownik.
2. **Propozycja zmian**: PRZED każdą zmianą kodu, AI musi przedstawić konkretną propozycję zmian i zapytać o zgodę na wdrożenie.
3. **Autoryzacja zmian pośrednich**: Jeśli wykonanie prośby wymaga modyfikacji innej części kodu (nieobjętej prośbą), AI ma obowiązek zapytać o pozwolenie przed wprowadzeniem tych zmian.
4. **Nazewnictwo**: Zawsze używamy nazw z powyższej tabeli (np. "Lista Podopieczny" zamiast "Selectbox").
5. **Identyfikacja**: W razie wątpliwości sprawdzamy tagi `[WIDOK: ...]` w komentarzach skryptu `main.py`.
