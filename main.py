import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional


DATA_FILE = "todos.json"


@dataclass
class Todo:
    id: int
    text: str
    due: Optional[str] = None  # stored as string (e.g. 2026-05-20)
    done: bool = False
    created_at: str = ""


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_todos(path: str = DATA_FILE) -> List[Todo]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        todos: List[Todo] = []
        for item in raw:
            todos.append(Todo(**item))
        return todos
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        # If file is corrupted, don't crash the app; start fresh.
        return []


def save_todos(todos: List[Todo], path: str = DATA_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in todos], f, indent=2, ensure_ascii=False)


def next_id(todos: List[Todo]) -> int:
    return (max((t.id for t in todos), default=0) + 1)


def prompt_nonempty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("✖ Input cannot be empty. Please try again.")


def prompt_due(prompt: str) -> Optional[str]:
    while True:
        s = input(prompt).strip()
        if not s:
            return None

        # If it looks like YYYY-MM-DD, validate it; otherwise treat as free text.
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            try:
                datetime.strptime(s, "%Y-%m-%d")
                return s
            except ValueError:
                print("✖ Invalid date format. Use YYYY-MM-DD (or press Enter to skip).")
                continue

        return s


def print_header() -> None:
    width = 54
    title = "TO-DO LIST"
    subtitle = f"Data: {DATA_FILE}"

    print("\n" + "═" * width)
    print("║" + title.center(width - 2) + "║")
    print("║" + subtitle.center(width - 2) + "║")
    print("╚" + "═" * (width - 2) + "╝")


def print_menu() -> None:
    options = [
        ("1", "Add task"),
        ("2", "List tasks"),
        ("3", "Toggle complete"),
        ("4", "Delete task"),
        ("5", "Exit"),
    ]

    print("")
    for k, label in options:
        print(f"  [{k}] {label}")


def list_tasks(todos: List[Todo]) -> None:
    print("")
    if not todos:
        print("• No tasks yet. Add one to get started.")
        return

    ordered = sorted(todos, key=lambda t: (t.done, t.id))
    total = len(todos)
    done_count = sum(1 for t in todos if t.done)

    print(f"• {done_count}/{total} completed")
    print("—" * 54)

    for t in ordered:
        status = "✅" if t.done else "⬜"
        due_part = f" | due: {t.due}" if t.due else ""
        created_part = f" | created: {t.created_at}" if t.created_at else ""
        print(f"[{t.id:>3}] {status} {t.text}{due_part}{created_part}")

    print("—" * 54)


def find_task(todos: List[Todo], task_id: int) -> Optional[Todo]:
    for t in todos:
        if t.id == task_id:
            return t
    return None


def main() -> None:
    todos = load_todos()

    while True:
        os.system("cls")
        print_header()
        print_menu()
        print("")

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            text = prompt_nonempty("Task description: ")
            due = prompt_due("Due date (YYYY-MM-DD, optional): ")
            t = Todo(
                id=next_id(todos),
                text=text,
                due=due,
                done=False,
                created_at=_now_iso(),
            )
            todos.append(t)
            save_todos(todos)
            print("✓ Added.")
            input("Press Enter to continue...")

        elif choice == "2":
            list_tasks(todos)
            input("Press Enter to continue...")

        elif choice == "3":
            if not todos:
                print("• No tasks to update.")
                input("Press Enter to continue...")
                continue

            list_tasks(todos)
            raw = input("Enter task id to toggle complete: ").strip()
            if not raw.isdigit():
                print("✖ Invalid id.")
                input("Press Enter to continue...")
                continue

            task = find_task(todos, int(raw))
            if not task:
                print("✖ Task id not found.")
                input("Press Enter to continue...")
                continue

            task.done = not task.done
            save_todos(todos)
            print(f"✓ Updated: task {task.id} is now {'done' if task.done else 'not done'}.")
            input("Press Enter to continue...")

        elif choice == "4":
            if not todos:
                print("• No tasks to delete.")
                input("Press Enter to continue...")
                continue

            list_tasks(todos)
            raw = input("Enter task id to delete: ").strip()
            if not raw.isdigit():
                print("✖ Invalid id.")
                input("Press Enter to continue...")
                continue

            task_id = int(raw)
            before = len(todos)
            todos = [t for t in todos if t.id != task_id]
            after = len(todos)

            if after == before:
                print("✖ Task id not found.")
                input("Press Enter to continue...")
                continue

            save_todos(todos)
            print("✓ Deleted.")
            input("Press Enter to continue...")

        elif choice == "5":
            save_todos(todos)
            print("Goodbye! ✨")
            break

        else:
            print("✖ Invalid option. Choose 1-5.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    # Kept for CLI version (optional). The HTML UI uses app.py.
    main()

