import subprocess
import os
import sys
import shutil
import shlex
from pathlib import Path


def run_decryptor(pcap_path, keylog_path, output_path):
    pcap_path   = Path(pcap_path)
    keylog_path = Path(keylog_path)
    output_path = Path(output_path)
    tshark_bin  = shutil.which("tshark") or "/usr/bin/tshark"

    # Validation
    if not pcap_path.exists():
        raise FileNotFoundError(f"PCAP file not found: {pcap_path}")
    if not keylog_path.exists():
        raise FileNotFoundError(f"SSL keylog file not found: {keylog_path}")
    if not Path(tshark_bin).exists():
        raise EnvironmentError(f"tshark not found at '{tshark_bin}'.")

    # ── Pass 1: HTTP fields (URLs, methods, response codes, data) ─────────────
    http_cmd = [
        tshark_bin,
        "-r", str(pcap_path),
        "-o", f"tls.keylog_file:{keylog_path.resolve()}",
        "-Y", "http",
        "-T", "fields",
        "-e", "frame.number",
        "-e", "ip.src",
        "-e", "ip.dst",
        "-e", "http.request.method",
        "-e", "http.request.full_uri",
        "-e", "http.response.code",
        "-e", "http.response.phrase",
        "-e", "http.host",
        "-e", "http.file_data",
        "-E", "separator=|",
        "-E", "empty=---",
    ]

    # ── Pass 2: TLS decrypted application data ────────────────────────────────
    tls_cmd = [
        tshark_bin,
        "-r", str(pcap_path),
        "-o", f"tls.keylog_file:{keylog_path.resolve()}",
        "-Y", "tls.app_data",
        "-T", "fields",
        "-e", "frame.number",
        "-e", "ip.src",
        "-e", "ip.dst",
        "-e", "tls.app_data",
        "-E", "separator=|",
        "-E", "empty=---",
    ]

    try:
        http_result = subprocess.run(
            http_cmd, capture_output=True, text=True, check=False
        )
        tls_result = subprocess.run(
            tls_cmd, capture_output=True, text=True, check=False
        )
    except Exception as e:
        raise RuntimeError(f"tshark failed: {e}")

    http_out = http_result.stdout.strip()
    tls_out  = tls_result.stdout.strip()

    if not http_out and not tls_out:
        raise RuntimeError(
            "No decrypted output found.\n"
            "Make sure your PCAP and keylog file are from the same browser session."
        )

    # ── Write structured output ───────────────────────────────────────────────
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  KeyTrace Decrypted Output\n")
        f.write(f"  PCAP    : {pcap_path}\n")
        f.write(f"  Keylog  : {keylog_path}\n")
        f.write("=" * 70 + "\n\n")

        if http_out:
            f.write("── HTTP TRAFFIC\n")
            f.write("Frame | Src IP | Dst IP | Method | URL | Code | Phrase | Host | Data\n")
            f.write("-" * 70 + "\n")
            for line in http_out.splitlines():
                parts = line.split("|")
                # Skip lines where everything except frame/ip is empty
                if all(p.strip() in ("---", "") for p in parts[3:]):
                    continue
                f.write(line + "\n")
            f.write("\n")

        if tls_out:
            f.write("── TLS APPLICATION DATA (hex)\n")
            f.write("Frame | Src IP | Dst IP | Data\n")
            f.write("-" * 70 + "\n")
            for line in tls_out.splitlines():
                parts = line.split("|")
                if all(p.strip() in ("---", "") for p in parts[3:]):
                    continue
                f.write(line + "\n")
            f.write("\n")

        f.write("=" * 70 + "\n")
        f.write(f"HTTP packets  : {len([l for l in http_out.splitlines() if l.strip()])}\n")
        f.write(f"TLS data pkts : {len([l for l in tls_out.splitlines() if l.strip()])}\n")
        f.write("=" * 70 + "\n")

    return str(output_path)