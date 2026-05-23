import shutil
from pathlib import Path


def run(args):
    tshark_bin = shutil.which("tshark") or "/usr/bin/tshark"

    if not Path(tshark_bin).exists():
        return (
            "[ERR] tshark not found.\n"
            "      Install it first:\n"
            "      Linux:  sudo apt install tshark\n"
            "      macOS:  brew install wireshark"
        )

    try:
        import subprocess
        result = subprocess.run(
            [tshark_bin, "-D"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"[ERR] tshark error:\n{result.stderr.strip()}"

        lines    = result.stdout.strip().splitlines()
        header   = [
            "\nAvailable Network Interfaces",
            "─" * 52,
        ]
        ifaces   = [f"  {line}" for line in lines]
        footer   = [
            "─" * 52,
            "Use the interface name or number with: capture <interface>",
        ]

        return "\n".join(header + ifaces + footer)

    except Exception as e:
        return f"[ERR] Could not list interfaces: {e}"