import threading

from .command_engine import TodoCommandEngine
from .todo_gui import TodoGuiApp
from .todo_store import TodoStore


def run_app():
    stop_event = threading.Event()
    store = TodoStore()
    engine = TodoCommandEngine(store, default_view="ALL")
    gui_closed = {"value": False}

    def on_gui_close():
        gui_closed["value"] = True
        stop_event.set()

    gui = TodoGuiApp(store, on_close=on_gui_close)
    gui.post_update("START", "Wizualizacja uruchomiona. Wpisuj komendy w konsoli.", "ALL", store.fetch_tasks("ALL"))

    def console_loop():
        print("TODO CLI + GUI. Komendy:")
        print("  ADD \"tekst\" [PRIORITY LOW|MEDIUM|HIGH] [DEADLINE YYYY-MM-DD] [DEPENDS ON id1,id2] [NOTE \"notatka\"]")
        print("  DONE n")
        print("  DELETE n")
        print("  NOTE n \"nowa notatka\"")
        print("  LIST [ALL|DONE|DEPENDENCIES]")
        print("Wyjscie: exit lub quit")

        while not stop_event.is_set():
            try:
                line = input("> ").strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                break

            if not line:
                continue

            result = engine.execute(line)
            if not result.ok:
                print(result.message)

            gui.post_update(line, result.message, result.view, result.rows)

            if result.exit_requested:
                stop_event.set()
                gui.request_close()
                break

        stop_event.set()

    thread = threading.Thread(target=console_loop, daemon=True)
    thread.start()

    gui.run()

    stop_event.set()
    if thread.is_alive() and not gui_closed["value"]:
        gui.request_close()
    thread.join(timeout=1.0)
    store.close()





