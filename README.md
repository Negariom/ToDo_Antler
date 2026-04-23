# ToDoAntler - zarządzanie zadaniami (CLI + podgląd GUI)

ToDoAntler to projekt oparty o własny DSL parsowany przez **ANTLR v4** i zapisywany w **SQLite**. Komendy wpisujesz w konsoli, a GUI (`tkinter`) pokazuje na żywo wizualizację listy zadań i zależności.

## Główne funkcje

- dodawanie zadań (`ADD`)
- priorytety (`LOW`, `MEDIUM`, `HIGH`)
- deadline (`DEADLINE YYYY-MM-DD`)
- zależności między zadaniami (`DEPENDS ON ...`)
- notatki do zadań (`NOTE`)
- edycja nazwy, priorytetu i deadline'u zadania (`EDIT`)
- oznaczanie wykonania (`DONE`)
- usuwanie (`DELETE`)
- widoki listy (`LIST`, `LIST ALL`, `LIST DONE`, `LIST DEPENDENCIES`)
- blokada cyklicznych zależności
- komendy case-insensitive (`ADD`, `add`, `AdD` działają tak samo)

## Jak uruchomić

1. Zainstaluj wymagania.
2. Uruchom `src/main.py`.
3. Wpisuj komendy w terminalu - GUI odświeża się automatycznie.

```bash
pip install -r requirements.txt
python src/main.py
```

## Składnia komend

### 1) Dodawanie zadania
```text
ADD "Nazwa zadania" [PRIORITY LOW|MEDIUM|HIGH] [DEADLINE YYYY-MM-DD] [DEPENDS ON id1,id2] [NOTE "Treść notatki"]
```

Przykłady:
```text
ADD "Kupic mleko"
ADD "Wyslac raport" PRIORITY HIGH DEADLINE 2026-04-30
ADD "Pomalowac salon" DEPENDS ON 7,8 NOTE "Po remoncie"
```

### 2) Oznaczenie jako zrobione
```text
DONE <ID_ZADANIA>
```

### 3) Usunięcie zadania
```text
DELETE <ID_ZADANIA>
```

### 4) Edycja notatki
```text
NOTE <ID_ZADANIA> "Nowa treść notatki"
```

### 5) Edycja nazwy zadania
```text
EDIT <ID_ZADANIA> ["Nowa nazwa zadania"] [PRIORITY LOW|MEDIUM|HIGH] [DEADLINE YYYY-MM-DD]
```

Przykłady:
```text
EDIT 3 "Nowa nazwa"
EDIT 3 PRIORITY HIGH
EDIT 3 DEADLINE 2026-05-01
EDIT 3 "Nowa nazwa" PRIORITY MEDIUM DEADLINE 2026-05-10
```

### 6) Widoki listy

- `LIST` - aktywne zadania (niewykonane i odblokowane)
- `LIST ALL` - wszystkie zadania
- `LIST DONE` - tylko wykonane
- `LIST DEPENDENCIES` - podgląd zależności

## Architektura

- `grammar/todoParser.g4` - definicja DSL
- `gen/` - wygenerowane pliki lexer/parser/visitor ANTLR
- `src/main.py` - minimalny punkt wejścia
- `src/todo_app/app_runner.py` - uruchamia równolegle konsolę i GUI
- `src/todo_app/command_engine.py` - parsuje komendę i zwraca wynik dla UI/CLI
- `src/todo_app/todo_visitor.py` - mapuje drzewo ANTLR na operacje na magazynie
- `src/todo_app/todo_store.py` - operacje SQLite i logika widoków
- `src/todo_app/todo_gui.py` - okno podglądu danych

## Baza danych

Plik bazy: `src/todo.db`.

Tabele:

- `tasks` - główna tabela z zadaniami
- `task_dependencies` - relacje zależności między zadaniami

## Regeneracja parsera (tylko po zmianie gramatyki)

Pliki w `gen/` są już w repo. Komenda poniżej jest potrzebna tylko, gdy edytujesz `grammar/todoParser.g4`:

```bash
antlr4 -Dlanguage=Python3 -visitor -o gen grammar/todoParser.g4
```


