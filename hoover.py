# ============================================================
#   hoover.py  ·  ClipboardHoover
#   The clipboard vacuum that never stops sucking.
# ============================================================
#
#   Usage:
#     python hoover.py            → save clipboard once & exit
#     python hoover.py --watch    → watch mode (Ctrl+C to stop)
#
# ============================================================

import pyperclip
import datetime
import os
import sys
import time

# ── Config ───────────────────────────────────────────────────
LOG_FILE        = "the_loot.txt"
TIMESTAMP_FMT   = "%Y-%m-%d %H:%M:%S"
WATCH_INTERVAL  = 1.2   # seconds between clipboard polls
BANNER_WIDTH    = 62

# ── ANSI color codes ──────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    GREY    = "\033[90m"

# ── Banner ────────────────────────────────────────────────────
BANNER = f"""
{C.CYAN}{C.BOLD}
  ██████╗██╗     ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗ 
 ██╔════╝██║     ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
 ██║     ██║     ██║██████╔╝██████╔╝██║   ██║███████║██████╔╝██║  ██║
 ██║     ██║     ██║██╔═══╝ ██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
 ╚██████╗███████╗██║██║     ██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
  ╚═════╝╚══════╝╚═╝╚═╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
{C.RESET}{C.CYAN}
  ██╗  ██╗ ██████╗  ██████╗ ██╗   ██╗███████╗██████╗ 
  ██║  ██║██╔═══██╗██╔═══██╗██║   ██║██╔════╝██╔══██╗
  ███████║██║   ██║██║   ██║██║   ██║█████╗  ██████╔╝
  ██╔══██║██║   ██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
  ██║  ██║╚██████╔╝╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
{C.RESET}"""

def divider(char="─", color=C.GREY):
    return f"{color}{char * BANNER_WIDTH}{C.RESET}"

def tag(label, color=C.CYAN):
    return f"{color}{C.BOLD}[{label}]{C.RESET}"

def timestamp_now():
    return datetime.datetime.now().strftime(TIMESTAMP_FMT)

# ── Core functions ────────────────────────────────────────────
def get_clipboard():
    try:
        content = pyperclip.paste()
        return content.strip() if content else None
    except Exception as e:
        print(f"{tag('ERROR', C.RED)} Clipboard access failed: {e}")
        return None

def append_to_log(content):
    if not content:
        return
    ts = timestamp_now()
    entry = f"[{ts}]\n{content}\n{'─' * 80}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        size = len(content)
        print(f"  {tag('SAVED', C.GREEN)} {C.WHITE}{size} chars{C.RESET}  {C.GREY}{ts}{C.RESET}")
    except Exception as e:
        print(f"{tag('ERROR', C.RED)} Log write failed: {e}")

def get_last_entry():
    if not os.path.exists(LOG_FILE):
        return ""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return ""
        return content.split("─" * 80)[0].split("\n", 1)[-1].strip()
    except Exception:
        return ""

def count_entries():
    if not os.path.exists(LOG_FILE):
        return 0
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.read().count("─" * 80)
    except Exception:
        return 0

def print_preview(text, max_len=100):
    preview = (text[:max_len] + "…") if len(text) > max_len else text
    lines = preview.splitlines()
    for line in lines[:4]:
        print(f"  {C.DIM}│{C.RESET}  {C.WHITE}{line}{C.RESET}")
    if len(lines) > 4:
        print(f"  {C.DIM}│  … ({len(lines)} lines total){C.RESET}")

# ── Modes ─────────────────────────────────────────────────────
def run_once():
    print(BANNER)
    print(divider("═", C.CYAN))
    print(f"  {C.BOLD}{C.WHITE}SINGLE CAPTURE MODE{C.RESET}   {C.GREY}one shot, one save{C.RESET}")
    print(divider("═", C.CYAN))
    print()

    text = get_clipboard()

    if not text:
        print(f"  {tag('EMPTY', C.YELLOW)} Clipboard has no text content. Nothing to hoard.")
    else:
        last = get_last_entry()
        if text == last:
            print(f"  {tag('DUPE', C.MAGENTA)} Already in the vault. Hoover remembers everything. 😏")
        else:
            print(f"  {tag('FOUND', C.CYAN)} Something juicy detected:\n")
            print_preview(text)
            print()
            append_to_log(text)

    print()
    print(divider())
    total = count_entries()
    log_path = os.path.abspath(LOG_FILE)
    print(f"  {C.GREY}Vault  →  {C.WHITE}{log_path}{C.RESET}")
    print(f"  {C.GREY}Total entries hoovered so far: {C.CYAN}{C.BOLD}{total}{C.RESET}")
    print(divider())
    print(f"  {C.DIM}Tip: run with {C.WHITE}--watch{C.DIM} to auto-capture every clipboard change{C.RESET}")
    print()

def run_watch():
    print(BANNER)
    print(divider("═", C.CYAN))
    print(f"  {C.BOLD}{C.WHITE}WATCH MODE{C.RESET}   {C.GREY}stalking your clipboard until you say stop{C.RESET}")
    print(divider("═", C.CYAN))
    print(f"  {C.GREY}Vault   →  {C.WHITE}{os.path.abspath(LOG_FILE)}{C.RESET}")
    print(f"  {C.GREY}Poll    →  every {WATCH_INTERVAL}s{C.RESET}")
    print(f"  {C.YELLOW}Stop    →  Ctrl+C{C.RESET}")
    print(divider())
    print(f"  {C.DIM}Listening…{C.RESET}\n")

    last = get_last_entry()
    captured = 0

    try:
        while True:
            current = get_clipboard()
            if current and current != last:
                print(f"\n{divider('·', C.CYAN)}")
                print(f"  {tag('NEW', C.CYAN)} Clipboard changed:")
                print_preview(current)
                print()
                append_to_log(current)
                last = current
                captured += 1
            time.sleep(WATCH_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n\n{divider('═', C.CYAN)}")
        print(f"  {tag('STOPPED', C.YELLOW)}  Hoover powered down cleanly.")
        print(f"  {C.GREY}Captured this session : {C.CYAN}{C.BOLD}{captured}{C.RESET}")
        print(f"  {C.GREY}Total in vault        : {C.CYAN}{C.BOLD}{count_entries()}{C.RESET}")
        print(f"  {C.GREY}Vault path            : {C.WHITE}{os.path.abspath(LOG_FILE)}{C.RESET}")
        print(divider("═", C.CYAN))
        print()

# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    # Enable ANSI on Windows
    if sys.platform == "win32":
        os.system("color")

    if "--watch" in sys.argv:
        run_watch()
    else:
        run_once()