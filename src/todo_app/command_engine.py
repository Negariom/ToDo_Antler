import json
import re
from dataclasses import dataclass, field

from antlr4 import CommonTokenStream, InputStream

from todoParserLexer import todoParserLexer
from todoParserParser import todoParserParser
from .todo_visitor import TodoVisitor


@dataclass
class CommandResult:
    ok: bool
    message: str
    view: str = "ALL"
    rows: list = field(default_factory=list)
    exit_requested: bool = False


class TodoCommandEngine:
    def __init__(self, store, default_view="ALL"):
        self.store = store
        self.default_view = default_view
        self.visitor = TodoVisitor(store)

    def execute(self, line):
        text = line.strip()
        if not text:
            return CommandResult(False, "Wpisz polecenie.", self.default_view, self.store.fetch_tasks(self.default_view))

        if text.lower() in ("exit", "quit"):
            return CommandResult(True, "Zamykanie aplikacji...", self.default_view, self.store.fetch_tasks(self.default_view), True)

        edit_result = self._handle_edit(text)
        if edit_result is not None:
            return edit_result

        input_stream = InputStream(text)
        lexer = todoParserLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = todoParserParser(tokens)
        tree = parser.command()

        if parser.getNumberOfSyntaxErrors() > 0:
            return CommandResult(False, "Blad skladni.", self.default_view, self.store.fetch_tasks(self.default_view))

        try:
            self.visitor.visit(tree)
        except ValueError as exc:
            return CommandResult(False, str(exc), self.default_view, self.store.fetch_tasks(self.default_view))

        view = self._resolve_view(text)
        return CommandResult(True, "Polecenie wykonane.", view, self.store.fetch_tasks(view))

    def _handle_edit(self, text):
        if not text.upper().startswith("EDIT"):
            return None

        match = re.match(r'^EDIT\s+(\d+)\b(.*)$', text, flags=re.IGNORECASE)
        if not match:
            return CommandResult(
                False,
                'Niepoprawna skladnia. Uzyj: EDIT <ID> ["Nowa nazwa"] [PRIORITY LOW|MEDIUM|HIGH] [DEADLINE YYYY-MM-DD]',
                self.default_view,
                self.store.fetch_tasks(self.default_view),
            )

        task_id = int(match.group(1))
        rest = (match.group(2) or "").strip()
        new_name = None
        priority = None
        deadline = None

        name_match = re.match(r'^("(?:[^"\\]|\\.)*")', rest)
        if name_match:
            try:
                new_name = json.loads(name_match.group(1))
            except json.JSONDecodeError:
                return CommandResult(False, "Niepoprawny tekst w cudzyslowie.", self.default_view, self.store.fetch_tasks(self.default_view))
            rest = rest[name_match.end():].strip()

        priority_match = re.match(r'^PRIORITY\s+(LOW|MEDIUM|HIGH)\b', rest, flags=re.IGNORECASE)
        if priority_match:
            priority_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
            priority = priority_map[priority_match.group(1).upper()]
            rest = rest[priority_match.end():].strip()

        deadline_match = re.match(r'^DEADLINE\s+([0-9]{4}-[0-9]{2}-[0-9]{2})\b', rest, flags=re.IGNORECASE)
        if deadline_match:
            deadline = deadline_match.group(1)
            rest = rest[deadline_match.end():].strip()

        if rest:
            return CommandResult(
                False,
                'Niepoprawna skladnia. Uzyj: EDIT <ID> ["Nowa nazwa"] [PRIORITY LOW|MEDIUM|HIGH] [DEADLINE YYYY-MM-DD]',
                self.default_view,
                self.store.fetch_tasks(self.default_view),
            )

        if new_name is None and priority is None and deadline is None:
            return CommandResult(
                False,
                'Podaj co najmniej jedno pole do edycji: "nazwa", PRIORITY lub DEADLINE.',
                self.default_view,
                self.store.fetch_tasks(self.default_view),
            )

        try:
            self.store.edit_task(task_id, new_name, priority=priority, deadline=deadline)
        except ValueError as exc:
            return CommandResult(False, str(exc), self.default_view, self.store.fetch_tasks(self.default_view))

        return CommandResult(True, "Zadanie zaktualizowane.", self.default_view, self.store.fetch_tasks(self.default_view))

    def _resolve_view(self, text):
        upper = text.strip().upper()
        if upper.startswith("LIST"):
            if "DEPENDENCIES" in upper:
                return "DEPENDENCIES"
            if "DONE" in upper:
                return "DONE"
            if "ALL" in upper:
                return "ALL"
            return "ACTIVE"
        return self.default_view


