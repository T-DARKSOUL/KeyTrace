#!/usr/bin/env python3
"""
start_keytrace.py
-----------------
Sets up SSLKEYLOGFILE permanently on Linux, macOS, and Windows.

After this runs:
  - The current process has SSLKEYLOGFILE set (so KeyTrace's browser launch works)
  - The user's system is permanently configured (so Wireshark and other tools work
    even without KeyTrace running)
"""

import os
import sys
import platform
from pathlib import Path


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_banner():
    print("=" * 54)
    print("  KeyTrace — SSLKEYLOGFILE Setup")
    print("=" * 54)
    print()
    print("This tool configures your system so browsers write")
    print("TLS session keys to a file. That file lets Wireshark")
    print("and KeyTrace decrypt captured HTTPS traffic.")
    print()


def _resolve_keylog_path() -> Path:
    """Returns the canonical keylog path for this user."""
    return Path.home() / "keytrace_sslkeylogfile.txt"


def _set_for_current_process(keylog_path: Path):
    """Sets the variable in the running process (needed for Phase 2 browser launch)."""
    os.environ["SSLKEYLOGFILE"] = str(keylog_path)


# ── Linux / macOS ─────────────────────────────────────────────────────────────

# Shell config files to try, in priority order
_SHELL_CONFIGS = [
    ".zshrc",
    ".bashrc",
    ".bash_profile",
    ".profile",
]

_EXPORT_COMMENT = "# Added by KeyTrace — enables TLS decryption in Wireshark"
_EXPORT_LINE    = 'export SSLKEYLOGFILE="{path}"'


def _find_shell_config() -> Path:
    """Returns the first shell config file that exists, or ~/.bashrc as fallback."""
    home = Path.home()
    for name in _SHELL_CONFIGS:
        candidate = home / name
        if candidate.exists():
            return candidate
    # Fallback — create .bashrc
    return home / ".bashrc"


def _already_configured_unix(config_file: Path, keylog_path: Path) -> bool:
    """Returns True if SSLKEYLOGFILE is already set in the config file."""
    if not config_file.exists():
        return False
    return "SSLKEYLOGFILE" in config_file.read_text(encoding="utf-8")


def _configure_unix(keylog_path: Path):
    config_file = _find_shell_config()

    if _already_configured_unix(config_file, keylog_path):
        print(f"[✓] SSLKEYLOGFILE already configured in {config_file}")
        print(f"    Path: {keylog_path}")
        print()
        print("    No changes made. Your system is already set up.")
    else:
        export_block = (
            f"\n{_EXPORT_COMMENT}\n"
            f"{_EXPORT_LINE.format(path=keylog_path)}\n"
        )
        with open(config_file, "a", encoding="utf-8") as f:
            f.write(export_block)

        print(f"[✓] Configured SSLKEYLOGFILE in: {config_file}")
        print(f"    Path: {keylog_path}")
        print()
        print("    What this means:")
        print("    ─ Every browser you open from a new terminal will log TLS keys")
        print("    ─ Wireshark can now decrypt your HTTPS traffic")
        print("    ─ KeyTrace will also use this file automatically")
        print()
        print("    To apply right now in your current terminal, run:")
        print(f"      source {config_file}")
        print()
        print("    Or just open a new terminal — it applies automatically.")

    # Touch the file so it exists for immediate use
    keylog_path.touch(exist_ok=True)
    _set_for_current_process(keylog_path)


# ── Windows ───────────────────────────────────────────────────────────────────

def _already_configured_windows(keylog_path: Path) -> bool:
    """Checks the Windows user environment registry for SSLKEYLOGFILE."""
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, "SSLKEYLOGFILE")
            return bool(value)
    except FileNotFoundError:
        return False
    except Exception:
        return False


def _configure_windows(keylog_path: Path):
    import subprocess

    if _already_configured_windows(keylog_path):
        print(f"[✓] SSLKEYLOGFILE already configured as a Windows environment variable.")
        print(f"    Path: {keylog_path}")
        print()
        print("    No changes made. Your system is already set up.")
    else:
        try:
            # setx writes permanently to HKCU\Environment
            result = subprocess.run(
                ["setx", "SSLKEYLOGFILE", str(keylog_path)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip())

            print(f"[✓] SSLKEYLOGFILE set as a permanent Windows environment variable.")
            print(f"    Path: {keylog_path}")
            print()
            print("    What this means:")
            print("    ─ Every browser you open will log TLS keys to that file")
            print("    ─ Wireshark can now decrypt your HTTPS traffic")
            print("    ─ KeyTrace will also use this file automatically")
            print()
            print("    IMPORTANT: You must restart your browser (and any open")
            print("    terminals) for this to take effect.")

        except Exception as e:
            raise RuntimeError(
                f"Failed to set environment variable on Windows: {e}\n"
                "Try running KeyTrace as Administrator."
            )

    # Touch the file so it exists for immediate use
    keylog_path.touch(exist_ok=True)
    _set_for_current_process(keylog_path)


# ── Public entry point ────────────────────────────────────────────────────────

def start_keytrace():
    """
    Main entry point called by main.py and gui.py.
    Detects the OS and runs the appropriate setup.
    Raises RuntimeError on failure so callers can handle it cleanly.
    """
    _print_banner()

    keylog_path = _resolve_keylog_path()
    system      = platform.system()

    print(f"[*] Detected OS  : {system}")
    print(f"[*] Keylog target: {keylog_path}")
    print()

    if system in ("Linux", "Darwin"):  # Darwin = macOS
        _configure_unix(keylog_path)
    elif system == "Windows":
        _configure_windows(keylog_path)
    else:
        raise RuntimeError(
            f"Unsupported operating system: {system}\n"
            "KeyTrace supports Linux, macOS, and Windows."
        )

    print()
    print("[✓] Phase 1 complete — SSLKEYLOGFILE is ready.")
    print("=" * 54)
    print()


# ── Standalone use ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        start_keytrace()
    except RuntimeError as e:
        print(f"\n[✗] Setup failed: {e}")
        sys.exit(1)