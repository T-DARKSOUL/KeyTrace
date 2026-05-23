from pathlib import Path


def run(args):
    if not args:
        return "[ERR] Usage: open <path_to_output_file>"

    path = Path(args[0])

    if not path.exists():
        return f"[ERR] File not found: {path}"

    if not path.is_file():
        return f"[ERR] Not a file: {path}"

    size = path.stat().st_size
    if size == 0:
        return f"[WARN] File is empty: {path}"

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[ERR] Could not read file: {e}"

    lines = content.splitlines()

    # Cap at 200 lines in terminal to avoid flooding
    MAX_LINES = 200
    truncated = len(lines) > MAX_LINES
    display   = lines[:MAX_LINES]

    header = (
        f"\nFile: {path}\n"
        f"Size: {size:,} bytes  |  {len(lines):,} lines\n"
        f"{'─' * 52}\n"
    )

    body = "\n".join(display)

    footer = (
        f"\n{'─' * 52}\n"
        f"[Showing first {MAX_LINES} of {len(lines):,} lines]\n"
        f"Use the Results page to view and search the full file."
    ) if truncated else f"\n{'─' * 52}"

    return header + body + footer