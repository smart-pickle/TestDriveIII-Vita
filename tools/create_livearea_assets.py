#!/usr/bin/env python3
"""
Generate LiveArea visual assets for Test Drive III: The Passion on PS Vita.
Creates:
  vpk/icon0.png   (128x128)
  vpk/bg.png      (840x500)
  vpk/startup.png (280x158)
  vpk/template.xml
"""

import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/System/Library/Fonts/Supplemental"
try:
    FONT_TITLE_LG = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 36)
    FONT_TITLE_MD = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 22)
    FONT_TITLE_SM = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 15)
    FONT_SUB_MD = ImageFont.truetype(f"{FONT_DIR}/Arial.ttf", 14)
    FONT_SUB_SM = ImageFont.truetype(f"{FONT_DIR}/Arial.ttf", 10)
    FONT_BADGE = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 11)
except Exception:
    default = ImageFont.load_default()
    FONT_TITLE_LG = default
    FONT_TITLE_MD = default
    FONT_TITLE_SM = default
    FONT_SUB_MD = default
    FONT_SUB_SM = default
    FONT_BADGE = default

def create_icon():
    im = Image.new("RGB", (128, 128), (14, 18, 30))
    draw = ImageDraw.Draw(im)

    # Gradient background
    for y in range(128):
        ratio = y / 128.0
        r = int(12 + ratio * 24)
        g = int(16 + ratio * 20)
        b = int(30 + ratio * 45)
        draw.line([(0, y), (127, y)], fill=(r, g, b))

    # Outer border
    draw.rounded_rectangle([2, 2, 125, 125], radius=14, outline=(255, 183, 3), width=2)
    draw.rounded_rectangle([5, 5, 122, 122], radius=11, outline=(45, 60, 90), width=1)

    # Racing stripes
    draw.line([(10, 22), (117, 22)], fill=(255, 61, 87), width=2)
    draw.line([(10, 26), (117, 26)], fill=(0, 212, 255), width=1)

    # "TEST DRIVE"
    draw.text((16, 32), "TEST", font=FONT_TITLE_SM, fill=(255, 255, 255))
    draw.text((64, 32), "DRIVE", font=FONT_TITLE_SM, fill=(0, 212, 255))

    # Big "III" roman numeral
    draw.text((50, 52), "III", font=FONT_TITLE_MD, fill=(255, 215, 0))

    # "THE PASSION" badge
    draw.rounded_rectangle([14, 86, 114, 106], radius=4, fill=(200, 30, 45), outline=(255, 120, 130), width=1)
    draw.text((20, 89), "THE PASSION", font=FONT_BADGE, fill=(255, 255, 255))

    # Bottom subtext
    draw.text((22, 110), "ACCOLADE 1990", font=FONT_SUB_SM, fill=(160, 180, 210))

    os.makedirs("vpk", exist_ok=True)
    im.save("vpk/icon0.png")
    print("Created vpk/icon0.png (128x128)")

def create_startup():
    im = Image.new("RGB", (280, 158), (12, 16, 26))
    draw = ImageDraw.Draw(im)

    # Gradient background
    for y in range(158):
        ratio = y / 158.0
        r = int(10 + ratio * 28)
        g = int(14 + ratio * 24)
        b = int(26 + ratio * 52)
        draw.line([(0, y), (279, y)], fill=(r, g, b))

    # 3D polygon wireframe / horizon feel
    horizon = 95
    draw.line([(0, horizon), (279, horizon)], fill=(50, 70, 110), width=1)
    # Perspective road
    draw.polygon([(140, horizon), (20, 157), (260, 157)], fill=(20, 26, 42))
    draw.line([(140, horizon), (20, 157)], fill=(0, 212, 255), width=2)
    draw.line([(140, horizon), (260, 157)], fill=(0, 212, 255), width=2)
    draw.line([(140, horizon), (140, 157)], fill=(255, 215, 0), width=2)

    # Frame border
    draw.rectangle([0, 0, 279, 157], outline=(255, 183, 3), width=2)

    # Title
    draw.text((24, 16), "TEST DRIVE III", font=FONT_TITLE_MD, fill=(255, 255, 255))
    draw.rounded_rectangle([24, 48, 140, 70], radius=4, fill=(200, 30, 45))
    draw.text((32, 52), "THE PASSION", font=FONT_BADGE, fill=(255, 255, 255))

    draw.text((148, 52), "VGA 3D POLYGON ENGINE", font=FONT_SUB_SM, fill=(200, 225, 255))

    im.save("vpk/startup.png")
    print("Created vpk/startup.png (280x158)")

