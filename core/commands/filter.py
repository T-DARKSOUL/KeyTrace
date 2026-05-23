import shutil
import subprocess
from pathlib import Path


def run(args):
    if len(args) < 2:
        return (
            "[ERR] Usage: filter <pcap_path> <display_filter>\n"
            "      Example: filter capture.pcapng http.request\n"
            "      Example: filter capture.pcapng \"ip.src == 192.168.1.1\"\n"
            "      Example: filter capture.pcapng tls"
        )

    tshark_bin = shutil.which("tshark") or "/usr/bin/tshark"
    if not Path(tshark_bin).exists():
        return "[ERR] tshark not found. Install: sudo apt install tshark"

    pcap_path     = Path(args[0])
    display_filter = " ".join(args[1:])

    if not pcap_path.exists():
        return f"[ERR] PCAP file not found: {pcap_path}"

    import os
    keylog = os.environ.get("SSLKEYLOGFILE", "")

    cmd = [
        tshark_bin,
        "-r", str(pcap_path),
        "-Y", display_filter,
        "-T", "fields",
        "-e", "frame.number",
        "-e", "ip.src",
        "-e", "ip.dst",
        "-e", "http.request.method",
        "-e", "http.request.full_uri",
        "-e", "http.response.code",
    ]

    if keylog and Path(keylog).exists():
        cmd += ["-o", f"tls.keylog_file:{keylog}"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return f"[ERR] tshark error:\n{result.stderr.strip()}"

        out = result.stdout.strip()
        if not out:
            return (
                f"[INFO] No packets matched filter: {display_filter}\n"
                f"       Try a broader filter like 'tcp' or 'http'"
            )

        lines     = out.splitlines()
        MAX_LINES = 100
        truncated = len(lines) > MAX_LINES

        header = [
            f"\nFilter: {display_filter}",
            f"File  : {pcap_path}",
            f"Hits  : {len(lines)} packets",
            "─" * 52,
        ]

        body   = lines[:MAX_LINES]
        footer = [
            "─" * 52,
            f"[Showing first {MAX_LINES} of {len(lines)} results]" if truncated else "",
        ]

        return "\n".join(header + body + footer)

    except subprocess.TimeoutExpired:
        return "[ERR] Filter timed out after 30 seconds. Try a more specific filter."
    except Exception as e:
        return f"[ERR] Filter failed: {e}"