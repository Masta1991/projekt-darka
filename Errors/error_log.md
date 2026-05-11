# Rejestr Błędów i Rozwiązań - Projekt Darka

Niniejszy plik służy jako baza wiedzy o unikalnych problemach technicznych napotkanych podczas rozwoju aplikacji, aby zapobiec ich powielaniu w przyszłości.

---

## 1. Błąd importu modułów (KeyError)
- **Problem**: Podczas uruchamiania na Streamlit Cloud, linia `from data_handler import DataHandler` wyrzucała `KeyError`.
- **Przyczyna**: Próba dostępu do `st.secrets` wewnątrz importowanego modułu w sposób słownikowy (`st.secrets["key"]`) lub sprawdzanie `in st.secrets` w momencie, gdy środowisko nie wczytało jeszcze sekretów.
- **Rozwiązanie**: Połączono klasę `DataHandler` bezpośrednio z plikiem `main.py` (tzw. "nuclear merge") lub stosowanie wyłącznie bezpiecznego `st.secrets.get("key")`.

## 2. Niestabilne stylowanie "Portali" (Kalendarz i Dropdowny)
- **Problem**: Standardowy CSS nie zmieniał koloru tła kalendarza `st.date_input` oraz list rozwijanych (pozostawały jasne).
- **Przyczyna**: Streamlit renderuje te elementy w osobnych kontenerach (Portalach) poza główną strukturą aplikacji, do których standardowe style `st.markdown` nie zawsze docierają.
- **Rozwiązanie**: Iniekcja globalnych stylów CSS bezpośrednio do nagłówka strony (`head`) za pomocą skryptu JavaScript działającego na poziomie `window.parent.document`.

## 3. Brak responsywności przycisków (JS Bridge)
- **Problem**: Po aktualizacji stylów przyciski w menu i kalendarzu przestały reagować na kliknięcia.
- **Przyczyna**: Listener zdarzeń w skrypcie JS został przypisany do `document.body`, co wewnątrz iframe'u `components.html` oznaczało nasłuchiwanie w pustym, ukrytym oknie, a nie na stronie aplikacji.
- **Rozwiązanie**: Zmieniono cel nasłuchiwania na `parentDoc.body.addEventListener`, co pozwoliło poprawnie przechwytywać kliknięcia na elementach strony głównej.

## 4. Błąd Indentacji przy pobieraniu klientów
- **Problem**: `IndentationError: expected an indented block after 'with' statement`.
- **Przyczyna**: Błędne wcięcie kodu po dodaniu dekoratora `@st.cache_data` wewnątrz bloku `with`.
- **Rozwiązanie**: Poprawiono strukturę wcięć i ostatecznie uproszczono funkcję pobierania listy klientów, aby uniknąć konfliktów z dekoratorami wewnątrz bloków warunkowych.

## 5. Walidacja zapisu treningu
- **Problem**: Użytkownik nie mógł zapisać samego faktu odbycia treningu w kalendarzu bez wybrania konkretnych ćwiczeń.
- **Przyczyna**: Kod wymagał, aby `st.session_state.add_data_exercises` nie było puste.
- **Rozwiązanie**: Usunięto warunek blokujący, pozwalając na zapisywanie zdarzeń kalendarzowych nawet z pustą listą ćwiczeń.
## 6. Stylizacja "owalu" w listach rozwijalnych
- **Problem**: Opcje w listach rozwijalnych (np. wybór godziny) stały się wąskimi owalami zamiast prostokątów.
- **Przyczyna**: Styl CSS dla zaznaczenia (`aria-selected="true"`) posiadał `border-radius: 50%` bez odpowiedniego zawężenia selektora do kalendarza. Streamlit używa tego samego atrybutu ARIA dla list rozwijalnych.
- **Rozwiązanie**: Zawężono selektor okrągły wyłącznie do kalendarza (`[data-baseweb="calendar"] [aria-selected="true"]`) i zdefiniowano osobny styl prostokątny dla list (`[role="listbox"] [aria-selected="true"]`).