def create_bg():
    im = Image.new("RGB", (840, 500), (10, 14, 24))
    draw = ImageDraw.Draw(im)

    # Synthwave / 3D horizon gradient
    for y in range(500):
        ratio = y / 500.0
        r = int(10 + ratio * 35)
        g = int(14 + ratio * 28)
        b = int(24 + ratio * 65)
        draw.line([(0, y), (839, y)], fill=(r, g, b))

    # Perspective highway grid at bottom
    horizon = 270
    for y in range(horizon, 500, 20):
        y_scaled = horizon + int((y - horizon) ** 1.3 * 0.7)
        if y_scaled < 500:
            draw.line([(0, y_scaled), (839, y_scaled)], fill=(35, 52, 85), width=1)
    for x in range(0, 841, 60):
        draw.line([(420 + (x - 420) // 5, horizon), (x, 499)], fill=(32, 46, 75), width=1)

    # Sun / Glow at horizon
    draw.ellipse([340, horizon - 80, 500, horizon + 80], fill=(45, 65, 110))

    # LiveArea Gate Title
    draw.text((60, 48), "TEST DRIVE III: THE PASSION", font=FONT_TITLE_LG, fill=(255, 255, 255))
    draw.rounded_rectangle([60, 102, 190, 129], radius=5, fill=(200, 30, 45), outline=(255, 120, 130), width=1)
    draw.text((72, 107), "VGA 3D ENGINE", font=FONT_BADGE, fill=(255, 255, 255))

    draw.text((205, 107), "PlayStation®Vita Community Edition", font=FONT_SUB_MD, fill=(0, 212, 255))
    draw.line([(60, 142), (780, 142)], fill=(45, 60, 90), width=1)

    # Info highlights
    draw.text((60, 162), "• Free-Roaming 3D Filled-Polygon Driving World with Multiple Route Choices", font=FONT_SUB_MD, fill=(220, 230, 245))
    draw.text((60, 192), "• 5 World-Class Supercars: CERV III, NSX, Diablo, Mythos & Stealth R/T", font=FONT_SUB_MD, fill=(220, 230, 245))
    draw.text((60, 222), "• Authentic AdLib / Sound Blaster OPL2 FM Synthesis via Nuked-OPL3", font=FONT_SUB_MD, fill=(220, 230, 245))
    draw.text((60, 252), "• Native Tri-Mode Display Engine (4:3 Pillarbox, 2x Integer, 16:9 Stretch)", font=FONT_SUB_MD, fill=(220, 230, 245))
    draw.text((60, 282), "• Full Analog Steering, Shoulder Trigger Pedals & Manual Shifting", font=FONT_SUB_MD, fill=(220, 230, 245))

    im.save("vpk/bg.png")
    print("Created vpk/bg.png (840x500)")

def create_template():
    content = """<?xml version="1.0" encoding="utf-8"?>
<livearea style="a1" format-ver="01.00">
  <livearea-background>
    <image>bg.png</image>
  </livearea-background>
  <gate>
    <startup-image>startup.png</startup-image>
  </gate>
</livearea>
"""
    with open("vpk/template.xml", "w", encoding="utf-8") as f:
        f.write(content)
    print("Created vpk/template.xml")

if __name__ == "__main__":
    create_icon()
    create_startup()
    create_bg()
    create_template()
