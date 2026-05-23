#!/usr/bin/env python3
"""
KeyTrace — Multi-page PyQt6 GUI
Pages: Dashboard, SSLKEYLOGFILE Manager, Capture & Decrypt,
       Saved Scans, Results, Settings, Help
"""

import sys
import os
import json
import threading
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QFileDialog, QFrame, QScrollArea, QCheckBox, QComboBox,
    QSplitter, QListWidget, QListWidgetItem, QTabWidget,
    QProgressBar, QGroupBox, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation,
    QEasingCurve
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QTextCursor, QPixmap
)


# ── Theme System ───────────────────────────────────────────────────────────────

DARK = {
    "bg":          "#0d1117",
    "bg2":         "#161b22",
    "bg3":         "#21262d",
    "border":      "#30363d",
    "accent":      "#00d4aa",
    "accent2":     "#0ea5e9",
    "danger":      "#f85149",
    "warning":     "#e3b341",
    "success":     "#3fb950",
    "text":        "#e6edf3",
    "text2":       "#8b949e",
    "text3":       "#484f58",
    "sidebar":     "#010409",
    "terminal_bg": "#0d1117",
    "terminal_fg": "#00d4aa",
}

LIGHT = {
    "bg":          "#ffffff",
    "bg2":         "#f6f8fa",
    "bg3":         "#eaeef2",
    "border":      "#d0d7de",
    "accent":      "#0969da",
    "accent2":     "#0550ae",
    "danger":      "#d1242f",
    "warning":     "#9a6700",
    "success":     "#1a7f37",
    "text":        "#1f2328",
    "text2":       "#656d76",
    "text3":       "#8c959f",
    "sidebar":     "#f6f8fa",
    "terminal_bg": "#1f2328",
    "terminal_fg": "#3fb950",
}

_theme = DARK
_is_dark = True


def t(key):
    return _theme[key]


def toggle_theme():
    global _theme, _is_dark
    _is_dark = not _is_dark
    _theme = DARK if _is_dark else LIGHT


# ── Stylesheet generator ───────────────────────────────────────────────────────

def build_stylesheet():
    return f"""
    QMainWindow, QWidget {{
        background-color: {t('bg')};
        color: {t('text')};
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 13px;
    }}
    QLabel {{
        color: {t('text')};
        background: transparent;
    }}
    QLabel#heading {{
        font-size: 22px;
        font-weight: bold;
        color: {t('accent')};
        letter-spacing: 2px;
    }}
    QLabel#subheading {{
        font-size: 13px;
        color: {t('text2')};
    }}
    QLabel#section {{
        font-size: 11px;
        font-weight: bold;
        color: {t('text3')};
        letter-spacing: 3px;
        text-transform: uppercase;
    }}
    QPushButton {{
        background-color: {t('bg3')};
        color: {t('text')};
        border: 1px solid {t('border')};
        border-radius: 6px;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: {t('accent')};
        color: {t('bg')};
        border-color: {t('accent')};
    }}
    QPushButton#accent {{
        background-color: {t('accent')};
        color: {t('bg')};
        border: none;
        font-weight: bold;
        padding: 10px 24px;
    }}
    QPushButton#accent:hover {{
        background-color: {t('accent2')};
    }}
    QPushButton#danger {{
        background-color: transparent;
        color: {t('danger')};
        border: 1px solid {t('danger')};
    }}
    QPushButton#danger:hover {{
        background-color: {t('danger')};
        color: white;
    }}
    QPushButton#nav {{
        background: transparent;
        border: none;
        border-radius: 0px;
        color: {t('text2')};
        text-align: left;
        padding: 12px 20px;
        font-size: 13px;
    }}
    QPushButton#nav:hover {{
        background-color: {t('bg3')};
        color: {t('text')};
    }}
    QPushButton#nav_active {{
        background-color: {t('bg2')};
        border: none;
        border-left: 3px solid {t('accent')};
        border-radius: 0px;
        color: {t('accent')};
        text-align: left;
        padding: 12px 17px;
        font-size: 13px;
        font-weight: bold;
    }}
    QLineEdit {{
        background-color: {t('bg2')};
        color: {t('text')};
        border: 1px solid {t('border')};
        border-radius: 6px;
        padding: 8px 12px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 12px;
    }}
    QLineEdit:focus {{
        border-color: {t('accent')};
    }}
    QTextEdit {{
        background-color: {t('bg2')};
        color: {t('text')};
        border: 1px solid {t('border')};
        border-radius: 6px;
        padding: 8px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 12px;
    }}
    QTextEdit#terminal {{
        background-color: {t('terminal_bg')};
        color: {t('terminal_fg')};
        border: 1px solid {t('border')};
        border-radius: 6px;
        font-size: 13px;
        padding: 12px;
    }}
    QFrame#card {{
        background-color: {t('bg2')};
        border: 1px solid {t('border')};
        border-radius: 8px;
    }}
    QFrame#sidebar {{
        background-color: {t('sidebar')};
        border-right: 1px solid {t('border')};
    }}
    QFrame#topbar {{
        background-color: {t('bg2')};
        border-bottom: 1px solid {t('border')};
    }}
    QListWidget {{
        background-color: {t('bg2')};
        color: {t('text')};
        border: 1px solid {t('border')};
        border-radius: 6px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 10px 14px;
        border-bottom: 1px solid {t('border')};
    }}
    QListWidget::item:selected {{
        background-color: {t('bg3')};
        color: {t('accent')};
    }}
    QListWidget::item:hover {{
        background-color: {t('bg3')};
    }}
    QComboBox {{
        background-color: {t('bg2')};
        color: {t('text')};
        border: 1px solid {t('border')};
        border-radius: 6px;
        padding: 6px 12px;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QScrollBar:vertical {{
        background: {t('bg')};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {t('border')};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t('accent')};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QProgressBar {{
        background-color: {t('bg3')};
        border: none;
        border-radius: 4px;
        height: 6px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: {t('accent')};
        border-radius: 4px;
    }}
    QGroupBox {{
        color: {t('text2')};
        border: 1px solid {t('border')};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 2px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {t('text3')};
    }}
    QTabWidget::pane {{
        border: 1px solid {t('border')};
        border-radius: 6px;
        background-color: {t('bg2')};
    }}
    QTabBar::tab {{
        background-color: {t('bg3')};
        color: {t('text2')};
        padding: 8px 20px;
        border: 1px solid {t('border')};
        border-bottom: none;
        border-radius: 4px 4px 0 0;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {t('bg2')};
        color: {t('accent')};
        border-bottom: 2px solid {t('accent')};
    }}
    QCheckBox {{
        color: {t('text')};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {t('border')};
        border-radius: 4px;
        background: {t('bg2')};
    }}
    QCheckBox::indicator:checked {{
        background: {t('accent')};
        border-color: {t('accent')};
    }}
    """


# ── Worker thread ──────────────────────────────────────────────────────────────

