import sys
import importlib
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

def _load(name):
    return importlib.import_module(f"core.commands.{name}")

def _build_commands():
    return {
        "help":          _load("help").run,
        "create-keylog": _load("create_keylog").run,
        "use-keylog":    _load("use_keylog").run,
        "show-config":   _load("show_config").run,
        "decrypt":       _load("decrypt").run,
        "status":        _load("status").run,
        "version":       _load("version").run,
        "clear-keylog":  _load("clear_keylog").run,
        "open":          _load("open_file").run,
        "list-scans":    _load("list_scans").run,
        "interfaces":    _load("interfaces").run,
        "capture":       _load("capture").run,
        "filter":        _load("filter").run,
        "clear":         lambda args: "__CLEAR__",
    }

def dispatch(command_line: str) -> str:
    command_line = command_line.strip()
    if not command_line:
        return ""
    parts   = command_line.split()
    command = parts[0]
    args    = parts[1:]
    try:
        COMMANDS = _build_commands()
    except Exception as e:
        return f"[ERR] Failed to load commands: {e}"
    if command not in COMMANDS:
        return (
            f"[KeyTrace] Unknown command: '{command}'\n"
            f"           Type 'help' to see available commands."
        )
    try:
        return COMMANDS[command](args)
    except Exception as e:
        return f"[ERR] Command '{command}' failed: {e}"
