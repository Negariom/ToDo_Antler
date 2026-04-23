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

        priority = 1  # LOW is default
        if ctx.priority():
            pri_text = ctx.priority().getText().upper()
            if "MEDIUM" in pri_text:
                priority = 2
            elif "HIGH" in pri_text:
                priority = 3

        deadline = None
        if ctx.deadline():
            deadline = ctx.deadline().DATE().getText()

        dependencies = []
        if ctx.depends():
            for int_node in ctx.depends().INT():
                dependencies.append(int(int_node.getText()))

        note = None
        if ctx.note():
            # Get the STRING token from note block
            raw_note = ctx.note().STRING().getText()
            note = json.loads(raw_note)

        self.store.add(text, priority=priority, deadline=deadline, dependencies=dependencies, note=note)
        return None

    def visitEditCommand(self, ctx):
        task_id = int(ctx.INT().getText())

        new_name = None
        if ctx.STRING():
            raw_text = ctx.STRING().getText()
            new_name = json.loads(raw_text)

        priority = None
        if ctx.priority():
            pri_text = ctx.priority().getText().upper()
            if "MEDIUM" in pri_text:
                priority = 2
            elif "HIGH" in pri_text:
                priority = 3
            else:
                priority = 1

        deadline = None
        if ctx.deadline():
            deadline = ctx.deadline().DATE().getText()

        self.store.edit_task(task_id, new_name, priority=priority, deadline=deadline)
        return None

    def visitDoneCommand(self, ctx: todoParserParser.DoneCommandContext):
        self.store.done(int(ctx.INT().getText()))
        return None

    def visitDeleteCommand(self, ctx: todoParserParser.DeleteCommandContext):
        self.store.delete(int(ctx.INT().getText()))
        return None

    def visitListCommand(self, ctx: todoParserParser.ListCommandContext):
        list_view = None
        if ctx.listView():
            list_view = ctx.listView().getText().upper()
        self.store.showList(list_view=list_view)
        return None

    def visitNoteCommand(self, ctx: todoParserParser.NoteCommandContext):
        task_id = int(ctx.INT().getText())
        raw_note = ctx.STRING().getText()
        note = json.loads(raw_note)
        self.store.edit_note(task_id, note)
        return None
