# 🎮 WuWa Unlock Steam

**Wuthering Waves FPS Unlocker — Steam Edition**

Unlock 120 FPS in Wuthering Waves (Steam version).

This tool **only** modifies game configuration files — no game files are touched.

## Features

- 🔓 Unlock 120 FPS (bypasses hardware whitelist)
- 🔍 Auto-detects Steam install location
- 🛡️ Only modifies settings files, not game files
- 🚫 Zero network calls — fully offline
- 📦 Zero dependencies — uses only Python standard library

## Usage

```bash
cd src
python main.py
```

No `pip install` required — everything uses Python built-in libraries.

### Build EXE (Optional)

```bash
pip install pyinstaller
cd src
pyinstaller --onefile --windowed --name="WuWaUnlockSteam" main.py
```

## Default Game Path (Steam)

```
C:\Program Files (x86)\Steam\steamapps\common\Wuthering Waves\Wuthering Waves Game
```

The tool auto-detects your Steam library folders. If auto-detection fails, you can manually browse for `Wuthering Waves.exe`.

## Files Modified

All files are located inside the game folder:

| File | Purpose |
|---|---|
| `Client/Saved/LocalStorage/LocalStorage.db` | SQLite — sets FPS value + creates a trigger to keep it locked |
| `Client/Saved/Config/WindowsNoEditor/GameUserSettings.ini` | Sets FrameRateLimit to 120 |

## Project Structure

```
wuwaunlock_steam/
├── README.md
└── src/
    ├── main.py              # Entry point + GUI
    ├── version_info.py      # Version metadata
    ├── steam_finder.py      # Auto-detect game path
    ├── process_check.py     # Check if game is running
    └── fps_unlocker.py      # FPS unlock logic
```

## Requirements

- Python 3.10+
- Windows 10/11
- No external packages needed

## Credits

Based on [WuWa_Simple_FPSUnlocker](https://github.com/WakuWakuPadoru/WuWa_Simple_FPSUnlocker) by [WakuWakuPadoru](https://github.com/WakuWakuPadoru). Original project supports both FPS unlock and Raytracing settings for the standalone launcher version.

## Notes

- Run the game at least once before using this tool
- Make sure the game is NOT running when using this tool
- You may need to run the tool again after a game update
- If the game is installed in Program Files, run as Administrator