class KeyTraceWorker(QThread):
    phase_update  = pyqtSignal(str, str)  # (message, level)
    finished      = pyqtSignal(bool, str) # (success, output_path)
    wait_for_user = pyqtSignal()          # emitted when browser is ready, pauses until user clicks Done

    def __init__(self, pcap_path, keylog_path, output_path, url, skip_browser):
        super().__init__()
        self.pcap_path    = pcap_path
        self.keylog_path  = keylog_path
        self.output_path  = output_path
        self.url          = url
        self.skip_browser = skip_browser
        self._user_ready  = threading.Event()  # blocks Phase 3 until user signals Done

    def user_done(self):
        """Called from the GUI when the user clicks Done browsing."""
        self._user_ready.set()

    def run(self):
        try:
            sys.path.append(str(Path(__file__).parent))
            from start_keytrace import start_keytrace
            from browser_launcher import launch_browser
            from decryptor import run_decryptor
        except ImportError as e:
            self.finished.emit(False, str(e))
            return

        try:
            # ── Phase 1 ───────────────────────────────────────────────────────
            self.phase_update.emit("Phase 1 — Configuring SSLKEYLOGFILE...", "phase")
            start_keytrace()
            self.phase_update.emit("[OK] SSLKEYLOGFILE configured.", "ok")

            # ── Phase 2 ───────────────────────────────────────────────────────
            if not self.skip_browser:
                self.phase_update.emit("Phase 2 — Launching browser...", "phase")
                launch_browser(url=self.url)
                self.phase_update.emit("[OK] Browser launched. Browse your target sites.", "ok")
                self.phase_update.emit("  → Click  Done Browsing  when ready to decrypt.", "info")

                # Signal the GUI to show the waiting dialog, then block until user clicks Done
                self.wait_for_user.emit()
                self._user_ready.wait()  # thread pauses here

                self.phase_update.emit("[OK] User confirmed. Proceeding to decryption...", "ok")
            else:
                self.phase_update.emit("Phase 2 — Skipped (using existing keylog).", "info")

            # ── Phase 3 ───────────────────────────────────────────────────────
            self.phase_update.emit("Phase 3 — Decrypting PCAP...", "phase")
            run_decryptor(
                pcap_path=Path(self.pcap_path),
                keylog_path=Path(self.keylog_path),
                output_path=Path(self.output_path),
            )
            self.phase_update.emit("[OK] Decryption complete.", "ok")
            self.finished.emit(True, self.output_path)

        except Exception as e:
            self.phase_update.emit(f"[ERR] {e}", "error")
            self.finished.emit(False, str(e))


# ── Reusable widgets ───────────────────────────────────────────────────────────

def card(parent=None):
    f = QFrame(parent)
    f.setObjectName("card")
    return f


def divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {t('border')}; background: {t('border')}; max-height: 1px;")
    return line


def heading(text):
    lbl = QLabel(text)
    lbl.setObjectName("heading")
    return lbl


def subheading(text):
    lbl = QLabel(text)
    lbl.setObjectName("subheading")
    return lbl


def section_label(text):
    lbl = QLabel(text.upper())
    lbl.setObjectName("section")
    return lbl


def accent_button(text):
    btn = QPushButton(text)
    btn.setObjectName("accent")
    return btn


def danger_button(text):
    btn = QPushButton(text)
    btn.setObjectName("danger")
    return btn


# ── Browsing Wait Dialog ───────────────────────────────────────────────────────

class BrowsingDialog(QWidget):
    """
    Floats over the app while the user browses.
    Shows a live keylog size counter and a Done button.
    Worker thread is paused until Done is clicked.
    """
    user_done = pyqtSignal()

    def __init__(self, keylog_path, parent=None):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.keylog_path = Path(keylog_path)
        self._build()
        self._start_monitor()

    def _build(self):
        self.setFixedSize(420, 240)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {t('bg2')};
                border: 1px solid {t('accent')};
                border-radius: 12px;
                color: {t('text')};
                font-family: 'JetBrains Mono', monospace;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # Icon + title
        title = QLabel("Browser is capturing TLS keys")
        title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {t('accent')};")
        layout.addWidget(title)

        info = QLabel(
            "Browse the sites you want to capture.\n"
            "KeyTrace is recording TLS session keys in the background.\n"
            "Click Done when you're finished browsing."
        )
        info.setStyleSheet(f"font-size: 11px; color: {t('text2')}; line-height: 1.6;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Live keylog size
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Keys captured:"))
        self.size_label = QLabel("0 bytes")
        self.size_label.setStyleSheet(f"color: {t('success')}; font-weight: bold;")
        size_row.addWidget(self.size_label)
        size_row.addStretch()
        layout.addLayout(size_row)

        # Pulse indicator
        self.pulse_label = QLabel("[ recording ]")
        self.pulse_label.setStyleSheet(f"color: {t('success')}; font-size: 11px;")
        layout.addWidget(self.pulse_label)
        self._pulse_state = True

        # Done button
        done_btn = accent_button("Done Browsing — Start Decryption")
        done_btn.setMinimumHeight(42)
        done_btn.clicked.connect(self._on_done)
        layout.addWidget(done_btn)

        # Center over parent
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.x() + (parent_geo.width()  - self.width())  // 2,
                parent_geo.y() + (parent_geo.height() - self.height()) // 2,
            )

    def _start_monitor(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(500)  # update every 500ms

    def _update(self):
        # Update keylog file size
        try:
            size = self.keylog_path.stat().st_size if self.keylog_path.exists() else 0
            if size > 1024:
                self.size_label.setText(f"{size / 1024:.1f} KB")
            else:
                self.size_label.setText(f"{size} bytes")
        except Exception:
            pass

        # Pulse animation
        self._pulse_state = not self._pulse_state
        self.pulse_label.setStyleSheet(
            f"color: {t('success') if self._pulse_state else t('text3')}; font-size: 11px;"
        )

    def _on_done(self):
        self._timer.stop()
        self.hide()
        self.user_done.emit()


# ── Pages ──────────────────────────────────────────────────────────────────────

class DashboardPage(QWidget):
    def __init__(self, nav_callback):
        super().__init__()
        self.nav = nav_callback
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Header
        layout.addWidget(heading("KEYTRACE"))
        layout.addWidget(subheading("TLS traffic decryption — simplified for everyone."))
        layout.addWidget(divider())

        # Status cards row
        status_row = QHBoxLayout()
        status_row.setSpacing(16)

        self.dep_card  = self._status_card("Dependencies",  "Checking...", "[>]")
        self.key_card  = self._status_card("SSLKEYLOGFILE", "Not set",     "[K]")
        self.scan_card = self._status_card("Saved Scans",   "0 scans",     "[F]")

        status_row.addWidget(self.dep_card[0])
        status_row.addWidget(self.key_card[0])
        status_row.addWidget(self.scan_card[0])
        layout.addLayout(status_row)

        # Quick actions
        layout.addWidget(section_label("Quick Actions"))

        actions = QGridLayout()
        actions.setSpacing(12)

        btns = [
            ("Create SSLKEYLOGFILE",  2, "The core feature — set up TLS key logging"),
            ("Capture & Decrypt",      3, "Decrypt a PCAP file"),
            ("Saved Scans",            5, "Browse your saved captures"),
            ("Results",                6, "View decryption output"),
            ("Settings",              7, "Configure KeyTrace"),
            ("Help & Docs",            8, "Learn how TLS decryption works"),
        ]

        for i, (label, page_idx, tip) in enumerate(btns):
            btn = QPushButton(label)
            btn.setToolTip(tip)
            btn.setMinimumHeight(52)
            btn.clicked.connect(lambda _, idx=page_idx: self.nav(idx))
            actions.addWidget(btn, i // 3, i % 3)

        layout.addLayout(actions)
        layout.addStretch()

        # Footer
        footer = QLabel("KeyTrace  ·  Cross-platform TLS Inspector")
        footer.setObjectName("subheading")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def _status_card(self, title, value, icon):
        f = card()
        v = QVBoxLayout(f)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(6)

        top = QHBoxLayout()
        top.addWidget(QLabel(icon))
        top.addStretch()
        v.addLayout(top)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {t('accent')};")
        v.addWidget(val_lbl)
        v.addWidget(QLabel(title))

        return f, val_lbl

    def refresh_status(self, keylog_exists, scan_count, deps_ok):
        self.dep_card[1].setText("Ready" if deps_ok else "Missing")
        self.dep_card[1].setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {t('success') if deps_ok else t('danger')};"
        )
        self.key_card[1].setText("Configured" if keylog_exists else "Not set")
        self.key_card[1].setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {t('success') if keylog_exists else t('warning')};"
        )
        self.scan_card[1].setText(f"{scan_count} scan{'s' if scan_count != 1 else ''}")


