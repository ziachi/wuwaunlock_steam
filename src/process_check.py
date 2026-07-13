"""
Check if Wuthering Waves is currently running.
Must be closed before modifying config files.
Uses built-in Windows 'tasklist' command — no external dependencies.
"""

import subprocess
from tkinter import messagebox


GAME_PROCESSES = [
    "launcher.exe",
    "wuthering waves.exe",
    "launcher_main.exe",
]


def is_game_running() -> bool:
    """Check if any game process is currently running. Returns True if game is running."""
    try:
        output = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/NH"],
            text=True, creationflags=0x08000000,  # CREATE_NO_WINDOW
        )
    except Exception:
        return False  # Can't check, assume not running

    running = []
    for line in output.strip().splitlines():
        parts = line.split('","')
        if not parts:
            continue
        proc_name = parts[0].strip('"').lower()
        if proc_name in GAME_PROCESSES:
            running.append(proc_name)

    if running:
        procs = "\n".join(set(running))
        messagebox.showerror(
            "Game Is Running!",
            f"Please close the game and launcher before continuing.\n\n"
            f"Detected processes:\n{procs}"
        )
        return True
    return False
