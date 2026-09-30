# Test Drive III: The Passion (1990) — PlayStation®Vita Port

A native, hardware-accelerated PlayStation®Vita and PlayStation®TV port of **Test Drive III: The Passion (1990)**, based on the static recompilation and reverse-engineering work by **kylofon** ([`test-drive-3-sdl3`](https://github.com/kylofon/test-drive-3-sdl3)).

This port brings Accolade's groundbreaking 1990 3D polygon racing sequel to the PS Vita with smooth 60 FPS presentation via VitaGL / GXM hardware acceleration, authentic AdLib / Sound Blaster FM music and sound synthesis via **Nuked-OPL3**, responsive physical controls, dynamic multi-mode aspect scaling, expansion disk support, and a Sony TRC-compliant LiveArea digital user manual.

---

## Features

- **Hardware Acceleration**: Smooth 60 FPS presentation powered by VitaSDK's SDL2 with VitaGL / GXM GPU backend.
- **True 3D Filled-Polygon World**: Free driving over realistic scenic courses with multiple route choices, side roads, and scenic shortcuts.
- **Authentic AdLib & PC Speaker Sound**: Bundled Yamaha YMF262 (OPL2) FM synthesis via Nuked-OPL3 playing Russell Shiffer's original soundtrack and engine sounds in 44.1 kHz stereo.
- **Tri-Mode Aspect Ratio Engine**: Toggle between 3 display modes in real time with the **`Select`** button:
  - **Mode 1 (Boot Default)**: 4:3 Aspect-Correct ($725 \times 544$ pillarboxed) — authentic retro CRT proportion with full cockpit dashboard visibility.
  - **Mode 2**: 2× Integer Scale ($640 \times 400$ / $640 \times 480$ centered) — razor-sharp pixel doubling matching original DOS VGA scanlines.
  - **Mode 0**: 16:9 Widescreen Stretch ($960 \times 544$) — full edge-to-edge panoramic view filling the 5-inch OLED/LCD display.
- **Ergonomic Vita Controls**: Full support for Left Stick analog steering, D-Pad, face buttons, shoulder trigger pedals (R for Gas, L for Brake), and manual sequential shifting (Triangle for Shift Up, Square for Shift Down).
- **Cockpit Actions & Shortcuts**: Toggle windshield wipers (D-Pad ▼) in rainstorms, pop on headlights (L + Circle) at dusk, switch radio stations (D-Pad ▲), switch to chase camera (L + Triangle), check rearview mirror (L + Square), and trigger 3D instant replays (L + Cross).
- **Hybrid Filesystem & Persistent Saves**: High scores (`<scene>.hi`), last car/course choices (`playdisk.dat`), and options (`td3.cfg`) are written directly to `ux0:data/TestDrive3/`, avoiding Sony's read-only `app0:` restriction.
- **Add-on Expansion Disks**: Drop optional Car Disks and Scenery Disks into `ux0:data/TestDrive3/` and the game automatically recognizes them!
- **Built-in LiveArea User Manual**: A complete 5-page digital manual installed to `sce_sys/manual/`, accessible directly from the LiveArea book icon.
- **Sony TRC Compliant**: All LiveArea & manual PNGs strictly 8-bit indexed palette (`color_type=3`, non-interlaced, no alpha in `icon0.png`) preventing VitaShell error `0x8010113D`.

---

## Important Notice: Game Data Setup

> [!IMPORTANT]
> **Proprietary game assets are NOT bundled in the release VPK.**
> To comply with copyright laws, you must provide the original game data from your legally owned copy of the original DOS version of *Test Drive III: The Passion* (Version 3.0) by Accolade. **It will not work with Version 1.0 of the game it has to be 3.0**

### How to Install Game Files

1. Install `TestDrive3Vita.vpk` on your PS Vita using **VitaShell**.
2. Launch **VitaShell** and press **`Select`** to start a **USB** or **FTP** connection.
3. On your PS Vita memory card, navigate to:
   ```
   ux0:data/TestDrive3/
   ```
   *(This directory is created automatically when the game first launches, or you can create it manually).*
4. Copy all files from your original DOS version into `ux0:data/TestDrive3/`.

### Required Files Checklist

| File | Type | Description |
| :--- | :--- | :--- |
| **`TDIII.EXE`** | **Required** | **Version 3.0 not 1.0** primary game executable (~125 KB packed / 166 KB unpacked) |
| **`DATAA.DAT`** | **Required** | Menus, screens, title animations, and UI art |
| **`DATAB.DAT`** | **Required** | High-resolution illustrations and splash art |
| **`DATAC.DAT`** | **Required** | VGA color palettes and lookup tables |
| **`INSTR.DAT`** | **Required** | AdLib / Sound Blaster FM instrument bank |
| **`PLAYDISK.DAT`** | **Required** | Car and scenery disk manifest |
| **`C*.DAT/.LST/.POB`** | **Required** | Car 3D models, specifications, and cockpit graphics |
| **`SCENE*.DAT/.LST`** | **Required** | Course scenery and 3D world networks |
| **`SCENE*.HI`** | Optional | High score table (created automatically if missing) |
| **`TD3.CFG`** | Optional | Saved configuration (created automatically if missing) |

*Note: The game engine resolves filenames case-insensitively, so both lowercase (`tdiii.exe`) and uppercase (`TDIII.EXE`) work seamlessly.*

---

## Controls

### In-Game Driving

| Input | Action | Description |
| :--- | :--- | :--- |
| **Left Stick** or **D-Pad ◄ / ►** | **Steer** | Turn vehicle left and right with analog precision |
| **Cross ($\times$)** / **R Trigger** / **D-Pad ▲** | **Gas (Accelerate)** | Depress accelerator pedal |
| **L Trigger** / **D-Pad ▼** | **Brake** | Apply vehicle brakes |
| **Triangle ($\triangle$)** | **Shift Up** | Shift manual transmission to higher gear ('A' key) |
| **Square ($\square$)** | **Shift Down** | Shift manual transmission to lower gear ('Z' key) |
| **Circle ($\bigcirc$)** | **Spacebar / Action** | Hard brake / Emergency stop |
| **Select** | **Cycle Display Mode** | Switch between 4:3, 2× Integer, and 16:9 |
| **Start** | **Pause / Menu** | Pause gameplay or exit current drive (`Esc`) |

### Cockpit Shortcuts (L-Trigger Chords)

| Combination | Action | Description |
| :--- | :--- | :--- |
| **L + Triangle** | **Chase View** | Toggle between cockpit and external 3D chase camera (F5) |
| **L + Square** | **Rearview Mirror** | Toggle cockpit mirror display on/off ('R' key) |
| **L + Circle** | **Headlights** | Toggle headlights for night / fog driving ('H' key) |
| **L + Cross** | **Instant Replay** | Replay last 15 seconds of driving from any angle (F10) |
| **L + Start** | **Return to Road** | Tow vehicle back onto the center tarmac (F6) |
| **D-Pad ▲** | **Radio Station** | Cycle through FM radio music tracks ('M' key) |
| **D-Pad ▼** | **Wipers** | Clear raindrops and windshield splatter ('W' key) |

---

## Building from Source

### Prerequisites
- [Docker](https://www.docker.com/) (recommended) or a local installation of [VitaSDK](https://vitasdk.org/).

### Build using Docker (One-Liner)

```bash
# Clone repository
git clone https://github.com/gainusha/TestDrive3Vita.git
cd TestDrive3Vita

# Build clean release VPK (without bundled DOS files)
docker run --platform linux/amd64 --rm -v "$(pwd):/src" -w /src vitasdk/vitasdk bash -c "
  cmake -B build-vita -DCMAKE_TOOLCHAIN_FILE=/usr/local/vitasdk/share/vita.toolchain.cmake -DBUNDLE_GAME_DATA=OFF &&
  cmake --build build-vita
"
```

The output package `TestDrive3Vita.vpk` will be generated in the root directory.

### CMake Build Options

- `-DBUNDLE_GAME_DATA=OFF` *(Default for releases)*: Builds a clean, standalone VPK with zero copyrighted DOS assets bundled (~930 KB).
- `-DBUNDLE_GAME_DATA=ON` : Bundles local files from `Game/` into the VPK under `app0:Game/` for self-testing in Vita3K.

---

## Credits & Acknowledgments

- **[kylofon](https://github.com/kylofon)** — Creator of the extraordinary [**test-drive-3-sdl3**](https://github.com/kylofon/test-drive-3-sdl3) static recompilation and reverse-engineering work.
- **Accolade** — Tom Loughry, Russell Shiffer, and the original team behind *Test Drive III: The Passion* (1990).
- **[Nuke.YKT](https://github.com/nukeykt/Nuked-OPL3)** — Author of the Nuked-OPL3 Yamaha YMF262 FM synthesizer emulator.
- **VitaSDK Team** — For the open-source cross-compiler toolchain and Sony PS Vita homebrew libraries.
- **Vita3K Team** — For the PlayStation Vita emulator facilitating development and testing.
