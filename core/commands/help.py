def run(args):
    return """
KeyTrace Terminal Commands
─────────────────────────────────────────────────────

  SETUP
  help                    Show this message
  version                 Show KeyTrace and dependency versions
  status                  Quick health check of your environment

  SSLKEYLOGFILE
  create-keylog           Create and configure SSLKEYLOGFILE
  use-keylog <path>       Point KeyTrace at an existing keylog file
  clear-keylog            Wipe keylog contents for a fresh capture
  show-config             Show current configuration and paths

  CAPTURE
  interfaces              List available network interfaces
  capture <iface> [secs]  Live capture on an interface (default 30s)

  DECRYPT
  decrypt <pcap>          Decrypt a PCAP using current SSLKEYLOGFILE
  filter <pcap> <filter>  Filter a PCAP with a tshark display filter

  OUTPUT
  list-scans              List all saved decrypted output files
  open <path>             View a decrypted output file in the terminal

  TERMINAL
  clear                   Clear the terminal screen

─────────────────────────────────────────────────────
  Examples:
    capture wlan0 60
    decrypt /home/user/Desktop/capture.pcapng
    filter capture.pcapng http.request
    open capture_decrypted.txt
─────────────────────────────────────────────────────
"""