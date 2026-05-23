import sys
import platform
import shutil
from pathlib import Path


def run(args):
    py_version     = platform.python_version()
    os_info        = f"{platform.system()} {platform.release()}"
    tshark_version = "Not found"

    tshark_bin = shutil.which("tshark") or "/usr/bin/tshark"
    if Path(tshark_bin).exists():
        try:
            import subprocess
            result = subprocess.run(
                [tshark_bin, "--version"],
                capture_output=True, text=True
            )
            first_line     = result.stdout.splitlines()[0] if result.stdout else ""
            tshark_version = first_line.split("(")[0].strip() if first_line else "Unknown"
        except Exception:
            tshark_version = "Found (version unknown)"

    return f"""
KeyTrace
─────────────────────────────────────────────────────
  KeyTrace version  : 1.0.0
  Python            : {py_version}
  Platform          : {os_info}
  tshark            : {tshark_version}
─────────────────────────────────────────────────────
  Heat. Shape. Ship.
─────────────────────────────────────────────────────
"""