import json

from todoParserParser import todoParserParser
from todoParserVisitor import todoParserVisitor


class TodoVisitor(todoParserVisitor):
    def __init__(self, store):
        self.store = store

    def visitProgram(self, ctx: todoParserParser.ProgramContext):
        for line_ctx in ctx.line():
            self.visit(line_ctx)
        return None

    def visitLine(self, ctx: todoParserParser.LineContext):
        if ctx.command() is not None:
            self.visit(ctx.command())
        return None

    def visitAddCommand(self, ctx: todoParserParser.AddCommandContext):
        raw_text = ctx.STRING().getText()
        text = json.loads(raw_text)
        self.store.add(text)
        return None

    def visitDoneCommand(self, ctx: todoParserParser.DoneCommandContext):
        self.store.done(int(ctx.INT().getText()))
        return None

    def visitDeleteCommand(self, ctx: todoParserParser.DeleteCommandContext):
        self.store.delete(int(ctx.INT().getText()))
        return None

    def visitListCommand(self, ctx: todoParserParser.ListCommandContext):
        self.store.showList()
        return None
