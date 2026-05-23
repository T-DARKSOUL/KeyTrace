import os
import shutil
from pathlib import Path


def run(args):
    keylog  = os.environ.get("SSLKEYLOGFILE", "Not set")
    kpath   = Path(keylog) if keylog != "Not set" else None
    k_exists = kpath.exists() if kpath else False
    k_size   = kpath.stat().st_size if k_exists else 0

    tshark_ok = shutil.which("tshark") is not None or Path("/usr/bin/tshark").exists()

    if k_size > 1024 * 1024:
        size_str = f"{k_size / 1024 / 1024:.2f} MB"
    elif k_size > 1024:
        size_str = f"{k_size / 1024:.1f} KB"
    else:
        size_str = f"{k_size} bytes"

    def check(ok):
        return "Ready    " if ok else "Not ready"

    return f"""
KeyTrace Status
─────────────────────────────────────────────────────
  tshark          {check(tshark_ok)}   {"found" if tshark_ok else "install with: sudo apt install tshark"}
  SSLKEYLOGFILE   {check(keylog != "Not set")}   {keylog}
  Keylog file     {check(k_exists)}   {"exists  " + size_str if k_exists else "not created yet — run: create-keylog"}
─────────────────────────────────────────────────────
"""