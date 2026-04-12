from antlr4 import CommonTokenStream, InputStream

from todoParserLexer import todoParserLexer
from todoParserParser import todoParserParser
from todo_app.todo_store import TodoStore
from todo_app.todo_visitor import TodoVisitor


def main():
    store = TodoStore()
    visitor = TodoVisitor(store)

    print("TODO CLI. Komendy:")
    print("  ADD \"tekst\" [PRIORITY LOW|MEDIUM|HIGH] [DEADLINE YYYY-MM-DD] [DEPENDS ON id1,id2] [NOTE \"notatka\"]")
    print("  DONE n")
    print("  DELETE n")
    print("  NOTE n \"nowa notatka\"")
    print("  LIST [ALL|DONE|DEPENDENCIES]")
    print("Wyjscie: exit lub quit")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break

        input_stream = InputStream(line)
        lexer = todoParserLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = todoParserParser(tokens)

        tree = parser.command()

        if parser.getNumberOfSyntaxErrors() > 0:
            print("Blad skladni.")
            continue

        try:
            visitor.visit(tree)
        except ValueError as exc:
            print(exc)


if __name__ == "__main__":
    main()