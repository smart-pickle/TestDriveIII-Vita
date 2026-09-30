#!/usr/bin/env python3
"""
Generate Sony PS Vita TRC-compliant LiveArea User Manual pages (960x544 PNG).
Creates 5 comprehensive, pixel-perfect, highly readable pages for Test Drive III: The Passion:
  001.png - Cover & Introduction
  002.png - Game Data Setup & File Installation
  003.png - PlayStation Vita Controls & Cockpit Shortcuts
  004.png - Cockpit Instruments, Radar Detector & Driving Features
  005.png - The Supercars, Courses & Expansion Disks
"""

import os
from PIL import Image, ImageDraw, ImageFont

WIDTH = 960
HEIGHT = 544
TOTAL_PAGES = 5
OUTPUT_DIR = "vpk/manual"

# Color Palette
BG_DARK = (14, 18, 26)
BG_CARD = (22, 28, 42)
BG_CARD_ALT = (28, 36, 52)
BORDER_MUTED = (45, 58, 82)
CYAN_ACCENT = (0, 212, 255)
GOLD_ACCENT = (255, 183, 3)
RED_ACCENT = (255, 61, 87)
GREEN_ACCENT = (0, 230, 118)
TEXT_WHITE = (245, 248, 255)
TEXT_MUTED = (160, 175, 200)
TEXT_DIM = (110, 125, 145)

# PlayStation Button Colors
COLOR_CROSS = (41, 121, 255)
COLOR_CIRCLE = (255, 61, 0)
COLOR_SQUARE = (224, 64, 251)
COLOR_TRIANGLE = (0, 230, 118)
COLOR_TRIGGER = (80, 95, 120)

# Fonts
FONT_DIR = "/System/Library/Fonts/Supplemental"
try:
    FONT_TITLE_HERO = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 36)
    FONT_PAGE_TITLE = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 25)
    FONT_SECTION_HDR = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 16)
    FONT_SUBTITLE = ImageFont.truetype(f"{FONT_DIR}/Arial.ttf", 14)
    FONT_BODY_BOLD = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 14)
    FONT_BODY = ImageFont.truetype(f"{FONT_DIR}/Arial.ttf", 13)
    FONT_BODY_SM = ImageFont.truetype(f"{FONT_DIR}/Arial.ttf", 12)
    FONT_MONO = ImageFont.truetype(f"{FONT_DIR}/Courier New Bold.ttf", 13)
    FONT_MONO_SM = ImageFont.truetype(f"{FONT_DIR}/Courier New Bold.ttf", 11)
    FONT_BADGE = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 11)
except Exception:
    default = ImageFont.load_default()
    FONT_TITLE_HERO = default
    FONT_PAGE_TITLE = default
    FONT_SECTION_HDR = default
    FONT_SUBTITLE = default
    FONT_BODY_BOLD = default
    FONT_BODY = default
    FONT_BODY_SM = default
    FONT_MONO = default
    FONT_MONO_SM = default
    FONT_BADGE = default


def draw_badge(draw, x, y, text, bg_color, text_color=TEXT_WHITE, border=None):
    bbox = FONT_BADGE.getbbox(text)
    w = bbox[2] - bbox[0] + 16
    h = 22
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg_color, outline=border, width=1 if border else 0)
    draw.text((x + 8, y + 4), text, font=FONT_BADGE, fill=text_color)
    return w


