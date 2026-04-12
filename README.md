# ToDoAntler - System Zarządzania Zadaniami (CLI)

Zaawansowana aplikacja do zarządzania zadaniami z poziomu wiersza poleceń. Projekt wykorzystuje parser **ANTLR v4** do interpretacji spersonalizowanego języka (DSL) za pomocą własnej gramatyki, oraz bazę **SQLite** do trwałego przechowywania i filtrowania danych.

## 🚀 Główne Funkcjonalności

- **Zarządzanie Czasem**: Definiowanie terminów końcowych (Deadline) oraz śledzenie czasu wykonania zadań.
- **Priorytetyzacja**: Trzy poziomy ważności poszczególnych zadań (LOW, MEDIUM, HIGH).
- **Zależności (Task Dependencies)**: Możliwość definiowania blokad (Zadanie A zależy od Zadania B). Zablokowane zadania są ukryte ze standardowego widoku, dopóki zadanie blokujące nie zostanie wykonane. System posiada zabezpieczenie przed tworzeniem cyklicznych zależności (zakleszczeń).
- **Notatki**: Dodawanie i uaktualnianie dodatkowych notatek (opisów) do istniejących zadań.
- **Zaawansowane Widoki (Filtrowanie)**: Różnorodne perspektywy wyświetlania zadań opierające się o silnik SQL (Wszystkie, Zrobione, Graf Zależności, Domyślne Ukrywające Zablokowane).
- **Case Insensitive**: Komendy można wpisywać bez zważania na wielkość znaków (np. `ADD` / `add` / `Add`).

---

## 📝 Składnia i Lista Komend

Aplikacja dba o interaktywne przyjmowanie zapytań (REPL). Dostępne instrukcje:

### 1. Dodawanie Zadania (`ADD`)
```text
ADD "Nazwa zadania" [PRIORITY LOW|MEDIUM|HIGH] [DEADLINE YYYY-MM-DD] [DEPENDS ON id1,id2] [NOTE "Treść notatki"]
```
*Przykład:* 
`ADD "Kup mleko" PRIORITY HIGH DEADLINE 2026-04-15 NOTE "Tylko bez laktozy"`
`ADD "Zrób ciasto" PRIORITY LOW DEPENDS ON 1`

### 2. Oznaczanie jako gotowe (`DONE`)
```text
DONE <ID_ZADANIA>
```
*Przykład:* `DONE 1`

### 3. Usuwanie Zadania (`DELETE`)
```text
DELETE <ID_ZADANIA>
```
*Przykład:* `DELETE 2`

### 4. Aktualizacja Notatki (`NOTE`)
```text
NOTE <ID_ZADANIA> "Nowa treść notatki"
```
*Przykład:* `NOTE 1 "Kup jednak 2 kartony"`

### 5. Wyświetlanie Zadań (`LIST`)
Dostępne opcje widoków:
- `LIST` *(Domyślny)*: Pokazuje zadania niewykonane oraz **tylko i wyłącznie** te, których zależności zostały już spełnione (zadania nadrzędne mają status `DONE`). Sortowane po priorytecie i terminie.
- `LIST ALL`: Pokazuje wszystkie zadania niezależnie od statusu w systemie.
- `LIST DONE`: Pokazuje tylko wykonane zadania (wraz z zapisaną datą ukończenia).
- `LIST DEPENDENCIES`: Widok analityczny – zrzuca graf pokazujący pozycje i po przecinku numery identyfikatorów zależących.

---

## 🏗 Architektura Projektu

1. **`grammar/todoParser.g4`**: Plik gramatyki ANTLR. Definiuje Tokeny (słowa kluczowe, łańcuchy znaków) oraz reguły parsowania dla wszystkich operacji projektowych.
2. **`src/todo_app/todo_visitor.py`**: Przechwytuje drzewo składniowe wygenerowane przez ANTLR (AST) dla danej operacji, rozbija parametry wejściowe (wyłapuje daty, JSON-stringi na czysty tekst, tłumaczy logikę priorytetów na int) i zleca wykonanie akcji magazynowi.
3. **`src/todo_app/todo_store.py`**: Rdzeń bazodanowy. Bezpośrednio obsługuje repozytorium SQLite (`todo.db`). Przetwarza wejścia od Visitora w pełnoprawne kwerendy (DDL w czasie inicjalizacji, klauzula `WITH RECURSIVE` dla detekcji cykli oraz instrukcje SQL dla wielorakich widoków komputera wyjściowego).
4. **`src/main.py`**: Główny plik startupujący interfejs wiersza poleceń. Nawiązuje interaktywną powłokę oczekującą na wejście użytkownika i spaja parser z logiką aplikacji.

## 🛠 Struktura Bazy Danych
Model oparty o pojedynczy plik bazy `todo.db`, z minimalnym zrzutem tabel:

* **Tabela `tasks`**: Zawiera wszystkie jednostki (kolumny z id, name, status, priority, deadline, completed_at, note).
* **Tabela `task_dependencies`**: Tabela asocjacyjna służąca do ustanawiania relacji *wiele-do-wielu* pozwalających realizować blokady między poszczególnymi zadaniami.

## 🚀 Instrukcja Kompilacji

Jeśli edytujesz gramatykę (`todoParser.g4`), musisz uaktualnić (wygenerować ponownie) auto-generowane pliki interpretera w folderze projektu:

```bash
# Wymagane narzędzie antlr-tools (do generacji) oraz biblioteka wykonawcza runtime
antlr4 -Dlanguage=Python3 -visitor -o gen grammar/todoParser.g4
```

Odpalenie narzędzia lokalnie:
```bash
python src/main.py
```
