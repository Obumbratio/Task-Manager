#!/usr/bin/env python3
import json, argparse, os, datetime
from json import JSONDecodeError

DB = "tasks.json"

# ---------- Utilidades de persistencia ----------
def load():
    """Carga la lista de tareas desde tasks.json. Si no existe o está corrupto, devuelve []."""
    if not os.path.exists(DB):
        return []
    try:
        with open(DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            print("⚠️  Formato inesperado en tasks.json: se esperaba una lista. Se usará lista vacía.")
            return []
    except JSONDecodeError:
        print("⚠️  tasks.json está corrupto o mal formado. Se usará lista vacía.")
        return []

def save(tasks):
    """Guarda la lista de tareas con formato legible."""
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def next_id(tasks):
    """ID robusto: 1 + máximo ID existente (así evitarás duplicados si borras una tarea)."""
    return (max((t.get("id", 0) for t in tasks), default=0) + 1)

# ---------- Acciones ----------
def add_task(text: str):
    text = (text or "").strip()
    if not text:
        print("❌ No se puede agregar una tarea vacía. Usa:  add \"Descripción de la tarea\"")
        return
    tasks = load()
    tasks.append({
        "id": next_id(tasks),
        "text": text,
        "done": False,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds")
    })
    save(tasks)
    print(f"✅ Tarea agregada: \"{text}\"")

def list_tasks():
    tasks = load()
    if not tasks:
        print("🗒️  No hay tareas.")
        return
    done_count = sum(1 for t in tasks if t.get("done"))
    for t in tasks:
        status = "✔" if t.get("done") else "⏳"
        print(f'{t.get("id", "?"):>3} {status} {t.get("text","(sin texto)")}  ({t.get("created_at","")})')
    print(f"\n📊 Resumen: {len(tasks)} tareas | {done_count} completadas | {len(tasks)-done_count} pendientes")

def done_task(task_id: int):
    if task_id <= 0:
        print("❌ ID inválido. El ID debe ser un entero positivo.")
        return
    tasks = load()
    for t in tasks:
        if t.get("id") == task_id:
            if t.get("done"):
                print(f"ℹ️  La tarea {task_id} ya estaba marcada como completada.")
            else:
                t["done"] = True
                save(tasks)
                print(f"✅ Tarea {task_id} marcada como completada.")
            return
    print(f"⚠️  ID no encontrado: {task_id}")

def delete_task(task_id: int):
    """Elimina UNA tarea por ID sin renumerar las demás (IDs quedan estables)."""
    if task_id <= 0:
        print("❌ ID inválido. El ID debe ser un entero positivo.")
        return
    tasks = load()
    new_tasks = [t for t in tasks if t.get("id") != task_id]
    if len(new_tasks) == len(tasks):
        print(f"⚠️  ID no encontrado: {task_id}")
        return
    save(new_tasks)
    print(f"🗑️  Tarea {task_id} eliminada.")

def clear_tasks():
    save([])
    print("🧹 Lista limpiada.")

# ---------- CLI ----------
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Task Manager CLI")
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("add", help='Agregar una tarea'); a.add_argument("text")
    sub.add_parser("list", help='Listar tareas')
    d = sub.add_parser("done", help='Marcar tarea como completada'); d.add_argument("id", type=int)
    x = sub.add_parser("delete", help='Eliminar tarea por ID'); x.add_argument("id", type=int)
    sub.add_parser("clear", help='Borrar TODAS las tareas')

    args = p.parse_args()
    if args.cmd == "add": add_task(args.text)
    elif args.cmd == "list": list_tasks()
    elif args.cmd == "done": done_task(args.id)
    elif args.cmd == "delete": delete_task(args.id)
    elif args.cmd == "clear": clear_tasks()
    else:
        p.print_help()
