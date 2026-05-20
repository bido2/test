import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional

from flask import Flask, jsonify, request, send_from_directory


DATA_FILE = "todos.json"

app = Flask(__name__, static_folder="webapp", static_url_path="")


@dataclass
class Todo:
    id: int
    text: str
    due: Optional[str] = None
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
        return []


def save_todos(todos: List[Todo], path: str = DATA_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in todos], f, indent=2, ensure_ascii=False)


def next_id(todos: List[Todo]) -> int:
    return (max((t.id for t in todos), default=0) + 1)


def find_task(todos: List[Todo], task_id: int) -> Optional[Todo]:
    for t in todos:
        if t.id == task_id:
            return t
    return None


def todos_to_json(todos: List[Todo]):
    return [asdict(t) for t in todos]


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/todos")
def api_list_todos():
    todos = load_todos()
    todos = sorted(todos, key=lambda t: (t.done, t.id))
    return jsonify({"todos": todos_to_json(todos)})


@app.post("/api/todos")
def api_add_todo():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    due = (data.get("due") if data.get("due") is not None else None)

    if not text:
        return jsonify({"error": "text is required"}), 400

    if isinstance(due, str):
        due = due.strip() or None

    todos = load_todos()
    t = Todo(
        id=next_id(todos),
        text=text,
        due=due,
        done=False,
        created_at=_now_iso(),
    )
    todos.append(t)
    save_todos(todos)
    return jsonify({"ok": True, "todo": asdict(t)}), 201


@app.post("/api/todos/<int:task_id>/toggle")
def api_toggle_todo(task_id: int):
    todos = load_todos()
    task = find_task(todos, task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404
    task.done = not task.done
    save_todos(todos)
    return jsonify({"ok": True, "todo": asdict(task)})


@app.delete("/api/todos/<int:task_id>")
def api_delete_todo(task_id: int):
    todos = load_todos()
    before = len(todos)
    todos = [t for t in todos if t.id != task_id]
    if len(todos) == before:
        return jsonify({"error": "task not found"}), 404
    save_todos(todos)
    return jsonify({"ok": True})


if __name__ == "__main__":
    # Default port 5000.
    app.run(host="127.0.0.1", port=5000, debug=True)

