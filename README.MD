# Dokumentacja Aplikacji PDF to CSV Converter

## Przegląd Aplikacji

Aplikacja **PDF to CSV Converter** to narzędzie Streamlit, które umożliwia konwersję tabel z dokumentów PDF do formatu CSV (Comma Separated Values) przy użyciu modelu językowego Gemini API. Aplikacja jest szczególnie przydatna do ekstrakcji danych tabelarycznych z raportów, zestawień i innych dokumentów PDF.

**Główna funkcjonalność aplikacji:**

*   **Konwersja PDF do CSV:** Wykorzystuje model Gemini API do rozpoznawania i ekstrakcji danych tabelarycznych z dokumentów PDF i przekształcania ich w format CSV.
*   **Obsługa PDF z pliku i URL:** Użytkownik może przesłać plik PDF z dysku lokalnego lub podać URL do dokumentu PDF online.
*   **Wybór zakresu stron:** Możliwość konwersji tylko określonego zakresu stron z dokumentu PDF.
*   **Wyświetlanie tabeli w czasie rzeczywistym:** Wyniki konwersji są wyświetlane w formie tabeli w aplikacji na bieżąco podczas przetwarzania.
*   **Pobieranie pliku CSV:** Wygenerowany plik CSV można pobrać na dysk lokalny.
*   **Kontrola procesu:** Przyciski "Convert", "STOP" i "Od nowa" umożliwiają kontrolę nad procesem konwersji, zatrzymanie go i zresetowanie aplikacji.
*   **Wskaźniki postępu:** Aplikacja informuje o postępie konwersji, szacowanym czasie zakończenia i prędkości przetwarzania.
*   **Obsługa błędów:** Aplikacja informuje o błędach podczas odczytu PDF, konwersji lub parsowania CSV.

## Jak Używać Aplikacji

Poniżej znajdziesz instrukcję krok po kroku, jak korzystać z aplikacji PDF to CSV Converter.

### 1. Uruchomienie Aplikacji

1.  **Upewnij się, że masz zainstalowane wymagane biblioteki.** Jeśli jeszcze tego nie zrobiłeś, zainstaluj je za pomocą `pip`:
    ```bash
    pip install streamlit PyPDF2 requests python-dotenv google-generativeai pandas stqdm
    ```
2.  **Zapisz kod aplikacji** (dostarczony kod Python) do pliku, na przykład `pdf_to_csv_app.py`.
3.  **Uruchom aplikację Streamlit** z poziomu terminala, przechodząc do katalogu, w którym zapisałeś plik i wykonując polecenie:
    ```bash
    streamlit run pdf_to_csv_app.py
    ```
    Aplikacja powinna otworzyć się w Twojej przeglądarce internetowej.

### 2. Konfiguracja Klucza API Gemini

1.  **Uzyskaj klucz API Gemini.**  Jeśli jeszcze go nie posiadasz, kliknij przycisk **"GET KEY"** w aplikacji. Zostaniesz przekierowany do Google AI Studio, gdzie możesz utworzyć klucz API.
2.  **Wprowadź klucz API.** W polu tekstowym **"Enter your Gemini API Key..."** wprowadź swój klucz API Gemini. Możesz również pozostawić to pole puste, jeśli ustawiłeś zmienną środowiskową `GEMINI_API_KEY` zawierającą Twój klucz.
3.  **Alternatywnie, ustaw zmienną środowiskową.** Możesz ustawić zmienną środowiskową `GEMINI_API_KEY` w systemie operacyjnym, aby uniknąć konieczności wprowadzania klucza API za każdym razem.

### 3. Wybór Źródła PDF

W aplikacji dostępne są dwie opcje wyboru źródła dokumentu PDF:

*   **Upload PDF file:**
    1.  Wybierz opcję **"Upload PDF file"**.
    2.  Kliknij **"Browse files"** i wybierz plik PDF z dysku lokalnego, który chcesz przekonwertować.

