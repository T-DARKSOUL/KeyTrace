# KeyTrace

**TLS traffic decryption — simplified for everyone.**

KeyTrace removes the barrier that normally stops people from decrypting their own HTTPS traffic. Whether you're a security researcher, a networking student, or someone who's never heard of Wireshark — KeyTrace gets you from zero to decrypted in one click.

---

## The Problem

Decrypting TLS traffic requires setting `SSLKEYLOGFILE` before your browser launches, knowing which shell config file to edit, restarting your environment correctly, and then pointing Wireshark at the right file. Most people get one step wrong and spend hours debugging.

## The Solution

KeyTrace handles the entire setup automatically — and once configured, your keylog file works everywhere, not just inside KeyTrace.

---

## Features

- **One-click SSLKEYLOGFILE setup** — permanent, cross-platform configuration
- **PCAP decryption** — powered by tshark
- **Beginner mode** — guided buttons, no terminal required
- **Pro mode** — full inline terminal with 14 commands
- **Live capture** — capture traffic directly from a network interface
- **Results viewer** — search, filter, and export decrypted output
- **Saved scans** — all your sessions stored and accessible
- **Dark/light theme** — toggle in Settings
- **Cross-platform** — Linux, macOS, Windows

---

## Installation

### Requirements
- Python 3.8+
- tshark (included with Wireshark)

### Install tshark first

**Linux:**
```bash
sudo apt install tshark
```

**macOS:**
```bash
brew install wireshark
```

**Windows:**
Download from https://www.wireshark.org/download.html

### Install KeyTrace

**Linux / macOS:**
```bash
git clone https://github.com/T-DARKSOUL/KeyTrace.git
cd KeyTrace
bash install.sh
```

**Windows:**
```bash
git clone https://github.com/T-DARKSOUL/KeyTrace.git
cd KeyTrace
install.bat
```

**Manual install (any platform):**
```bash
git clone https://github.com/T-DARKSOUL/KeyTrace.git
cd KeyTrace
pip install -r requirements.txt
python gui.py
```

---

## Terminal Commands

```
help                    Show all commands
status                  Quick health check
version                 Show versions
create-keylog           Create and configure SSLKEYLOGFILE
use-keylog <path>       Use an existing keylog file
clear-keylog            Wipe keylog for a fresh capture
show-config             Show current configuration
interfaces              List network interfaces
capture <iface> [secs]  Live capture (default 30s)
decrypt <pcap>          Decrypt a PCAP file
filter <pcap> <query>   Filter with tshark display filter
list-scans              List saved decrypted output files
open <path>             View output file in terminal
clear                   Clear the terminal
```

---

## Using Your Keylog Outside KeyTrace

Once KeyTrace configures `SSLKEYLOGFILE`, the file works with any compatible tool:

**Wireshark:**
Edit → Preferences → Protocols → TLS → set log filename

**tshark:**
```bash
tshark -r capture.pcapng -o tls.keylog_file:/path/to/sslkeylogfile.txt
```

**Chrome / Brave / Edge:**
```bash
SSLKEYLOGFILE=/path/to/file chromium
```

---

## Project Structure

```
KeyTrace/
├── gui.py                  # Main PyQt6 GUI
├── main.py                 # CLI entry point
├── start_keytrace.py       # SSLKEYLOGFILE setup
├── browser_launcher.py     # Browser launch logic
├── decryptor.py            # tshark decryption
├── install.sh              # Linux/macOS installer
├── install.bat             # Windows installer
└── core/
    ├── dispatcher.py       # Command routing
    └── commands/           # Individual command modules
```

---

## License

KeyTrace Proprietary License — free for personal and educational use.
Commercial use requires a license. See [LICENSE](./LICENSE) for full terms.

---

## Author

Built by [Emmanuel Peculiar Ojo](https://github.com/T-DARKSOUL)

> Heat. Shape. Ship.