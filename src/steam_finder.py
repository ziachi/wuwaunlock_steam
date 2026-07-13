"""
Auto-detect Wuthering Waves installation path for Steam.
Searches Steam library folders and common install locations.
"""

import os
import re
import glob
from pathlib import Path
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from dataclasses import dataclass
from typing import Optional


@dataclass
class GamePaths:
    """All relevant game config paths."""
    game_dir: Path               # Root game directory (where Wuthering Waves.exe lives)
    local_storage_dir: Path      # Client/Saved/LocalStorage/
    game_settings_ini: Path      # Client/Saved/Config/WindowsNoEditor/GameUserSettings.ini
    engine_ini: Path             # Client/Saved/Config/WindowsNoEditor/Engine.ini


def get_steam_library_folders() -> list[str]:
    """Read Steam's libraryfolders.vdf to find all Steam library paths."""
    steam_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
        os.path.expandvars(r"%ProgramFiles%\Steam"),
        r"C:\Steam",
        r"D:\Steam",
        r"E:\Steam",
    ]

    library_dirs = []

    for steam_path in steam_paths:
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            try:
                with open(vdf_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Parse "path" values from VDF
                paths = re.findall(r'"path"\s+"([^"]+)"', content)
                library_dirs.extend(paths)
            except Exception:
                pass
            # Also add the main Steam directory
            if steam_path not in library_dirs:
                library_dirs.append(steam_path)

    return library_dirs


def find_wuwa_in_steam_libraries() -> Optional[Path]:
    """Search Steam library folders for Wuthering Waves."""
    possible_folder_names = [
        "Wuthering Waves",
        "WutheringWaves",
    ]

    library_dirs = get_steam_library_folders()

    for lib_dir in library_dirs:
        steamapps = os.path.join(lib_dir, "steamapps", "common")
        if not os.path.exists(steamapps):
            continue
        for folder_name in possible_folder_names:
            game_dir = os.path.join(steamapps, folder_name, "Wuthering Waves Game")
            exe_path = os.path.join(game_dir, "Wuthering Waves.exe")
            if os.path.exists(exe_path):
                return Path(game_dir)

    return None


def find_wuwa_common_paths() -> Optional[Path]:
    """Check common install locations outside Steam."""
    common_dirs = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Wuthering Waves\Wuthering Waves Game",
        r"C:\Wuthering Waves\Wuthering Waves Game",
        r"C:\Program Files\Wuthering Waves\Wuthering Waves Game",
        r"D:\Wuthering Waves\Wuthering Waves Game",
        r"D:\Program Files\Wuthering Waves\Wuthering Waves Game",
        r"D:\Games\Wuthering Waves\Wuthering Waves Game",
        r"D:\SteamLibrary\steamapps\common\Wuthering Waves\Wuthering Waves Game",
        r"E:\SteamLibrary\steamapps\common\Wuthering Waves\Wuthering Waves Game",
        r"E:\Steam\steamapps\common\Wuthering Waves\Wuthering Waves Game",
        r"E:\Program Files (x86)\Steam\steamapps\common\Wuthering Waves\Wuthering Waves Game",
        r"E:\Wuthering Waves\Wuthering Waves Game",
    ]

    for dir_path in common_dirs:
        exe_path = os.path.join(dir_path, "Wuthering Waves.exe")
        if os.path.exists(exe_path):
            return Path(dir_path)

    return None


def ask_manual_browse(initial_dir: Optional[str] = None) -> Optional[Path]:
    """Let user manually browse for Wuthering Waves.exe."""
    filepath = askopenfilename(
        initialdir=initial_dir,
        title='Select "Wuthering Waves.exe" in your game folder',
        filetypes=[("Exe files", "Wuthering Waves.exe")],
    )
    if not filepath:
        return None
    return Path(filepath).parent


def validate_game_paths(game_dir: Path) -> Optional[GamePaths]:
    """Validate that all required config paths exist."""
    local_storage = game_dir / "Client" / "Saved" / "LocalStorage"
    game_settings = game_dir / "Client" / "Saved" / "Config" / "WindowsNoEditor" / "GameUserSettings.ini"
    engine_ini = game_dir / "Client" / "Saved" / "Config" / "WindowsNoEditor" / "Engine.ini"

    # LocalStorage must exist (game must have been run at least once)
    if not local_storage.is_dir():
        messagebox.showerror(
            "Error",
            "LocalStorage folder not found.\n\n"
            "Make sure the game has been launched at least once!"
        )
        return None

    # Check LocalStorage DB files
    db_files = sorted(glob.glob(str(local_storage / "LocalStorage*.db")))
    if len(db_files) == 0:
        messagebox.showerror(
            "Error",
            "LocalStorage.db file not found.\n\n"
            "Make sure the game has been launched at least once!"
        )
        return None
    elif len(db_files) > 1:
        files_list = "\n".join(db_files)
        messagebox.showerror(
            "Error",
            f"Multiple LocalStorage files found:\n\n{files_list}\n\n"
            "This is usually caused by a game crash. To fix:\n"
            "1) Close the game and launcher\n"
            "2) Delete all files in the LocalStorage folder\n"
            "3) Launch the game once, then close it\n"
            "4) Run this tool again"
        )
        return None

    return GamePaths(
        game_dir=game_dir,
        local_storage_dir=local_storage,
        game_settings_ini=game_settings,
        engine_ini=engine_ini,
    )


def find_wuwa_steam_paths() -> Optional[GamePaths]:
    """
    Main entry: find Wuthering Waves and return validated paths.
    Tries auto-detect first, falls back to manual browse.
    """
    game_dir = find_wuwa_in_steam_libraries()

    if game_dir is None:
        game_dir = find_wuwa_common_paths()

    if game_dir is None:
        messagebox.showinfo(
            "Auto-Detect",
            "Could not auto-detect the game location.\n\n"
            'Please select "Wuthering Waves.exe" manually.'
        )
        game_dir = ask_manual_browse()
        if game_dir is None:
            return None

    paths = validate_game_paths(game_dir)
    if paths is None:
        return None

    messagebox.showinfo(
        "Game Found",
        f"Game found at:\n{game_dir}"
    )
    return paths