*   **Enter PDF URL:**
    1.  Wybierz opcję **"Enter PDF URL"**.
    2.  W polu tekstowym **"Enter PDF URL:"** wprowadź adres URL dokumentu PDF, który chcesz przekonwertować. Na przykład, dla raportu ENEA:
        ```
        https://operator.enea.pl/uploads-ev2/Operator/ospolce/raporty/Publikacja_podmiot%C3%B3w_31_12_2024r..pdf
        ```

### 4. Wybór Zakresu Stron

1.  **Sprawdź liczbę stron.** Po wczytaniu pliku PDF lub URL, aplikacja wyświetli informację o całkowitej liczbie stron w dokumencie.
2.  **Ustaw zakres stron.** W polach **"Start Page"** i **"End Page"** wprowadź numery stron, które chcesz przekonwertować. Domyślnie zakres jest ustawiony na cały dokument (od strony 1 do ostatniej strony). Możesz dostosować zakres, jeśli chcesz przetworzyć tylko część dokumentu. Upewnij się, że strona początkowa nie jest większa niż strona końcowa.

### 5. Rozpoczęcie Konwersji

1.  **Kliknij przycisk "Convert".** Po ustawieniu źródła PDF i zakresu stron, kliknij przycisk **"Convert"**, aby rozpocząć proces konwersji.
2.  **Obserwuj postęp.** Aplikacja wyświetli pasek postępu, informację o aktualnie przetwarzanej stronie, szacowany czas zakończenia i prędkość przetwarzania. Wyniki konwersji będą wyświetlane w formie tabeli poniżej w czasie rzeczywistym.
3.  **Oczekiwanie na zakończenie.** Proces konwersji może potrwać od kilku sekund do kilku minut, w zależności od rozmiaru dokumentu PDF, liczby stron i szybkości Gemini API. Po zakończeniu konwersji, aplikacja wyświetli komunikat **"Conversion complete."**.

### 6. Zatrzymywanie Konwersji

*   **Przycisk "STOP".** W trakcie konwersji możesz w dowolnym momencie kliknąć przycisk **"STOP"**, aby przerwać proces. Aplikacja wyświetli komunikat **"Conversion stopped by user."**.

### 7. Pobieranie Wyników CSV

1.  **Kliknij przycisk "Download CSV".** Po zakończeniu konwersji (lub jej zatrzymaniu), pojawi się przycisk **"Download CSV"**.
2.  **Zapisz plik CSV.** Kliknij przycisk **"Download CSV"** i zapisz wygenerowany plik CSV (`result.csv`) na dysku lokalnym. Plik CSV będzie zawierał dane tabelaryczne wyekstrahowane z dokumentu PDF.

### 8. Resetowanie Aplikacji

*   **Przycisk "Od nowa".** Aby zresetować aplikację i rozpocząć nową konwersję, kliknij przycisk **"Od nowa"**. Spowoduje to wyczyszczenie wszystkich danych, w tym wczytanego pliku PDF, zakresu stron i wyników konwersji. Aplikacja zostanie przywrócona do stanu początkowego.

## Przykład Użycia z Raportem ENEA

Poniżej przedstawiono przykład użycia aplikacji z raportem ENEA "Publikacja podmiotów 31_12_2024r.pdf", którego URL został podany:

`https://operator.enea.pl/uploads-ev2/Operator/ospolce/raporty/Publikacja_podmiot%C3%B3w_31_12_2024r..pdf`

1.  **Uruchom aplikację PDF to CSV Converter.**
2.  **Wprowadź klucz API Gemini** (lub upewnij się, że zmienna środowiskowa `GEMINI_API_KEY` jest ustawiona).
3.  **Wybierz "Enter PDF URL".**
4.  **Wklej URL raportu ENEA** w polu "Enter PDF URL:":
    ```
    https://operator.enea.pl/uploads-ev2/Operator/ospolce/raporty/Publikacja_podmiot%C3%B3w_31_12_2024r..pdf
    ```
