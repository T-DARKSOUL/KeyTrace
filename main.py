#!/usr/bin/env python3
import sys
from pathlib import Path

# Add script's directory to sys.path for custom modules
sys.path.append(str(Path(__file__).parent))

from start_keytrace import start_keytrace
from browser_launcher import launch_browser
from decryptor import run_decryptor

def main(pcap_path=None, keylog_path=None, output_path=None):
    # ---- Paths (single source of truth) ----
    pcap_path   = Path(pcap_path) if pcap_path else Path("/home/feranmi/Desktop/pcap-decryptor/Saki scan 1.pcapng")
    keylog_path = Path(keylog_path) if keylog_path else Path.home() / "keytrace_sslkeylogfile.txt"
    output_path = Path(output_path) if output_path else Path("/home/feranmi/Desktop/KeyTrace/decrypted_output.txt")

    # Validate inputs
    if not pcap_path.exists():
        raise FileNotFoundError(f"PCAP file not found: {pcap_path}")
    if not keylog_path.parent.exists() or not keylog_path.parent.is_dir():
        raise PermissionError(f"Keylog directory not accessible: {keylog_path.parent}")

    try:
        # ---- Phase 1: Setup SSLKEYLOGFILE ----
        start_keytrace()

        # ---- Phase 2: Launch browser & generate keys ----
        launch_browser()

        # ---- Phase 3: Decrypt capture ----
        run_decryptor(
            pcap_path=pcap_path,
            keylog_path=keylog_path,
            output_path=output_path
        )
        print("Decryption complete. Check output file.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()