class SSLKeylogPage(QWidget):
    keylog_created = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addWidget(heading("SSLKEYLOGFILE MANAGER"))
        layout.addWidget(subheading(
            "Create and manage your TLS key log file. Works with Wireshark, KeyTrace, and any compatible tool."
        ))
        layout.addWidget(divider())

        tabs = QTabWidget()

        # ── Tab 1: Create ─────────────────────────────────────────────────────
        create_tab = QWidget()
        ct = QVBoxLayout(create_tab)
        ct.setContentsMargins(20, 20, 20, 20)
        ct.setSpacing(16)

        ct.addWidget(section_label("Keylog File Location"))

        path_row = QHBoxLayout()
        self.keylog_path_input = QLineEdit()
        self.keylog_path_input.setText(str(Path.home() / "keytrace_sslkeylogfile.txt"))
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_keylog_path)
        path_row.addWidget(self.keylog_path_input)
        path_row.addWidget(browse_btn)
        ct.addLayout(path_row)

        info = QLabel(
            "KeyTrace will set SSLKEYLOGFILE to this path in your shell profile (Linux/macOS)\n"
            "or as a permanent Windows environment variable. Your browser will write TLS session\n"
            "keys here automatically whenever it launches."
        )
        info.setObjectName("subheading")
        info.setWordWrap(True)
        ct.addWidget(info)

        self.create_btn = accent_button("Create & Configure SSLKEYLOGFILE")
        self.create_btn.setMinimumHeight(48)
        self.create_btn.clicked.connect(self._create_keylog)
        ct.addWidget(self.create_btn)

        self.create_status = QTextEdit()
        self.create_status.setObjectName("terminal")
        self.create_status.setReadOnly(True)
        self.create_status.setMaximumHeight(160)
        self.create_status.setPlaceholderText("Output will appear here...")
        ct.addWidget(self.create_status)
        ct.addStretch()

        # ── Tab 2: Use Existing ───────────────────────────────────────────────
        use_tab = QWidget()
        ut = QVBoxLayout(use_tab)
        ut.setContentsMargins(20, 20, 20, 20)
        ut.setSpacing(16)

        ut.addWidget(section_label("Use an Existing Keylog File"))

        existing_row = QHBoxLayout()
        self.existing_path_input = QLineEdit()
        self.existing_path_input.setPlaceholderText("Path to existing sslkeylog.log...")
        browse_existing = QPushButton("Browse")
        browse_existing.clicked.connect(self._browse_existing)
        existing_row.addWidget(self.existing_path_input)
        existing_row.addWidget(browse_existing)
        ut.addLayout(existing_row)

        verify_btn = accent_button("Verify & Use This File")
        verify_btn.clicked.connect(self._verify_existing)
        ut.addWidget(verify_btn)

        self.verify_status = QLabel("")
        self.verify_status.setWordWrap(True)
        ut.addWidget(self.verify_status)
        ut.addStretch()

        # ── Tab 3: External Use ───────────────────────────────────────────────
        ext_tab = QWidget()
        et = QVBoxLayout(ext_tab)
        et.setContentsMargins(20, 20, 20, 20)
        et.setSpacing(12)

        et.addWidget(section_label("Using Your Keylog Outside KeyTrace"))

        steps = [
            ("Wireshark",
             "Edit → Preferences → Protocols → TLS\nSet '(Pre)-Master-Secret log filename' to your keylog path."),
            ("tshark (terminal)",
             "tshark -r capture.pcapng -o tls.keylog_file:/path/to/sslkeylog.log"),
            ("Chrome / Brave / Edge",
             "Launch with: SSLKEYLOGFILE=/path/to/file chromium\nOr set the env variable permanently and launch normally."),
            ("Firefox",
             "Set SSLKEYLOGFILE in your environment before launching Firefox.\nFirefox respects this variable natively."),
        ]

        for tool, instruction in steps:
            g = QGroupBox(tool)
            gl = QVBoxLayout(g)
            lbl = QLabel(instruction)
            lbl.setObjectName("subheading")
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            gl.addWidget(lbl)
            et.addWidget(g)

        et.addStretch()

        tabs.addTab(create_tab,  "Create New")
        tabs.addTab(use_tab,     "Use Existing")
        tabs.addTab(ext_tab,     "Use Outside KeyTrace")
        layout.addWidget(tabs)

    def _browse_keylog_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "Set Keylog Path", str(Path.home()), "Log files (*.log *.txt);;All files (*)")
        if path:
            self.keylog_path_input.setText(path)

    def _browse_existing(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Keylog File", str(Path.home()), "Log files (*.log *.txt);;All files (*)")
        if path:
            self.existing_path_input.setText(path)

    def _create_keylog(self):
        self.create_status.clear()
        path = self.keylog_path_input.text().strip()
        if not path:
            self._log_create("[ERR] Please specify a path.", "error")
            return

        self.create_btn.setEnabled(False)
        self.create_btn.setText("Configuring...")

        def run():
            try:
                sys.path.append(str(Path(__file__).parent))
                from start_keytrace import start_keytrace
                import os
                os.environ["SSLKEYLOGFILE"] = path
                Path(path).touch(exist_ok=True)
                start_keytrace()
                self._log_create(f"[OK] SSLKEYLOGFILE created at:\n  {path}", "ok")
                self._log_create("[OK] Your shell profile has been updated.", "ok")
                self._log_create("[OK] Wireshark and other tools can now use this file.", "ok")
                self.keylog_created.emit(path)
            except Exception as e:
                self._log_create(f"[ERR] {e}", "error")
            finally:
                self.create_btn.setEnabled(True)
                self.create_btn.setText("Create & Configure SSLKEYLOGFILE")

        threading.Thread(target=run, daemon=True).start()

    def _log_create(self, msg, level="info"):
        colors = {"ok": t("success"), "error": t("danger"), "info": t("text2")}
        color  = colors.get(level, t("text"))
        self.create_status.append(f'<span style="color:{color};">{msg}</span>')

    def _verify_existing(self):
        path = self.existing_path_input.text().strip()
        if not path:
            self.verify_status.setText("Please enter a path.")
            return
        p = Path(path)
        if p.exists() and p.is_file():
            size = p.stat().st_size
            self.verify_status.setText(
                f'<span style="color:{t("success")};">File found ({size:,} bytes). '
                f'You can use this file with KeyTrace and Wireshark.</span>'
            )
            self.verify_status.setTextFormat(Qt.TextFormat.RichText)
            os.environ["SSLKEYLOGFILE"] = str(p)
        else:
            self.verify_status.setText(
                f'<span style="color:{t("danger")};">File not found at: {path}</span>'
            )
            self.verify_status.setTextFormat(Qt.TextFormat.RichText)


# ── Inline Terminal Widget ─────────────────────────────────────────────────────

class TerminalWidget(QTextEdit):
    """
    A single QTextEdit that behaves like a real terminal.
    - Type inline at the prompt
    - Enter dispatches the command
    - Backspace can't delete past the prompt
    - Up/Down arrows cycle command history
    - Clicking elsewhere snaps cursor back to input position
    """

    def __init__(self, dispatch_fn, parent=None):
        super().__init__(parent)
        self.dispatch_fn   = dispatch_fn
        self.history       = []
        self.history_idx   = -1
        self._prompt       = "keytrace> "
        self._prompt_pos   = 0  # character position where current input starts

        self.setObjectName("terminal")
        self.setUndoRedoEnabled(False)
        self.setAcceptRichText(False)
        self.setFont(QFont("Courier New", 14))

        self._print_welcome()
        self._new_prompt()

    def _print_welcome(self):
        self.append("KeyTrace Terminal  —  type 'help' for commands")
        self.append("─" * 48)
        self.append("")

    def _new_prompt(self):
        """Print a fresh prompt and record where input starts."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(self._prompt)
        self._prompt_pos = cursor.position()
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def _get_input(self):
        """Return whatever the user has typed after the current prompt."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        full_text = self.toPlainText()
        return full_text[self._prompt_pos:]

    def _set_input(self, text):
        """Replace current input with text (for history navigation)."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        # Select from prompt_pos to end
        cursor.setPosition(self._prompt_pos, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(text)
        self.setTextCursor(cursor)

    def _run_command(self):
        cmd = self._get_input().strip()

        if cmd:
            self.history.append(cmd)
        self.history_idx = -1

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText("\n")

        if cmd:
            try:
                result = self.dispatch_fn(cmd)
                if result == "__CLEAR__":
                    self.clear()
                    self._prompt_pos = 0
                    self._new_prompt()
                    return
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.insertText(result.strip() + "\n")
            except Exception as e:
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.insertText(f"Error: {e}\n")

        self._new_prompt()

    def keyPressEvent(self, event):
        key = event.key()
        cursor = self.textCursor()

        # Always keep cursor at or after prompt_pos
        if cursor.position() < self._prompt_pos:
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self._run_command()
            return

        if key == Qt.Key.Key_Backspace:
            if cursor.position() <= self._prompt_pos:
                return  # Can't delete the prompt
            super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_Up:
            if self.history:
                self.history_idx = min(self.history_idx + 1, len(self.history) - 1)
                self._set_input(self.history[-(self.history_idx + 1)])
            return

        if key == Qt.Key.Key_Down:
            if self.history_idx > 0:
                self.history_idx -= 1
                self._set_input(self.history[-(self.history_idx + 1)])
            elif self.history_idx == 0:
                self.history_idx = -1
                self._set_input("")
            return

        if key == Qt.Key.Key_Home:
            cursor.setPosition(self._prompt_pos)
            self.setTextCursor(cursor)
            return

        if key in (Qt.Key.Key_Left, Qt.Key.Key_Backspace):
            if cursor.position() <= self._prompt_pos:
                return

        # For all printable keys, move cursor to end first
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Snap cursor back to end (input position) after any click
        cursor = self.textCursor()
        if cursor.position() < self._prompt_pos:
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)


class CaptureDecryptPage(QWidget):
    def __init__(self, scans_page, results_page, nav_callback):
        super().__init__()
        self.scans_page   = scans_page
        self.results_page = results_page
        self.nav_callback = nav_callback
        self.worker       = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addWidget(heading("CAPTURE & DECRYPT"))
        layout.addWidget(subheading("Decrypt TLS traffic from a PCAP file using your SSLKEYLOGFILE."))
        layout.addWidget(divider())

        tabs = QTabWidget()

        # ── Beginner tab ──────────────────────────────────────────────────────
        beginner = QWidget()
        bl = QVBoxLayout(beginner)
        bl.setContentsMargins(20, 20, 20, 20)
        bl.setSpacing(14)

        # PCAP
        bl.addWidget(section_label("PCAP File"))
        pcap_row = QHBoxLayout()
        self.pcap_input = QLineEdit()
        self.pcap_input.setPlaceholderText("Select your .pcap or .pcapng file...")
        browse_pcap = QPushButton("Browse")
        browse_pcap.clicked.connect(self._browse_pcap)
        pcap_row.addWidget(self.pcap_input)
        pcap_row.addWidget(browse_pcap)
        bl.addLayout(pcap_row)

        # Keylog
        bl.addWidget(section_label("SSLKEYLOGFILE"))
        key_row = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setText(str(Path.home() / "keytrace_sslkeylogfile.txt"))
        browse_key = QPushButton("Browse")
        browse_key.clicked.connect(self._browse_key)
        key_row.addWidget(self.key_input)
        key_row.addWidget(browse_key)
        bl.addLayout(key_row)

        # URL
        bl.addWidget(section_label("URL (for browser launch)"))
        self.url_input = QLineEdit()
        self.url_input.setText("https://www.google.com")
        bl.addWidget(self.url_input)

        # Skip checkbox
        self.skip_browser = QCheckBox("Skip browser launch (I already have a keylog file)")
        bl.addWidget(self.skip_browser)

        # Start
        self.start_btn = accent_button("Start KeyTrace")
        self.start_btn.setMinimumHeight(48)
        self.start_btn.clicked.connect(self._start)
        bl.addWidget(self.start_btn)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        bl.addWidget(self.progress)

        # Status
        self.status_box = QTextEdit()
        self.status_box.setObjectName("terminal")
        self.status_box.setReadOnly(True)
        self.status_box.setPlaceholderText("Phase updates will appear here...")
        bl.addWidget(self.status_box)

        # ── Pro tab (inline terminal) ─────────────────────────────────────────
        pro = QWidget()
        pl = QVBoxLayout(pro)
        pl.setContentsMargins(20, 20, 20, 20)
        pl.setSpacing(10)

        pl.addWidget(section_label("KeyTrace Terminal"))

        self.terminal = TerminalWidget(self._dispatch_command)
        pl.addWidget(self.terminal)

        tabs.addTab(beginner, "Beginner Mode")
        tabs.addTab(pro,      "Pro Mode  (Terminal)")
        layout.addWidget(tabs)

    def _browse_pcap(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select PCAP", str(Path.home()),
            "PCAP files (*.pcap *.pcapng);;All files (*)"
        )
        if path:
            self.pcap_input.setText(path)

    def _browse_key(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Keylog", str(Path.home()),
            "Log files (*.log *.txt);;All files (*)"
        )
        if path:
            self.key_input.setText(path)

    def _start(self):
        pcap = self.pcap_input.text().strip()
        key  = self.key_input.text().strip()
        url  = self.url_input.text().strip()

        if not pcap:
            self._log("[ERR] Please select a PCAP file.", "error")
            return
        if not key:
            self._log("[ERR] Please specify a keylog file.", "error")
            return

        output = str(Path(pcap).with_suffix("")) + "_decrypted.txt"

        self.status_box.clear()
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Running...")
        self.progress.setVisible(True)

        self.worker = KeyTraceWorker(
            pcap, key, output, url, self.skip_browser.isChecked()
        )
        self.worker.phase_update.connect(self._log)
        self.worker.finished.connect(self._on_finish)
        self.worker.wait_for_user.connect(lambda: self._show_browsing_dialog(key))
        self.worker.start()

    def _show_browsing_dialog(self, keylog_path):
        """Show the browsing wait dialog — called from main thread via signal."""
        self._browsing_dialog = BrowsingDialog(
            keylog_path,
            parent=self.window()
        )
        self._browsing_dialog.user_done.connect(self.worker.user_done)
        self._browsing_dialog.show()

    def _on_finish(self, success, output_path):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Start KeyTrace")
        self.progress.setVisible(False)

        if success:
            self._log(f"Output: {output_path}", "info")
            self.scans_page.add_scan(self.pcap_input.text(), output_path)
            # Auto-display and save simultaneously
            self.results_page.load_output(output_path)
            self.nav_callback(4)  # Navigate to Results page
        else:
            self._log("KeyTrace encountered an error. Check output above.", "error")

    def _log(self, msg, level="info"):
        colors = {
            "phase": t("accent2"),
            "ok":    t("success"),
            "error": t("danger"),
            "info":  t("text2"),
        }
        color = colors.get(level, t("text"))
        self.status_box.append(f'<span style="color:{color};">{msg}</span>')
        self.status_box.moveCursor(QTextCursor.MoveOperation.End)

    def _dispatch_command(self, cmd):
        try:
            # Ensure KeyTrace root is on sys.path regardless of where script is run from
            kt_root = str(Path(__file__).resolve().parent)
            if kt_root not in sys.path:
                sys.path.insert(0, kt_root)

            from core.dispatcher import dispatch
            return dispatch(cmd)
        except ModuleNotFoundError as e:
            return (
                f"[ERR] Could not load command module: {e}\n"
                f"      Make sure core/ folder is in: {kt_root}"
            )
        except Exception as e:
            return f"[ERR] {e}"


class SavedScansPage(QWidget):
    open_result = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scans = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addWidget(heading("SAVED SCANS"))
        layout.addWidget(subheading("All captured and decrypted sessions stored here."))
        layout.addWidget(divider())

        top_row = QHBoxLayout()
        top_row.addWidget(section_label("Sessions"))
        top_row.addStretch()
        clear_btn = danger_button("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        top_row.addWidget(clear_btn)
        layout.addLayout(top_row)

        self.scan_list = QListWidget()
        self.scan_list.itemDoubleClicked.connect(self._open_scan)
        layout.addWidget(self.scan_list)

        layout.addWidget(section_label("Selected Scan"))

        self.detail_box = QTextEdit()
        self.detail_box.setObjectName("terminal")
        self.detail_box.setReadOnly(True)
        self.detail_box.setMaximumHeight(120)
        self.detail_box.setPlaceholderText("Double-click a scan to view details...")
        layout.addWidget(self.detail_box)

        open_btn = accent_button("Open in Results Viewer")
        open_btn.clicked.connect(self._open_selected)
        layout.addWidget(open_btn)

    def add_scan(self, pcap_path, output_path):
        ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
        name = Path(pcap_path).name
        entry = {"pcap": pcap_path, "output": output_path, "time": ts, "name": name}
        self.scans.append(entry)
        item = QListWidgetItem(f"{name}  ·  {ts}")
        self.scan_list.addItem(item)

    def _open_scan(self, item):
        idx = self.scan_list.row(item)
        if idx < len(self.scans):
            s = self.scans[idx]
            self.detail_box.setText(
                f"PCAP:   {s['pcap']}\nOutput: {s['output']}\nTime:   {s['time']}"
            )

    def _open_selected(self):
        idx = self.scan_list.currentRow()
        if idx >= 0 and idx < len(self.scans):
            self.open_result.emit(self.scans[idx]["output"])

    def _clear_all(self):
        self.scans.clear()
        self.scan_list.clear()
        self.detail_box.clear()

    def count(self):
        return len(self.scans)


class ResultsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addWidget(heading("RESULTS"))
        layout.addWidget(subheading("View and search your decrypted traffic output."))
        layout.addWidget(divider())

        top = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search output...")
        self.search_input.textChanged.connect(self._search)
        top.addWidget(self.search_input)

        load_btn = QPushButton("Load File")
        load_btn.clicked.connect(self._load_file)
        top.addWidget(load_btn)

        export_btn = accent_button("Export")
        export_btn.clicked.connect(self._export)
        top.addWidget(export_btn)
        layout.addLayout(top)

        self.output_view = QTextEdit()
        self.output_view.setObjectName("terminal")
        self.output_view.setReadOnly(True)
        self.output_view.setPlaceholderText("Load a decrypted output file to view results here...")
        layout.addWidget(self.output_view)

        self.stats_label = QLabel("")
        self.stats_label.setObjectName("subheading")
        layout.addWidget(self.stats_label)

        self._raw_content = ""

    def load_output(self, path):
        try:
            content = Path(path).read_text(encoding="utf-8")
            self._raw_content = content
            self.output_view.setText(content)
            lines = content.splitlines()
            self.stats_label.setText(
                f"{len(lines):,} lines  ·  {len(content):,} bytes  ·  {path}"
            )
        except Exception as e:
            self.output_view.setText(f"Error loading file: {e}")

    def _search(self, query):
        if not query:
            self.output_view.setText(self._raw_content)
            return
        lines = [l for l in self._raw_content.splitlines() if query.lower() in l.lower()]
        self.output_view.setText("\n".join(lines))
        self.stats_label.setText(f"{len(lines)} matching lines")

    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Output File", str(Path.home()),
            "Text files (*.txt);;All files (*)"
        )
        if path:
            self.load_output(path)

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", str(Path.home() / "keytrace_export.txt"),
            "Text files (*.txt);;CSV files (*.csv);;All files (*)"
        )
        if path:
            Path(path).write_text(self.output_view.toPlainText(), encoding="utf-8")


class SettingsPage(QWidget):
    theme_toggled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addWidget(heading("SETTINGS"))
        layout.addWidget(divider())

        # Appearance
        g1 = QGroupBox("APPEARANCE")
        gl1 = QVBoxLayout(g1)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme"))
        theme_row.addStretch()
        self.theme_btn = QPushButton("Switch to Light Mode")
        self.theme_btn.clicked.connect(self._toggle_theme)
        theme_row.addWidget(self.theme_btn)
        gl1.addLayout(theme_row)
        layout.addWidget(g1)

        # tshark
        g2 = QGroupBox("TSHARK")
        gl2 = QVBoxLayout(g2)
        gl2.addWidget(QLabel("tshark binary path"))
        tshark_row = QHBoxLayout()
        self.tshark_input = QLineEdit("/usr/bin/tshark")
        browse_tshark = QPushButton("Browse")
        browse_tshark.clicked.connect(self._browse_tshark)
        tshark_row.addWidget(self.tshark_input)
        tshark_row.addWidget(browse_tshark)
        gl2.addLayout(tshark_row)
        layout.addWidget(g2)

        # Default paths
        g3 = QGroupBox("DEFAULT PATHS")
        gl3 = QVBoxLayout(g3)

        gl3.addWidget(QLabel("Default keylog directory"))
        self.keylog_dir_input = QLineEdit(str(Path.home()))
        gl3.addWidget(self.keylog_dir_input)

        gl3.addWidget(QLabel("Default output directory"))
        self.output_dir_input = QLineEdit(str(Path.home() / "keytrace_output"))
        gl3.addWidget(self.output_dir_input)
        layout.addWidget(g3)

        # Browser
        g4 = QGroupBox("BROWSER")
        gl4 = QVBoxLayout(g4)
        gl4.addWidget(QLabel("Preferred browser"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Auto-detect", "Chrome", "Firefox", "Brave", "Opera"])
        gl4.addWidget(self.browser_combo)
        layout.addWidget(g4)

        save_btn = accent_button("Save Settings")
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

        self.save_feedback = QLabel("")
        self.save_feedback.setStyleSheet(f"color: {t('success')};")
        layout.addWidget(self.save_feedback)

        layout.addStretch()

    def load_config(self):
        """Load saved settings from disk and populate fields."""
        cfg_path = Path.home() / ".keytrace_config.json"
        try:
            config = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        except Exception:
            config = {}

        if "tshark" in config:
            self.tshark_input.setText(config["tshark"])
        if "keylog_dir" in config:
            self.keylog_dir_input.setText(config["keylog_dir"])
        if "output_dir" in config:
            self.output_dir_input.setText(config["output_dir"])
        if "browser" in config:
            idx = self.browser_combo.findText(config["browser"])
            if idx >= 0:
                self.browser_combo.setCurrentIndex(idx)
        if config.get("theme") == "light" and _is_dark:
            self._toggle_theme()

    def _toggle_theme(self):
        toggle_theme()
        self.theme_btn.setText("Switch to Light Mode" if _is_dark else "Switch to Dark Mode")
        self.theme_toggled.emit()

    def _browse_tshark(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select tshark binary", "/usr/bin")
        if path:
            self.tshark_input.setText(path)

    def _save(self):
        # Preserve existing config keys (like first_run_complete) when saving
        cfg_path = Path.home() / ".keytrace_config.json"
        try:
            config = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        except Exception:
            config = {}

        config.update({
            "tshark":     self.tshark_input.text(),
            "keylog_dir": self.keylog_dir_input.text(),
            "output_dir": self.output_dir_input.text(),
            "browser":    self.browser_combo.currentText(),
            "theme":      "dark" if _is_dark else "light",
        })
        cfg_path.write_text(json.dumps(config, indent=2))

        # Visual confirmation
        self.save_feedback.setText("Settings saved.")
        QTimer.singleShot(2000, lambda: self.save_feedback.setText(""))


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(20)
        layout.addStretch()

        logo = QLabel("KEYTRACE")
        logo.setStyleSheet(
            f"font-size: 36px; font-weight: bold; color: {t('accent')}; letter-spacing: 6px;"
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        tagline = QLabel("Heat. Shape. Ship.")
        tagline.setStyleSheet(f"font-size: 14px; color: {t('text2')}; letter-spacing: 3px;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)

        layout.addWidget(divider())

        info_lines = [
            ("Version",   "1.0.0"),
            ("Platform",  f"{__import__('platform').system()} {__import__('platform').release()}"),
            ("Python",    __import__('platform').python_version()),
            ("License",   "MIT"),
            ("Author",    "Oluwaferanmi"),
        ]

        for label, value in info_lines:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {t('text3')}; min-width: 100px;")
            val = QLabel(value)
            val.setStyleSheet(f"color: {t('text')};")
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addStretch()
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            layout.addLayout(row)

        layout.addWidget(divider())

        desc = QLabel(
            "KeyTrace makes TLS traffic decryption accessible to everyone.\n"
            "From security researchers to complete beginners — one tool, no barriers."
        )
        desc.setObjectName("subheading")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        layout.addStretch()


class SetupWizardPage(QWidget):
    """
    Shown on first launch only.
    Checks all dependencies and guides the user through fixing any issues.
    Writes a first_run flag to config once dismissed.
    """
    setup_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._checks = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)

        layout.addWidget(heading("WELCOME TO KEYTRACE"))
        layout.addWidget(subheading(
            "Let's make sure everything is set up correctly before you start."
        ))
        layout.addWidget(divider())
        layout.addWidget(section_label("System Check"))

        # Check result rows
        checks = [
            ("tshark",       "tshark installed",            self._check_tshark),
            ("python",       "Python 3.8+",                 self._check_python),
            ("keylog_dir",   "Keylog directory writable",   self._check_keylog_dir),
            ("sslkeylog",    "SSLKEYLOGFILE configured",    self._check_sslkeylog),
        ]

        self._rows = {}
        for key, label, _ in checks:
            row = QHBoxLayout()
            name_lbl = QLabel(label)
            name_lbl.setMinimumWidth(240)
            status_lbl = QLabel("Checking...")
            status_lbl.setStyleSheet(f"color: {t('text3')};")
            fix_btn = QPushButton("How to fix")
            fix_btn.setVisible(False)
            fix_btn.setObjectName("danger")
            row.addWidget(name_lbl)
            row.addWidget(status_lbl)
            row.addStretch()
            row.addWidget(fix_btn)
            layout.addLayout(row)
            self._rows[key] = (status_lbl, fix_btn)

        layout.addWidget(divider())

        # Fix instructions box (hidden until needed)
        self.fix_box = QTextEdit()
        self.fix_box.setObjectName("terminal")
        self.fix_box.setReadOnly(True)
        self.fix_box.setMaximumHeight(110)
        self.fix_box.setVisible(False)
        layout.addWidget(self.fix_box)

        # Summary label
        self.summary_lbl = QLabel("")
        self.summary_lbl.setWordWrap(True)
        layout.addWidget(self.summary_lbl)

        # Action button
        self.action_btn = accent_button("Checking your system...")
        self.action_btn.setMinimumHeight(48)
        self.action_btn.setEnabled(False)
        self.action_btn.clicked.connect(self._launch)
        layout.addWidget(self.action_btn)

        layout.addStretch()

        # Run checks after a short delay so the window renders first
        QTimer.singleShot(300, self._run_checks)

    # ── Individual checks ──────────────────────────────────────────────────────

    def _check_tshark(self):
        import shutil
        ok = shutil.which("tshark") is not None or Path("/usr/bin/tshark").exists()
        fix = (
            "Install tshark:\n\n"
            "  Linux:  sudo apt install tshark\n"
            "  macOS:  brew install wireshark\n"
            "  Windows: download from https://www.wireshark.org/download.html\n\n"
            "After installing, restart KeyTrace."
        )
        return ok, fix

    def _check_python(self):
        import sys as _sys
        ok = _sys.version_info >= (3, 8)
        fix = (
            "KeyTrace requires Python 3.8 or higher.\n\n"
            "Download the latest Python from https://python.org/downloads\n"
            "Then reinstall and relaunch KeyTrace."
        )
        return ok, fix

    def _check_keylog_dir(self):
        keylog_dir = Path.home()
        ok = os.access(keylog_dir, os.W_OK)
        fix = (
            f"KeyTrace needs write access to: {keylog_dir}\n\n"
            "This is your home directory. If you see this error,\n"
            "check your folder permissions:\n\n"
            "  Linux/macOS:  chmod 755 ~\n"
            "  Windows: right-click home folder → Properties → Security"
        )
        return ok, fix

    def _check_sslkeylog(self):
        keylog = os.environ.get("SSLKEYLOGFILE")
        ok = bool(keylog) and Path(keylog).exists()
        fix = (
            "SSLKEYLOGFILE is not configured yet.\n\n"
            "This is fine — go to the SSLKEYLOGFILE Manager page\n"
            "after setup to create and configure it in one click.\n\n"
            "This is KeyTrace's core feature and will be set up\n"
            "automatically when you click 'Create SSLKEYLOGFILE'."
        )
        return ok, fix

    # ── Run all checks ─────────────────────────────────────────────────────────

    def _run_checks(self):
        check_fns = {
            "tshark":     self._check_tshark,
            "python":     self._check_python,
            "keylog_dir": self._check_keylog_dir,
            "sslkeylog":  self._check_sslkeylog,
        }

        all_critical_ok = True
        critical_keys   = {"tshark", "python", "keylog_dir"}

        for key, fn in check_fns.items():
            ok, fix = fn()
            self._checks[key] = ok
            status_lbl, fix_btn = self._rows[key]

            if ok:
                status_lbl.setText("Ready")
                status_lbl.setStyleSheet(f"color: {t('success')}; font-weight: bold;")
                fix_btn.setVisible(False)
            else:
                status_lbl.setText("Not found")
                status_lbl.setStyleSheet(f"color: {t('danger')}; font-weight: bold;")
                fix_btn.setVisible(True)
                fix_btn.clicked.connect(lambda _, f=fix: self._show_fix(f))
                if key in critical_keys:
                    all_critical_ok = False

        # SSLKEYLOGFILE not set is a warning, not a blocker
        sslkeylog_ok = self._checks.get("sslkeylog", False)

        if all_critical_ok:
            if sslkeylog_ok:
                self.summary_lbl.setText(
                    "Everything is ready. KeyTrace is fully configured."
                )
                self.summary_lbl.setStyleSheet(f"color: {t('success')};")
            else:
                self.summary_lbl.setText(
                    "Ready to launch. Set up your SSLKEYLOGFILE on the next page."
                )
                self.summary_lbl.setStyleSheet(f"color: {t('warning')};")

            self.action_btn.setText("Launch KeyTrace")
            self.action_btn.setEnabled(True)
        else:
            self.summary_lbl.setText(
                "Some critical dependencies are missing. Fix them before continuing."
            )
            self.summary_lbl.setStyleSheet(f"color: {t('danger')};")
            self.action_btn.setText("Fix issues above to continue")
            self.action_btn.setEnabled(False)

    def _show_fix(self, text):
        self.fix_box.setVisible(True)
        self.fix_box.setText(text)

    def _launch(self):
        # Write first_run flag so wizard never shows again
        cfg_path = Path.home() / ".keytrace_config.json"
        try:
            config = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        except Exception:
            config = {}
        config["first_run_complete"] = True
        cfg_path.write_text(json.dumps(config, indent=2))
        self.setup_complete.emit()


class HelpPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addWidget(heading("HELP & DOCS"))
        layout.addWidget(subheading("Understanding TLS decryption — for everyone."))
        layout.addWidget(divider())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(16)

        topics = [
            ("What is SSLKEYLOGFILE?",
             "SSLKEYLOGFILE is an environment variable that tells your browser to write TLS session "
             "keys to a file as it creates them. TLS is the encryption that protects HTTPS traffic. "
             "By capturing these keys at the moment they're made, you can decrypt traffic you've "
             "captured — but only traffic from that browser session."),

            ("Why is this hard without KeyTrace?",
             "Normally, setting SSLKEYLOGFILE requires editing your shell profile manually, knowing "
             "which file to edit, restarting your terminal, and then launching your browser correctly. "
             "Most beginners get one step wrong and spend hours debugging. KeyTrace does all of this "
             "for you in one click."),

            ("What is a PCAP file?",
             "A PCAP (Packet Capture) file is a recording of network traffic. Tools like Wireshark, "
             "tcpdump, and tshark can create them. Without the TLS keys, a PCAP of HTTPS traffic "
             "looks like meaningless encrypted bytes. With the keys, you can read the actual HTTP "
             "requests and responses."),

            ("What is tshark?",
             "tshark is the command-line version of Wireshark. KeyTrace uses it internally to process "
             "your PCAP file and apply the TLS keys. Install it with: sudo apt install tshark (Linux) "
             "or brew install wireshark (macOS)."),

            ("Can I use my keylog file with Wireshark?",
             "Yes — that's the whole point. Once SSLKEYLOGFILE is configured, open Wireshark → "
             "Edit → Preferences → Protocols → TLS → set the log filename. Any capture you take "
             "while the browser is running will be decryptable, forever, regardless of whether "
             "KeyTrace is open."),

            ("Is this legal?",
             "Decrypting your own traffic on your own machine for testing, debugging, or learning "
             "is legal and normal practice in security research and development. Decrypting someone "
             "else's traffic without permission is not. KeyTrace is a tool for legitimate use."),
        ]

        for title, body in topics:
            g = QGroupBox(title)
            gl = QVBoxLayout(g)
            lbl = QLabel(body)
            lbl.setWordWrap(True)
            lbl.setObjectName("subheading")
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            gl.addWidget(lbl)
            cl.addWidget(g)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)


# ── Main Window ────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyTrace")
        self.setMinimumSize(1100, 720)
        self._build()
        self._apply_theme()
        self._refresh_dashboard()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Logo
        logo_frame = QFrame()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 24, 20, 16)
        logo_lbl = QLabel("KEYTRACE")
        logo_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {t('accent')}; letter-spacing: 3px;")
        logo_layout.addWidget(logo_lbl)
        version_lbl = QLabel("v1.0.0  ·  TLS Inspector")
        version_lbl.setObjectName("subheading")
        version_lbl.setStyleSheet(f"font-size: 10px; color: {t('text3')};")
        logo_layout.addWidget(version_lbl)
        sb_layout.addWidget(logo_frame)
        sb_layout.addWidget(divider())

        # Nav buttons
        nav_items = [
            ("Dashboard",          0),
            ("SSLKEYLOGFILE",      1),
            ("Capture & Decrypt",  2),
            ("Saved Scans",        3),
            ("Results",            4),
            ("Settings",           5),
            ("Help & Docs",        6),
            ("About",              7),
        ]

        self.nav_buttons = []
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav")
            btn.clicked.connect(lambda _, i=idx: self.navigate(i))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # System info at bottom of sidebar
        sys_frame = QFrame()
        sys_layout = QVBoxLayout(sys_frame)
        sys_layout.setContentsMargins(16, 8, 16, 16)
        import platform
        self.sys_label = QLabel(f"OS: {platform.system()} {platform.release()}")
        self.sys_label.setStyleSheet(f"font-size: 10px; color: {t('text3')};")
        sys_layout.addWidget(self.sys_label)
        sb_layout.addWidget(sys_frame)

        root.addWidget(sidebar)

        # ── Main content ──────────────────────────────────────────────────────
        main_area = QWidget()
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(48)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(24, 0, 24, 0)
        self.page_title_lbl = QLabel("Dashboard")
        self.page_title_lbl.setStyleSheet(f"font-size: 13px; color: {t('text2')};")
        tb_layout.addWidget(self.page_title_lbl)
        tb_layout.addStretch()

        self.dep_indicator = QLabel("tshark")
        self.dep_indicator.setStyleSheet(f"color: {t('text3')}; font-size: 11px;")
        tb_layout.addWidget(self.dep_indicator)
        main_layout.addWidget(topbar)

        # Pages
        self.stack = QStackedWidget()

        self.scans_page    = SavedScansPage()
        self.results_page  = ResultsPage()
        self.dash_page     = DashboardPage(self.navigate)
        self.keylog_page   = SSLKeylogPage()
        self.capture_page  = CaptureDecryptPage(
            self.scans_page,
            self.results_page,
            self.navigate
        )
        self.settings_page = SettingsPage()
        self.help_page     = HelpPage()
        self.about_page    = AboutPage()
        self.wizard_page   = SetupWizardPage()

        # Stack order: 0-7 main pages, 8 wizard
        for page in [
            self.dash_page, self.keylog_page, self.capture_page,
            self.scans_page, self.results_page,
            self.settings_page, self.help_page,
            self.about_page, self.wizard_page,
        ]:
            self.stack.addWidget(page)

        self.scans_page.open_result.connect(self._open_result_from_scan)
        self.settings_page.theme_toggled.connect(self._apply_theme)
        self.wizard_page.setup_complete.connect(lambda: self.navigate(0))

        main_layout.addWidget(self.stack)
        root.addWidget(main_area)

        # Load saved settings
        self.settings_page.load_config()

        # Restore window geometry
        self._restore_geometry()

        # Keyboard shortcuts
        self._setup_shortcuts()

        # Show wizard on first run, dashboard otherwise
        if self._is_first_run():
            self.stack.setCurrentIndex(8)
            self.page_title_lbl.setText("Setup Wizard")
        else:
            self.navigate(0)

        self._check_deps()

    def _restore_geometry(self):
        cfg_path = Path.home() / ".keytrace_config.json"
        try:
            config = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
            geo    = config.get("window_geometry")
            if geo:
                self.resize(geo["width"], geo["height"])
                self.move(geo["x"], geo["y"])
            else:
                self.resize(1100, 720)
        except Exception:
            self.resize(1100, 720)

    def _save_geometry(self):
        cfg_path = Path.home() / ".keytrace_config.json"
        try:
            config = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        except Exception:
            config = {}
        geo = self.geometry()
        config["window_geometry"] = {
            "x": geo.x(), "y": geo.y(),
            "width": geo.width(), "height": geo.height(),
        }
        try:
            cfg_path.write_text(json.dumps(config, indent=2))
        except Exception:
            pass

    def _setup_shortcuts(self):
        from PyQt6.QtGui import QShortcut, QKeySequence
        shortcuts = [
            ("Ctrl+1", lambda: self.navigate(0)),
            ("Ctrl+2", lambda: self.navigate(1)),
            ("Ctrl+3", lambda: self.navigate(2)),
            ("Ctrl+4", lambda: self.navigate(3)),
            ("Ctrl+5", lambda: self.navigate(4)),
            ("Ctrl+6", lambda: self.navigate(5)),
            ("Ctrl+7", lambda: self.navigate(6)),
            ("Ctrl+8", lambda: self.navigate(7)),
            ("Ctrl+Q", self.close),
            ("Ctrl+W", self.close),
        ]
        for key, fn in shortcuts:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(fn)

    def closeEvent(self, event):
        self._save_geometry()
        event.accept()

    def _is_first_run(self):
        cfg_path = Path.home() / ".keytrace_config.json"
        try:
            config = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
            return not config.get("first_run_complete", False)
        except Exception:
            return True

    def navigate(self, idx):
        self.stack.setCurrentIndex(idx)
        titles = [
            "Dashboard", "SSLKEYLOGFILE Manager", "Capture & Decrypt",
            "Saved Scans", "Results", "Settings", "Help & Docs", "About"
        ]
        self.page_title_lbl.setText(titles[idx] if idx < len(titles) else "")

        for i, btn in enumerate(self.nav_buttons):
            btn.setObjectName("nav_active" if i == idx else "nav")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if idx == 0:
            self._refresh_dashboard()

    def _check_deps(self):
        import shutil
        tshark_ok = shutil.which("tshark") is not None or Path("/usr/bin/tshark").exists()
        color = t("success") if tshark_ok else t("danger")
        self.dep_indicator.setText("tshark")
        self.dep_indicator.setStyleSheet(f"color: {color}; font-size: 11px;")

    def _refresh_dashboard(self):
        import shutil
        keylog = Path.home() / "keytrace_sslkeylogfile.txt"
        keylog_exists = keylog.exists()
        deps_ok = shutil.which("tshark") is not None or Path("/usr/bin/tshark").exists()
        self.dash_page.refresh_status(keylog_exists, self.scans_page.count(), deps_ok)

    def _open_result_from_scan(self, path):
        self.results_page.load_output(path)
        self.navigate(4)

    def _apply_theme(self):
        self.setStyleSheet(build_stylesheet())


# ── Entry point ────────────────────────────────────────────────────────────────

import logging
import traceback

LOG_PATH = Path.home() / ".keytrace_error.log"
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _handle_exception(exc_type, exc_value, exc_tb):
    """Catch unhandled exceptions, log them, and show a user-friendly message."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.error(f"Unhandled exception:\n{error_msg}")

    from PyQt6.QtWidgets import QMessageBox
    msg = QMessageBox()
    msg.setWindowTitle("KeyTrace — Unexpected Error")
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("KeyTrace encountered an unexpected error.")
    msg.setInformativeText(
        f"The error has been logged to:\n{LOG_PATH}\n\n"
        f"Please report this issue.\n\n{exc_type.__name__}: {exc_value}"
    )
    msg.exec()


sys.excepthook = _handle_exception


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("KeyTrace")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()