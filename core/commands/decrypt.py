import os
import sys
from pathlib import Path

def run(args):
    if not args:
        return "[ERR] Usage: decrypt <pcap_path>"
    pcap = Path(args[0])
    if not pcap.exists():
        return f"[ERR] PCAP not found: {pcap}"
    keylog = os.environ.get("SSLKEYLOGFILE")
    if not keylog:
        return "[ERR] No SSLKEYLOGFILE set.\n      Run: create-keylog  or  use-keylog <path>"
    output = str(pcap.with_suffix("")) + "_decrypted.txt"
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from decryptor import run_decryptor
        run_decryptor(pcap_path=pcap, keylog_path=Path(keylog), output_path=Path(output))
        return f"[OK] Decryption complete.\n     Output: {output}"
    except Exception as e:
        return f"[ERR] Decryption failed: {e}"
