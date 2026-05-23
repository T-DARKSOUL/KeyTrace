import sys
from pathlib import Path

def run(args):
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from start_keytrace import start_keytrace
        start_keytrace()
        keylog = Path.home() / "keytrace_sslkeylogfile.txt"
        return f"[OK] SSLKEYLOGFILE created and configured.\n     Path: {keylog}"
    except Exception as e:
        return f"[ERR] Failed: {e}"
