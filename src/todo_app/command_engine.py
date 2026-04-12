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


