# Mapa Aplikacji - Projekt Darka

Niniejszy dokument definiuje standardowe nazewnictwo elementów interfejsu użytkownika. Będziemy się nimi posługiwać przy wszelkich poprawkach i modyfikacjach.

---

## Widok: Rejestracja Treningu
(Ekran dodawania danych treningowych)

| Numer | Nazwa Elementu | Opis / Lokalizacja |
| :--- | :--- | :--- |
| **1** | **Kalendarz Główny** | Panel "DOWODZENIE" w bocznej sekcji (mini-kalendarz). |
| **2** | **Lista Podopieczny** | Pole wyboru (Selectbox) do wskazania klienta. |
| **3** | **Data Treningu** | Pole wyboru daty (Date Input) pod nagłówkiem "Data". |
| **4** | **Godzina Treningu** | Pole wyboru (Selectbox) pod nagłówkiem "Godzina". |
| **5** | **Lista Główna Partia** | Pole wyboru (Selectbox) dla głównej partii mięśniowej. |
| **6** | **Lista Partia Uzupełniająca** | Pole wyboru (Selectbox) dla partii uzupełniającej. |
| **7** | **Przyciski dla Ćwiczeń** | Interaktywne wiersze (Row Style) do zaznaczania ćwiczeń i wpisywania ciężarów. |
| **8** | **Przyciski Dolne** | Pasek akcji na dole ekranu (POWRÓT, WYCZYŚĆ, ZAPISZ TRENING). |
| **9** | **Menu** | Kafelki Bento w panelu bocznym (ADMINISTRACJA, ANALITYKA, itd.). |

---

## Zasady Współpracy
1. **Precyzja zmian**: Zmieniamy TYLKO ten element, o który prosi użytkownik.
2. **Autoryzacja zmian pośrednich**: Jeśli wykonanie prośby wymaga modyfikacji innej części kodu (nieobjętej prośbą), AI ma obowiązek zapytać o pozwolenie przed wprowadzeniem tych zmian.
3. **Nazewnictwo**: Zawsze używamy nazw z powyższej tabeli (np. "Lista Podopieczny" zamiast "Selectbox").
