import shutil
import subprocess
from pathlib import Path
from datetime import datetime


def run(args):
    if not args:
        return (
            "[ERR] Usage: capture <interface> [duration_seconds]\n"
            "      Example: capture eth0\n"
            "      Example: capture wlan0 30\n"
            "      Run 'interfaces' to see available interfaces."
        )

    tshark_bin = shutil.which("tshark") or "/usr/bin/tshark"
    if not Path(tshark_bin).exists():
        return "[ERR] tshark not found. Install: sudo apt install tshark"

    interface = args[0]
    duration  = int(args[1]) if len(args) > 1 and args[1].isdigit() else 30

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path.home() / "Desktop" / "KeyTrace"
    output_dir.mkdir(parents=True, exist_ok=True)
    pcap_path  = output_dir / f"capture_{interface}_{timestamp}.pcapng"

    cmd = [
        tshark_bin,
        "-i", interface,
        "-a", f"duration:{duration}",
        "-w", str(pcap_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if not pcap_path.exists() or pcap_path.stat().st_size == 0:
            return (
                f"[ERR] Capture failed or produced no output.\n"
                f"      stderr: {result.stderr.strip()}\n"
                f"      Try running KeyTrace as root: sudo python gui.py"
            )

        size = pcap_path.stat().st_size
        return (
            f"[OK] Capture complete.\n"
            f"     Interface : {interface}\n"
            f"     Duration  : {duration} seconds\n"
            f"     Saved to  : {pcap_path}\n"
            f"     Size      : {size:,} bytes\n\n"
            f"     Now decrypt it with:\n"
            f"     decrypt {pcap_path}"
        )

    except PermissionError:
        return (
            "[ERR] Permission denied.\n"
            "      Network capture requires root privileges.\n"
            "      Try: sudo python gui.py"
        )
    except Exception as e:
        return f"[ERR] Capture failed: {e}"