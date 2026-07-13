"""
WuWa Unlock Steam — Wuthering Waves FPS Unlocker (Steam Edition)
Unlocks 120 FPS for the Steam version of Wuthering Waves.
Only modifies game configuration files — no game files are touched.
"""

import sys
import ctypes
from tkinter import Tk, Label, Button, CENTER, messagebox

from steam_finder import find_wuwa_steam_paths
from fps_unlocker import unlock_fps
from version_info import APP_VERSION, APP_TITLE


def request_admin_restart():
    """Ask user if they want to restart with admin privileges."""
    ask = messagebox.askyesno(
        "Admin Rights",
        "This program may require Administrator privileges depending on "
        "the game install location (e.g. Program Files).\n\n"
        "Would you like to restart as Administrator?\n\n"
        "Usually not required."
    )
    if ask:
        try:
            if getattr(sys, 'frozen', False):
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable,
                    " ".join(sys.argv[1:]), None, 1
                )
            else:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable,
                    " ".join(sys.argv), None, 1
                )
            sys.exit()
        except Exception:
            messagebox.showerror("Error", "Failed to restart as Administrator.")


def is_admin() -> bool:
    """Check if running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def main() -> int:
    root = Tk()
    root.title(f"{APP_TITLE} v{APP_VERSION}")
    root.geometry("680x420")
    root.resizable(False, False)
    root.withdraw()

    # Admin check
    if not is_admin():
        request_admin_restart()

    root.deiconify()

    # Header
    Label(
        root,
        text=f"🎮 {APP_TITLE} v{APP_VERSION}",
        font=("Segoe UI", 18, "bold"),
    ).pack(pady=(20, 5))

    Label(
        root,
        text="Steam Edition — FPS Unlocker",
        font=("Segoe UI", 11),
        fg="#666666",
    ).pack()

    # Instructions
    Label(
        root,
        text=(
            "How to use:\n"
            "1) Make sure the game has been launched at least once.\n"
            "2) Make sure the game is NOT currently running.\n"
            "3) Click the button below to unlock 120 FPS.\n\n"
            "This tool auto-detects your Steam install location.\n"
            "It only modifies config files, NOT game files.\n\n"
            "After a game update or changing graphics settings,\n"
            "run this tool again."
        ),
        font=("Segoe UI", 11),
        wraplength=600,
        justify=CENTER,
    ).pack(pady=(15, 20))

    # Status label
    status_label = Label(root, text="", font=("Segoe UI", 10), fg="#008800")
    status_label.pack()

    # Buttons
    Button(
        root,
        text="🔓  Unlock 120 FPS",
        command=lambda: on_unlock_fps(status_label),
        font=("Segoe UI", 13, "bold"),
        width=25,
        bg="#4CAF50",
        fg="white",
        cursor="hand2",
    ).pack(pady=(10, 8))

    Button(
        root,
        text="❌  Exit",
        command=root.destroy,
        font=("Segoe UI", 11),
        width=15,
        cursor="hand2",
    ).pack(pady=(10, 0))

    root.mainloop()
    return 0


def on_unlock_fps(status_label):
    """Handle FPS unlock button click."""
    paths = find_wuwa_steam_paths()
    if paths is None:
        return
    result = unlock_fps(paths)
    if result:
        status_label.config(text="✅ FPS successfully unlocked to 120!")


if __name__ == "__main__":
    sys.exit(main())
