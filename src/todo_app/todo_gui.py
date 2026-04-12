import tkinter as tk
from queue import Empty, Queue
from tkinter import ttk

class TodoGuiApp:
    def __init__(self, store, on_close=None):
        self.store = store
        self.on_close = on_close
        self.update_queue = Queue()

        self.root = tk.Tk()
        self.root.title("ToDo Antler")
        self.root.geometry("1280x780")
        self.root.minsize(1000, 640)
        self.root.attributes("-topmost", True)

        self.status_var = tk.StringVar(value="Tryb wizualizacji: wpisuj komendy w konsoli.")

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(100, self._process_queue, None)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="ToDo Antler - podglad na zywo z konsoli", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

        panes = ttk.PanedWindow(main, orient="horizontal")
        panes.pack(fill="both", expand=True, pady=(0, 10))

        self.main_frame = ttk.LabelFrame(panes, text="Aktualny widok", padding=10)

        self.deps_frame = ttk.LabelFrame(panes, text="Zależności", padding=10)

        panes.add(self.main_frame, weight=3)
        panes.add(self.deps_frame, weight=2)

        self.main_tree = ttk.Treeview(self.main_frame, show="headings")
        main_y_scroll = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.main_tree.yview)
        main_x_scroll = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.main_tree.xview)
        self.main_tree.configure(yscrollcommand=main_y_scroll.set, xscrollcommand=main_x_scroll.set)

        self.main_tree.grid(row=0, column=0, sticky="nsew")
        main_y_scroll.grid(row=0, column=1, sticky="ns")
        main_x_scroll.grid(row=1, column=0, sticky="ew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self.deps_tree = ttk.Treeview(self.deps_frame, show="headings")
        deps_y_scroll = ttk.Scrollbar(self.deps_frame, orient="vertical", command=self.deps_tree.yview)
        deps_x_scroll = ttk.Scrollbar(self.deps_frame, orient="horizontal", command=self.deps_tree.xview)
        self.deps_tree.configure(yscrollcommand=deps_y_scroll.set, xscrollcommand=deps_x_scroll.set)

        self.deps_tree.grid(row=0, column=0, sticky="nsew")
        deps_y_scroll.grid(row=0, column=1, sticky="ns")
        deps_x_scroll.grid(row=1, column=0, sticky="ew")
        self.deps_frame.rowconfigure(0, weight=1)
        self.deps_frame.columnconfigure(0, weight=1)

        self._configure_table(self.main_tree, "ALL")
        self._configure_table(self.deps_tree, "DEPENDENCIES")

        ttk.Label(main, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", pady=(8, 0))

    def post_update(self, command, message, view, rows):
        self.update_queue.put((command, message, view, rows))

    def request_close(self):
        self.root.after(0, self._on_close, None)

    def _process_queue(self, *args):
        try:
            while True:
                command, message, view, rows = self.update_queue.get_nowait()
                self._render_rows(view, rows)
                self._render_dependency_rows(self.store.fetch_tasks("DEPENDENCIES"))
                self._set_status(f"{message} | Ostatnia komenda: {command}")
        except Empty:
            pass

        self.root.after(100, self._process_queue, None)

    def _render_rows(self, view, rows):
        self._configure_table(self.main_tree, view)
        for item in self.main_tree.get_children():
            self.main_tree.delete(item)

        for row in rows:
            self.main_tree.insert("", "end", values=self._map_row(view, row))

        self._set_status(f"Widok: {view} | Rekordy: {len(rows)}")

    def _render_dependency_rows(self, rows):
        self._configure_table(self.deps_tree, "DEPENDENCIES")
        for item in self.deps_tree.get_children():
            self.deps_tree.delete(item)

        for row in rows:
            self.deps_tree.insert("", "end", values=self._map_row("DEPENDENCIES", row))

    def _configure_table(self, tree, view):
        if view == "DEPENDENCIES":
            columns = ("id", "name", "deps")
            headers = {"id": "ID", "name": "Zadanie", "deps": "Zaleznosci"}
            widths = {"id": 60, "name": 240, "deps": 220}
            stretch_map = {"id": False, "name": True, "deps": True}
        else:
            columns = ("id", "status", "priority", "deadline", "name", "note")
            headers = {
                "id": "ID",
                "status": "Status",
                "priority": "Priorytet",
                "deadline": "Deadline",
                "name": "Zadanie",
                "note": "Notatka",
            }
            widths = {"id": 55, "status": 70, "priority": 70, "deadline": 105, "name": 360, "note": 280}
            stretch_map = {
                "id": False,
                "status": False,
                "priority": False,
                "deadline": False,
                "name": True,
                "note": True,
            }

        tree["columns"] = columns
        for c in columns:
            tree.heading(c, text=headers[c])
            tree.column(c, width=widths[c], minwidth=50, anchor="w", stretch=stretch_map[c])

    def _map_row(self, view, row):
        if view == "DEPENDENCIES":
            return (row["id"], row["name"], row["deps"] or "-")

        priority_map = {1: "LOW", 2: "MEDIUM", 3: "HIGH"}
        return (
            row["id"],
            row["status"],
            priority_map.get(row["priority"], "LOW"),
            row["deadline"] or "",
            row["name"],
            row["note"] or "",
        )

    def _set_status(self, text):
        self.status_var.set(text)

    def _on_close(self, *args):
        if self.on_close is not None:
            self.on_close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()











