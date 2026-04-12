import sqlite3
from datetime import datetime

class TodoStore:
    def __init__(self, db_path="todo.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'TODO',
                    priority INTEGER DEFAULT 1,
                    deadline DATE,
                    completed_at TIMESTAMP,
                    note TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_id INTEGER,
                    depends_on_id INTEGER,
                    PRIMARY KEY (task_id, depends_on_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)

    def check_cycle(self, task_id, depends_on_id):
        # We check if depends_on_id eventually depends on task_id
        query = """
        WITH RECURSIVE
          deps(id) AS (
             SELECT depends_on_id FROM task_dependencies WHERE task_id = ?
             UNION
             SELECT td.depends_on_id
             FROM task_dependencies td
             JOIN deps d ON td.task_id = d.id
          )
        SELECT id FROM deps WHERE id = ?
        """
        cursor = self.conn.execute(query, (depends_on_id, task_id))
        return cursor.fetchone() is not None

    def add(self, text, priority=1, deadline=None, dependencies=None, note=None):
        if dependencies is None:
            dependencies = []

        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO tasks (name, priority, deadline, note) VALUES (?, ?, ?, ?)",
                (text, priority, deadline, note)
            )
            task_id = cursor.lastrowid
            
            for dep_id in dependencies:
                # Check if dependency exists
                dep_exists = self.conn.execute("SELECT 1 FROM tasks WHERE id = ?", (dep_id,)).fetchone()
                if not dep_exists:
                    self.conn.rollback()
                    raise ValueError(f"Zależność (ID: {dep_id}) nie istnieje!")
                
                # Insert dependency
                self.conn.execute(
                    "INSERT INTO task_dependencies (task_id, depends_on_id) VALUES (?, ?)",
                    (task_id, dep_id)
                )
        print(f"Dodano zadanie '{text}' (ID: {task_id}).")

    def edit_note(self, task_id, note_text):
        with self.conn:
            cursor = self.conn.execute("UPDATE tasks SET note = ? WHERE id = ?", (note_text, task_id))
            if cursor.rowcount == 0:
                raise ValueError(f"Zadanie o ID {task_id} nie zostało znalezione.")
        print(f"Zaktualizowano notatkę dla zadania ID {task_id}.")

    def done(self, task_id):
        with self.conn:
            cursor = self.conn.execute("UPDATE tasks SET status = 'DONE', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
            if cursor.rowcount == 0:
                raise ValueError(f"Zadanie o ID {task_id} nie zostało znalezione.")
        print(f"Oznaczono zadanie ID {task_id} jako DONE.")

    def delete(self, task_id):
        with self.conn:
            cursor = self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount == 0:
                raise ValueError(f"Zadanie o ID {task_id} nie zostało znalezione.")
        print(f"Usunięto zadanie ID {task_id}.")

    def showList(self, list_view=None):
        query = ""
        if list_view == "DONE":
            query = """
                SELECT id, name, status, priority, deadline, completed_at, note
                FROM tasks
                WHERE status = 'DONE'
                ORDER BY completed_at DESC
            """
        elif list_view == "ALL":
            query = """
                SELECT id, name, status, priority, deadline, completed_at, note
                FROM tasks
                ORDER BY priority DESC, deadline ASC
            """
        elif list_view == "DEPENDENCIES":
            query = """
                SELECT t.id, t.name, group_concat(td.depends_on_id) as deps
                FROM tasks t
                LEFT JOIN task_dependencies td ON t.id = td.task_id
                GROUP BY t.id
                ORDER BY t.id
            """
        else: # DEFAULT
            query = """
                SELECT id, name, status, priority, deadline, completed_at, note
                FROM tasks t
                WHERE status != 'DONE'
                  AND NOT EXISTS (
                      SELECT 1 FROM task_dependencies td
                      JOIN tasks t_dep ON td.depends_on_id = t_dep.id
                      WHERE td.task_id = t.id AND t_dep.status != 'DONE'
                  )
                ORDER BY priority DESC, deadline ASC
            """

        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("Brak zadań w wybranym widoku.")
            return

        for r in rows:
            if list_view == "DEPENDENCIES":
                deps_text = f" -> Zależy od: {r['deps']}" if r['deps'] else ""
                print(f"{r['id']}. {r['name']}{deps_text}")
            else:
                status_char = "x" if r['status'] == 'DONE' else " "
                pri_map = {1: 'LOW', 2: 'MEDIUM', 3: 'HIGH'}
                pri_str = pri_map.get(r['priority'], 'LOW')
                dead_str = f", DEADLINE: {r['deadline']}" if r['deadline'] else ""
                comp_str = f", ZAKOŃCZONO: {r['completed_at']}" if r['completed_at'] else ""
                note_str = f" [Notatka: {r['note']}]" if r['note'] else ""
                print(f"{r['id']}. [{status_char}] {r['name']} (PRIORITY: {pri_str}{dead_str}{comp_str}){note_str}")
