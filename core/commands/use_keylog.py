import os
from pathlib import Path

def run(args):
    if not args:
        return "[ERR] Usage: use-keylog <path>"
    path = Path(args[0])
    if not path.exists():
        return f"[ERR] File not found: {path}"
    os.environ["SSLKEYLOGFILE"] = str(path)
    size = path.stat().st_size
    return f"[OK] Now using keylog: {path}\n     Size: {size:,} bytes"
