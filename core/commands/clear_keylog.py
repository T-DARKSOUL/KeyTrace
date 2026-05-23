import os
from pathlib import Path


def run(args):
    keylog = os.environ.get("SSLKEYLOGFILE")

    if not keylog:
        # Fall back to default path
        keylog = str(Path.home() / "keytrace_sslkeylogfile.txt")

    kpath = Path(keylog)

    if not kpath.exists():
        return (
            f"[ERR] Keylog file not found: {kpath}\n"
            f"      Run: create-keylog  to create it first."
        )

    old_size = kpath.stat().st_size

    # Wipe contents but keep the file so the env variable still points to it
    kpath.write_text("", encoding="utf-8")

    if old_size > 1024:
        old_str = f"{old_size / 1024:.1f} KB"
    else:
        old_str = f"{old_size} bytes"

    return (
        f"[OK] Keylog file cleared.\n"
        f"     Path     : {kpath}\n"
        f"     Removed  : {old_str} of session keys\n"
        f"     The file still exists and SSLKEYLOGFILE is still set.\n"
        f"     Your next browser session will start fresh."
    )