5.  **Ustaw zakres stron.** Domyślnie aplikacja powinna wczytać cały raport. Możesz dostosować zakres stron, jeśli chcesz przetworzyć tylko wybrane strony. Na przykład, aby przetworzyć strony od 1 do 5, ustaw "Start Page" na 1 i "End Page" na 5.
6.  **Kliknij "Convert".**
7.  **Poczekaj na zakończenie konwersji.** Aplikacja będzie przetwarzać strony raportu i wyświetlać wyniki w tabeli.
8.  **Pobierz plik CSV.** Po zakończeniu konwersji, kliknij "Download CSV", aby zapisać wygenerowany plik CSV z danymi z raportu ENEA.

## Kluczowe Funkcje Aplikacji

*   **Wsparcie Gemini API:** Wykorzystanie zaawansowanego modelu językowego Gemini do dokładnej ekstrakcji danych tabelarycznych.
*   **Elastyczność źródła PDF:** Możliwość wczytywania PDF zarówno z plików lokalnych, jak i URL-i.
*   **Precyzyjny zakres stron:** Użytkownik ma pełną kontrolę nad zakresem stron do konwersji.
*   **Interaktywny interfejs:** Streamlit zapewnia intuicyjny i responsywny interfejs użytkownika.
*   **Dynamiczne wyświetlanie tabeli:** Wyniki konwersji są prezentowane w formie tabeli na bieżąco.
*   **Wskaźniki postępu:** Informacje o postępie, czasie i prędkości przetwarzania zapewniają lepsze doświadczenie użytkownika.
*   **Opcja zatrzymania i resetu:** Umożliwia użytkownikowi kontrolę nad procesem i łatwe rozpoczęcie nowej konwersji.

## Zależności i Konfiguracja

**Zależności:**

*   `streamlit`
*   `PyPDF2`
*   `requests`
*   `python-dotenv`
*   `google-generativeai`
*   `pandas`
*   `csv`
*   `stqdm`

**Konfiguracja:**

*   **Klucz API Gemini:** Wymagany klucz API Gemini, który można wprowadzić w aplikacji lub ustawić jako zmienną środowiskową `GEMINI_API_KEY`.
*   **Zmienne środowiskowe:** Opcjonalnie, ustaw zmienną środowiskową `GEMINI_API_KEY` zamiast wprowadzania klucza API w aplikacji.

## Rozwiązywanie Problemów

*   **Błąd API Key:** Jeśli aplikacja wyświetla błąd związany z kluczem API, upewnij się, że klucz został poprawnie wprowadzony lub zmienna środowiskowa `GEMINI_API_KEY` jest poprawnie ustawiona. Sprawdź, czy klucz API jest aktywny w Google AI Studio.
*   **Błąd odczytu PDF:** Jeśli aplikacja nie może odczytać pliku PDF lub URL, upewnij się, że plik PDF nie jest uszkodzony i URL jest poprawny oraz dostępny. W przypadku URL, sprawdź połączenie internetowe.
*   **Błąd parsowania CSV:** Jeśli aplikacja wyświetla ostrzeżenia dotyczące parsowania CSV z niektórych stron, oznacza to, że model Gemini API mógł niepoprawnie wygenerować format CSV dla tych stron. Sprawdź surowy output CSV (w opcjonalnym polu tekstowym, jeśli jest włączone) i spróbuj ponownie przekonwertować te strony lub dostosować zakres stron.
*   **Niska prędkość konwersji:** Prędkość konwersji zależy od obciążenia serwerów Gemini API i szybkości połączenia internetowego. Aplikacja ma wbudowane opóźnienie między zapytaniami (6 sekund), aby uniknąć przekroczenia limitu zapytań API.
*   **Niekompletne dane CSV:** W przypadku bardzo skomplikowanych tabel w PDF, model Gemini API może nie wyekstrahować wszystkich danych poprawnie. Sprawdź wygenerowany plik CSV i porównaj go z oryginalnym PDF, aby zidentyfikować ewentualne braki lub błędy. W takim przypadku, może być konieczne ręczne poprawienie pliku CSV.

Mam nadzieję, że ta dokumentacja jest pomocna w korzystaniu z aplikacji PDF to CSV Converter! Jeśli masz jakiekolwiek pytania, uwagi lub sugestie, daj mi znać. Dziękuję za korzystanie z aplikacji i życzę owocnej konwersji PDF na CSV! 📄➡️📊