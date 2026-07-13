"""
FPS Unlocker — Set Wuthering Waves FPS cap to 120.
Modifies LocalStorage.db (SQLite) and GameUserSettings.ini.
"""

import sqlite3
import json
import configparser
from pathlib import Path
from tkinter import messagebox

from process_check import is_game_running
from steam_finder import GamePaths

TARGET_FPS = 120


# Default menu data structures for 120 FPS support
MENU_DATA = {
    "___MetaType___": "___Map___",
    "Content": [
        [1, 100], [2, 100], [3, 100], [4, 100], [5, 0], [6, 0],
        [7, -0.4658685302734375], [10, 3], [11, 3], [20, 0], [21, 0],
        [22, 0], [23, 0], [24, 0], [25, 0], [26, 0], [27, 0], [28, 0],
        [29, 0], [30, 0], [31, 0], [32, 0], [33, 0], [34, 0], [35, 0],
        [36, 0], [37, 0], [38, 0], [39, 0], [40, 0], [41, 0], [42, 0],
        [43, 0], [44, 0], [45, 0], [46, 0], [47, 0], [48, 0], [49, 0],
        [50, 0], [51, 1], [52, 1], [53, 0], [54, 3], [55, 1], [56, 2],
        [57, 1], [58, 1], [59, 1], [61, 0], [62, 0], [63, 1], [64, 1],
        [65, 0], [66, 0], [67, 3], [68, 2], [69, 100], [70, 100], [79, 1],
        [81, 0], [82, 1], [83, 1], [84, 0], [85, 0], [87, 0], [88, 0],
        [89, 50], [90, 50], [91, 50], [92, 50], [93, 1], [99, 0], [100, 30],
        [101, 0], [102, 1], [103, 0], [104, 50], [105, 0], [106, 0.3],
        [107, 0], [112, 0], [113, 0], [114, 0], [115, 0], [116, 0],
        [117, 0], [118, 0], [119, 0], [120, 0], [121, 1], [122, 1],
        [123, 0], [130, 0], [131, 0], [132, 1], [135, 1], [133, 0],
    ],
}

PLAY_MENU_INFO = {
    "1": 100, "2": 100, "3": 100, "4": 100, "5": 0, "6": 0,
    "7": -0.4658685302734375, "10": 3, "11": 3, "20": 0, "21": 0,
    "22": 0, "23": 0, "24": 0, "25": 0, "26": 0, "27": 0, "28": 0,
    "29": 0, "30": 0, "31": 0, "32": 0, "33": 0, "34": 0, "35": 0,
    "36": 0, "37": 0, "38": 0, "39": 0, "40": 0, "41": 0, "42": 0,
    "43": 0, "44": 0, "45": 0, "46": 0, "47": 0, "48": 0, "49": 0,
    "50": 0, "51": 1, "52": 1, "53": 0, "54": 3, "55": 1, "56": 2,
    "57": 1, "58": 1, "59": 1, "61": 0, "62": 0, "63": 1, "64": 1,
    "65": 0, "66": 0, "67": 3, "68": 2, "69": 100, "70": 100, "79": 1,
    "81": 0, "82": 1, "83": 1, "84": 0, "85": 0, "87": 0, "88": 0,
    "89": 50, "90": 50, "91": 50, "92": 50, "93": 1, "99": 0, "100": 30,
    "101": 0, "102": 1, "103": 0, "104": 50, "105": 0, "106": 0.3,
    "107": 0, "112": 0, "113": 0, "114": 0, "115": 0, "116": 0,
    "117": 0, "118": 0, "119": 0, "120": 0, "121": 1, "122": 1,
    "123": 0, "130": 0, "131": 0, "132": 1,
}


def unlock_fps(paths: GamePaths) -> bool:
    """
    Unlock FPS to 120 by modifying:
    1. LocalStorage.db — CustomFrameRate, MenuData, PlayMenuInfo + trigger
    2. GameUserSettings.ini — FrameRateLimit
    """
    if is_game_running():
        return False

    try:
        # === 1. Modify SQLite database ===
        db_files = list(paths.local_storage_dir.glob("LocalStorage*.db"))
        if not db_files:
            messagebox.showerror("Error", "LocalStorage.db not found!")
            return False

        db_path = db_files[0]
        db = sqlite3.connect(str(db_path))
        cursor = db.cursor()

        # Drop existing trigger if present
        cursor.execute("DROP TRIGGER IF EXISTS prevent_custom_frame_rate_update")

        # Create trigger to lock FPS value
        cursor.execute(f"""
            CREATE TRIGGER prevent_custom_frame_rate_update
            AFTER UPDATE OF value ON LocalStorage
            WHEN NEW.key = 'CustomFrameRate'
            BEGIN
                UPDATE LocalStorage
                SET value = {TARGET_FPS}
                WHERE key = 'CustomFrameRate';
            END;
        """)

        # Update FPS value
        cursor.execute(
            "UPDATE LocalStorage SET value = ? WHERE key = 'CustomFrameRate'",
            (TARGET_FPS,),
        )

        # Clean and re-insert menu data
        cursor.execute(
            "DELETE FROM LocalStorage WHERE key IN ('MenuData', 'PlayMenuInfo')"
        )
        cursor.executemany(
            "INSERT INTO LocalStorage (key, value) VALUES (?, ?)",
            [
                ("MenuData", json.dumps(MENU_DATA)),
                ("PlayMenuInfo", json.dumps(PLAY_MENU_INFO)),
            ],
        )

        db.commit()
        db.close()

        # === 2. Update GameUserSettings.ini ===
        config = configparser.ConfigParser()
        if paths.game_settings_ini.exists():
            config.read(str(paths.game_settings_ini))

        section = "/Script/Engine.GameUserSettings"
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, "FrameRateLimit", str(TARGET_FPS))

        with open(str(paths.game_settings_ini), "w") as f:
            config.write(f)

        messagebox.showinfo(
            "Success! ✅",
            f"FPS successfully unlocked to {TARGET_FPS}!\n\n"
            "You can launch the game now.\n"
            "If it doesn't take effect immediately, restart the game once or twice."
        )
        return True

    except sqlite3.OperationalError as e:
        if "readonly" in str(e).lower():
            messagebox.showerror(
                "Access Error",
                "Database is read-only. Try running the program as Administrator."
            )
        else:
            messagebox.showerror("Database Error", f"SQLite error:\n\n{e}")
        return False

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n\n{e}")
        return False
