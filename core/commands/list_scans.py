from pathlib import Path


def run(args):
    # Look for decrypted output files in home and Desktop
    search_dirs = [
        Path.home(),
        Path.home() / "Desktop",
        Path.home() / "Desktop" / "KeyTrace",
        Path.home() / "keytrace_output",
    ]

    found = []
    for d in search_dirs:
        if d.exists():
            for f in sorted(d.glob("*_decrypted.txt"), key=lambda x: x.stat().st_mtime, reverse=True):
                found.append(f)

    if not found:
        return (
            "[INFO] No saved scans found.\n"
            "       Decrypted output files end in _decrypted.txt\n"
            "       Run a decryption first, then list-scans again."
        )

    lines = [
        f"\nSaved Scans ({len(found)} found)",
        "─" * 52,
    ]

    for i, f in enumerate(found[:20], 1):
        size  = f.stat().st_size
        mtime = __import__("datetime").datetime.fromtimestamp(
            f.stat().st_mtime
        ).strftime("%Y-%m-%d %H:%M")

        if size > 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} bytes"

        lines.append(f"  {i:>2}.  {f.name}")
        lines.append(f"        {mtime}  |  {size_str}")
        lines.append(f"        {f}")
        lines.append("")

    lines.append("─" * 52)
    lines.append("Use: open <path>  to view a file in the terminal")

    return "\n".join(lines)