def create_base(page_num, title, subtitle):
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(im)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_DARK[0] * (1 - ratio * 0.4) + 20 * (ratio * 0.4))
        g = int(BG_DARK[1] * (1 - ratio * 0.4) + 25 * (ratio * 0.4))
        b = int(BG_DARK[2] * (1 - ratio * 0.4) + 38 * (ratio * 0.4))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Top Header Bar (0..40)
    draw.rectangle([0, 0, WIDTH, 40], fill=(20, 26, 38))
    draw.line([(0, 40), (WIDTH, 40)], fill=GOLD_ACCENT, width=2)

    draw_badge(draw, 24, 10, "PLAYSTATION®VITA", GOLD_ACCENT, (10, 20, 30), border=GOLD_ACCENT)
    draw.text((155, 12), "TEST DRIVE III: THE PASSION (1990)", font=FONT_BODY_BOLD, fill=TEXT_MUTED)

    page_str = f"PAGE {page_num} OF {TOTAL_PAGES}"
    draw_badge(draw, WIDTH - 130, 10, page_str, (35, 45, 65), TEXT_WHITE, border=BORDER_MUTED)

    # Title & Subtitle
    draw.text((28, 52), title, font=FONT_PAGE_TITLE, fill=TEXT_WHITE)
    draw.text((30, 83), subtitle, font=FONT_SUBTITLE, fill=TEXT_MUTED)
    draw.line([(28, 102), (WIDTH - 28, 102)], fill=BORDER_MUTED, width=1)

    # Footer (512..544)
    draw.line([(28, 510), (WIDTH - 28, 510)], fill=BORDER_MUTED, width=1)
    footer_text = "Swipe screen or use D-Pad / L/R to turn pages  •  Press PS Button to return"
    draw.text((WIDTH // 2 - 210, 518), footer_text, font=FONT_BODY_SM, fill=TEXT_DIM)

    return im, draw


# ==============================================================================
# PAGE 1: Cover & Overview
# ==============================================================================
def make_page_1():
    im, draw = create_base(1, "TEST DRIVE III: THE PASSION", "Instruction Manual — Accolade / Distinctive Software (1990)")

    # Left Column: Hero Box
    draw.rounded_rectangle([28, 114, 460, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.rounded_rectangle([44, 130, 444, 200], radius=6, fill=(16, 22, 34), outline=GOLD_ACCENT, width=2)
    draw.text((60, 142), "TEST DRIVE III", font=FONT_TITLE_HERO, fill=TEXT_WHITE)
    draw.text((62, 178), "THE PASSION", font=FONT_SECTION_HDR, fill=GOLD_ACCENT)

    intro_p1 = (
        "Welcome to the groundbreaking 1990 sequel to the Test Drive series, now running "
        "natively on PlayStation®Vita! Unlike the pseudo-3D sprite scaling of its predecessors, "
        "Test Drive III features a revolutionary true 3D filled-polygon world with free-roaming "
        "open roads, picturesque branching shortcuts, dynamic weather, and head-to-head competition."
    )
    y = 216
    for line in [intro_p1[:75], intro_p1[75:148], intro_p1[148:224], intro_p1[224:]]:
        draw.text((44, y), line, font=FONT_BODY, fill=TEXT_MUTED)
        y += 18

    draw.line([(44, 305), (444, 305)], fill=BORDER_MUTED, width=1)
    draw.text((44, 318), "PORT SPECIFICATIONS & ENHANCEMENTS", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    specs = [
        ("Platform", "PlayStation®Vita & PlayStation®TV (Native ARM)"),
        ("Renderer", "Hardware Accelerated VGA 320x200 via SDL2 / VitaGL"),
        ("Framerate", "Authentic 145.65 Hz PIT Pacing (Configurable)"),
        ("Sound Synthesizer", "Yamaha YMF262 (OPL2) via Nuked-OPL3 Stereo"),
        ("Display Modes", "Tri-Mode (4:3 Pillarbox, 2x Integer, 16:9 Stretch)"),
        ("Original Base", "Reverse-Engineered C Port by kylofon"),
    ]
    y = 345
    for k, v in specs:
        draw.text((44, y), k, font=FONT_BODY_BOLD, fill=TEXT_WHITE)
        draw.text((180, y), v, font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 24

    # Right Column: Game Modes
    draw.rounded_rectangle([480, 114, 932, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((500, 128), "THE PASSION OF RACING", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    features = [
        ("FREE-ROAMING 3D COURSES", "Drive across Pacific to Yosemite or Cape Cod to Niagara with full freedom to take side roads and scenic shortcuts."),
        ("AUTHENTIC ADLIB SOUNDTRACK", "Enjoy Russell Shiffer's vibrant FM synth themes and realistic engine rumblings emulated via Nuked-OPL3."),
        ("5 EXOTIC SUPERCARS", "Take the wheel of the Chevrolet CERV III, Acura NSX, Lamborghini Diablo, Ferrari Mythos, and Dodge Stealth R/T."),
        ("ACTIVE COCKPIT CONTROLS", "Operate functioning windshield wipers during rain storms, toggle headlights at dusk, switch radio stations, and adjust mirrors."),
        ("SMART TRAFFIC & HIGHWAY PATROL", "Navigate commuter traffic and watch your radar detector—the police radar cruiser is always on patrol!"),
    ]
    y = 156
    for title, desc in features:
        draw.rounded_rectangle([500, y, 912, y + 58], radius=6, fill=BG_CARD_ALT, outline=BORDER_MUTED, width=1)
        draw.text((512, y + 8), title, font=FONT_BODY_BOLD, fill=GOLD_ACCENT)
        draw.text((512, y + 26), desc[:62], font=FONT_BODY_SM, fill=TEXT_MUTED)
        if len(desc) > 62:
            draw.text((512, y + 40), desc[62:125], font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 66

    im.save(f"{OUTPUT_DIR}/001.png")
    print("Created vpk/manual/001.png")


# ==============================================================================
# PAGE 2: Game Data Setup
# ==============================================================================
def make_page_2():
    im, draw = create_base(2, "GAME DATA SETUP & INSTALLATION", "Required DOS Data Files & Add-On Expansion Disks")

    # Important Box
    draw.rounded_rectangle([28, 114, 932, 172], radius=6, fill=(40, 20, 25), outline=RED_ACCENT, width=2)
    draw_badge(draw, 44, 124, "COPYRIGHT NOTICE", RED_ACCENT, TEXT_WHITE)
    draw.text((180, 126), "PROPRIETARY GAME ASSETS ARE NOT BUNDLED IN RELEASE VPKs", font=FONT_BODY_BOLD, fill=TEXT_WHITE)
    msg = "To play, you must copy original data files from your legally owned copy of Test Drive III: The Passion into ux0:data/TestDrive3/."
    draw.text((44, 150), msg, font=FONT_BODY_SM, fill=(240, 200, 205))

    # Installation Steps (Left Box)
    draw.rounded_rectangle([28, 184, 460, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((44, 196), "INSTALLATION INSTRUCTIONS", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    steps = [
        ("Step 1", "Install TestDrive3Vita.vpk using VitaShell on your PS Vita."),
        ("Step 2", "Launch VitaShell and press Select to connect USB or FTP to PC."),
        ("Step 3", "Navigate to your PS Vita memory card directory:\nux0:data/TestDrive3/\n(Directory is created automatically on first boot, or manually)."),
        ("Step 4", "Copy TDIII.EXE (Version 3.0), DATAA.DAT, DATAB.DAT,\nDATAC.DAT, INSTR.DAT, and car/scene files into the folder."),
        ("Step 5", "Launch Test Drive III from your LiveArea screen and drive!"),
    ]
    y = 222
    for step_num, step_desc in steps:
        draw_badge(draw, 44, y, step_num, (35, 45, 65), CYAN_ACCENT, border=BORDER_MUTED)
        lines = step_desc.split("\n")
        draw.text((110, y + 2), lines[0], font=FONT_BODY_SM, fill=TEXT_WHITE)
        if len(lines) > 1:
            draw.text((110, y + 18), lines[1], font=FONT_MONO_SM, fill=GOLD_ACCENT)
        if len(lines) > 2:
            draw.text((110, y + 32), lines[2], font=FONT_BODY_SM, fill=TEXT_MUTED)
            y += 14
        y += 48

    # Checklist Table (Right Box)
    draw.rounded_rectangle([480, 184, 932, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((496, 196), "DATA FILES CHECKLIST", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    headers = [("FILE", 496), ("TYPE", 620), ("PURPOSE", 710)]
    for h, x in headers:
        draw.text((x, 222), h, font=FONT_BODY_BOLD, fill=TEXT_MUTED)
    draw.line([(496, 238), (916, 238)], fill=BORDER_MUTED, width=1)

    files = [
        ("TDIII.EXE", "REQUIRED", "Version 3.0 Executable (125 KB packed)", GOLD_ACCENT),
        ("DATAA.DAT", "REQUIRED", "Front-end screens, menus, UI assets", GREEN_ACCENT),
        ("DATAB.DAT", "REQUIRED", "High-res images & game animations", GREEN_ACCENT),
        ("DATAC.DAT", "REQUIRED", "VGA color palettes & lookups", GREEN_ACCENT),
        ("INSTR.DAT", "REQUIRED", "AdLib / Sound Blaster FM instrument bank", GREEN_ACCENT),
        ("PLAYDISK.DAT", "REQUIRED", "Car & course disk manifest", GREEN_ACCENT),
        ("C*.DAT/.POB", "REQUIRED", "Car 3D models & cockpit art", GREEN_ACCENT),
        ("SCENE*.DAT", "REQUIRED", "Course scenery & 3D world maps", GREEN_ACCENT),
        ("SCENE*.HI", "AUTO-SAVED", "High score records (saved to ux0:)", CYAN_ACCENT),
    ]
    y = 246
    for fname, ftype, fdesc, clr in files:
        draw.text((496, y), fname, font=FONT_MONO, fill=clr)
        draw.text((620, y), ftype, font=FONT_BADGE, fill=TEXT_MUTED)
        draw.text((710, y), fdesc, font=FONT_BODY_SM, fill=TEXT_WHITE)
        y += 26

    im.save(f"{OUTPUT_DIR}/002.png")
    print("Created vpk/manual/002.png")


# ==============================================================================
# PAGE 3: PlayStation Vita Controls
# ==============================================================================
def make_page_3():
    im, draw = create_base(3, "PLAYSTATION®VITA CONTROLS", "Responsive Physical Controls, Analog Steering & Cockpit Shortcuts")

    # In-Game Driving Controls (Left Box)
    draw.rounded_rectangle([28, 114, 460, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((44, 126), "PRIMARY DRIVING CONTROLS", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    controls = [
        ("Left Stick", "Analog Steering", "Smooth proportional vehicle turning"),
        ("D-Pad ◄ / ►", "Digital Steering", "Quick steering taps & menu browsing"),
        ("Cross (X) / R", "Gas Pedal", "Depress accelerator / Full throttle"),
        ("L Trigger", "Brake Pedal", "Foot brake / Deceleration"),
        ("Triangle", "Shift Up", "Upshift manual transmission (A key)"),
        ("Square", "Shift Down", "Downshift manual transmission (Z key)"),
        ("Circle", "Spacebar", "Emergency handbrake / Menu confirm"),
        ("Start", "Pause / Menu", "Pause game / Cancel / Exit drive"),
        ("Select", "Display Mode", "Cycle 4:3, 2x Integer, 16:9 Stretch"),
    ]
    y = 154
    for btn, act, desc in controls:
        draw.rounded_rectangle([44, y, 140, y + 26], radius=4, fill=BG_CARD_ALT, outline=BORDER_MUTED, width=1)
        draw.text((48, y + 5), btn, font=FONT_BODY_SM, fill=GOLD_ACCENT)
        draw.text((150, y + 2), act, font=FONT_BODY_BOLD, fill=TEXT_WHITE)
        draw.text((150, y + 16), desc, font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 36

    # Cockpit Shortcuts & Chords (Right Box)
    draw.rounded_rectangle([480, 114, 932, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((496, 126), "COCKPIT CHORDS (L-TRIGGER COMBOS)", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    shortcuts = [
        ("L + Triangle", "Chase Car View (F5)", "Toggle between interior cockpit and external 3D chase camera view."),
        ("L + Square", "Rearview Mirror (R)", "Toggle the functional rearview mirror display on or off."),
        ("L + Circle", "Headlights Toggle (H)", "Turn vehicle headlights on or off for dusk and nighttime driving."),
        ("L + Cross", "Instant Replay (F10)", "Rewind and view the last 15 seconds of your drive in 3D replay."),
        ("L + Start", "Return to Road (F6)", "Call the emergency tow service back to the center of the tarmac."),
        ("D-Pad ▲", "Change Radio (M)", "Cycle through radio stations for upbeat Russell Shiffer FM tracks."),
        ("D-Pad ▼", "Windshield Wipers (W)", "Wipe away raindrops, snow flurries, and dirty windshield splatters."),
    ]
    y = 154
    for chord, act, desc in shortcuts:
        draw.rounded_rectangle([496, y, 600, y + 26], radius=4, fill=(35, 45, 65), outline=CYAN_ACCENT, width=1)
        draw.text((502, y + 5), chord, font=FONT_BODY_SM, fill=CYAN_ACCENT)
        draw.text((612, y + 2), act, font=FONT_BODY_BOLD, fill=TEXT_WHITE)
        draw.text((612, y + 16), desc[:52], font=FONT_BODY_SM, fill=TEXT_MUTED)
        if len(desc) > 52:
            draw.text((612, y + 28), desc[52:105], font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 46

    im.save(f"{OUTPUT_DIR}/003.png")
    print("Created vpk/manual/003.png")


# ==============================================================================
# PAGE 4: Cockpit Instruments & Driving Features
# ==============================================================================
def make_page_4():
    im, draw = create_base(4, "COCKPIT INSTRUMENTS & DRIVING FEATURES", "Understanding Your Dashboard, Gated Shifting & Road Hazards")

    # Left Column: Dashboard Instruments
    draw.rounded_rectangle([28, 114, 460, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((44, 126), "COCKPIT DASHBOARD INSTRUMENTS", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    gauges = [
        ("TACHOMETER & ENGINE RPM", "Monitor your engine revs closely! Redlining for more than a few seconds will blow the cylinder head and terminate your drive."),
        ("SPEEDOMETER & GEAR LEVER", "Test Drive III features authentic gated manual transmissions. Upshift at torque peaks (Triangle) and downshift for corners (Square)."),
        ("VISOR RADAR DETECTOR", "Mounted near your visor, the detector flashes red and beeps urgently when police radar traps are active. Brake immediately!"),
        ("REARVIEW MIRROR", "Keep an eye on computer opponents trying to overtake you. Press L + Square (R key) to toggle the mirror."),
    ]
    y = 154
    for title, desc in gauges:
        draw.rounded_rectangle([44, y, 444, y + 68], radius=6, fill=BG_CARD_ALT, outline=BORDER_MUTED, width=1)
        draw.text((54, y + 8), title, font=FONT_BODY_BOLD, fill=GOLD_ACCENT)
        draw.text((54, y + 26), desc[:55], font=FONT_BODY_SM, fill=TEXT_MUTED)
        draw.text((54, y + 40), desc[55:110], font=FONT_BODY_SM, fill=TEXT_MUTED)
        if len(desc) > 110:
            draw.text((54, y + 54), desc[110:], font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 76

    # Right Column: Road Hazards & Tactics
    draw.rounded_rectangle([480, 114, 932, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((496, 126), "TACTICS & ROAD SURVIVAL TIPS", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    hazards = [
        ("WEATHER & DIRTY WINDSHIELD", "Rainstorms and dirt trails will obscure your windshield. Press D-Pad ▼ (W key) to activate wipers before you lose visibility."),
        ("HEAD-TO-HEAD COMPUTER RACING", "The AI opponent is aggressive! They will cut across your lane and block passes. Use side roads and route branches to slip ahead."),
        ("BRANCHING HIGHWAY PATHS", "Unlike earlier titles, TD3 features an open world map. Watch the road signs and compass to discover alternate route legs."),
        ("INSTANT REPLAY THEATER", "Pulled off an incredible drift or catastrophic crash? Hit L + Cross (F10) to relive the action from any camera angle!"),
    ]
    y = 154
    for title, desc in hazards:
        draw.rounded_rectangle([496, y, 916, y + 68], radius=6, fill=BG_CARD_ALT, outline=BORDER_MUTED, width=1)
        draw.text((506, y + 8), title, font=FONT_BODY_BOLD, fill=RED_ACCENT)
        draw.text((506, y + 26), desc[:58], font=FONT_BODY_SM, fill=TEXT_MUTED)
        draw.text((506, y + 40), desc[58:115], font=FONT_BODY_SM, fill=TEXT_MUTED)
        if len(desc) > 115:
            draw.text((506, y + 54), desc[115:], font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 76

    im.save(f"{OUTPUT_DIR}/004.png")
    print("Created vpk/manual/004.png")


# ==============================================================================
# PAGE 5: The Supercars & Courses
# ==============================================================================
def make_page_5():
    im, draw = create_base(5, "THE SUPERCARS & EXPANSION COURSES", "Vehicle Specifications, Course Overview & Community Credits")

    # Supercars Box (Left)
    draw.rounded_rectangle([28, 114, 460, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((44, 126), "THE 5 EXOTIC SUPERCARS", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    cars = [
        ("CHEVROLET CERV III", "650 HP Twin-Turbo 5.7L V8 • AWD • 225 MPH", "Experimental engineering wonder with computerized active suspension."),
        ("ACURA NSX", "270 HP 3.0L V6 VTEC • Mid-Engine RWD • 168 MPH", "Precision handling and legendary chassis tuned by Ayrton Senna."),
        ("LAMBORGHINI DIABLO", "485 HP 5.7L V12 • Mid-Engine RWD • 202 MPH", "The ultimate raging bull with explosive raw acceleration."),
        ("FERRARI MYTHOS", "390 HP 4.9L Flat-12 • Mid-Engine RWD • 180 MPH", "Breathtaking Pininfarina speedster built on the Testarossa chassis."),
        ("DODGE STEALTH R/T", "300 HP Twin-Turbo 3.0L V6 • AWD / 4WS • 160 MPH", "High-tech American muscle packed with twin turbos and four-wheel steer."),
    ]
    y = 152
    for car_name, specs, blurb in cars:
        draw.text((44, y), car_name, font=FONT_BODY_BOLD, fill=GOLD_ACCENT)
        draw.text((44, y + 16), specs, font=FONT_BODY_SM, fill=TEXT_MUTED)
        draw.text((44, y + 30), blurb, font=FONT_BODY_SM, fill=TEXT_DIM)
        y += 50

    # Courses & Credits Box (Right)
    draw.rounded_rectangle([480, 114, 932, 498], radius=8, fill=BG_CARD, outline=BORDER_MUTED, width=1)
    draw.text((496, 126), "CHAMPIONSHIP SCENERY COURSES", font=FONT_SECTION_HDR, fill=CYAN_ACCENT)

    courses = [
        ("PACIFIC – YOSEMITE", "Cruise from the rugged Northern California coast through redwood groves into the majestic granite valleys of Yosemite National Park."),
        ("CAPE COD – NIAGARA", "Race across New England coastal highways, historic covered bridges, and autumn foliage toward the thundering roar of Niagara Falls."),
    ]
    y = 152
    for cname, cdesc in courses:
        draw.text((496, y), cname, font=FONT_BODY_BOLD, fill=GREEN_ACCENT)
        draw.text((496, y + 16), cdesc[:60], font=FONT_BODY_SM, fill=TEXT_MUTED)
        draw.text((496, y + 30), cdesc[60:120], font=FONT_BODY_SM, fill=TEXT_MUTED)
        if len(cdesc) > 120:
            draw.text((496, y + 44), cdesc[120:], font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 62

    draw.line([(496, 280), (916, 280)], fill=BORDER_MUTED, width=1)
    draw.text((496, 292), "CREDITS & ACKNOWLEDGMENTS", font=FONT_SECTION_HDR, fill=GOLD_ACCENT)

    credits = [
        ("kylofon", "Author of the test-drive-3-sdl3 static recompilation."),
        ("Accolade & DSI", "Tom Loughry, Russell Shiffer & the original 1990 creators."),
        ("Nuke.YKT", "Creator of the Nuked-OPL3 Yamaha YMF262 FM emulator."),
        ("VitaSDK Team", "Open-source PlayStation®Vita toolchain and libraries."),
        ("Vita3K Team", "PlayStation®Vita emulator team."),
    ]
    y = 320
    for name, role in credits:
        draw.text((496, y), name, font=FONT_BODY_BOLD, fill=TEXT_WHITE)
        draw.text((610, y), role, font=FONT_BODY_SM, fill=TEXT_MUTED)
        y += 24

    im.save(f"{OUTPUT_DIR}/005.png")
    print("Created vpk/manual/005.png")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    make_page_1()
    make_page_2()
    make_page_3()
    make_page_4()
    make_page_5()


if __name__ == "__main__":
    main()
