#!/usr/bin/env python3
"""
Generate official retail-style Sony PlayStation Vita LiveArea visual assets
for Test Drive III: The Passion (1990).

Produces:
  vpk/bg.png       (840x500) - Full-bleed authentic 1990 Accolade cover art (clean, no text clutter)
  vpk/startup.png  (280x158) - Polished start gate with official Test Drive III brush logo
  vpk/icon0.png    (128x128) - Home Screen bubble icon with official logo & badge
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
BOXART_PATH = os.path.join(SCRIPT_DIR, "boxart_front.jpg")
OUTPUT_DIR = os.path.join(ROOT_DIR, "vpk")

FONT_DIR = "/System/Library/Fonts/Supplemental"
try:
    FONT_TITLE = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 20)
    FONT_BADGE = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 9)
    FONT_SUB = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 8)
    FONT_SUB_GATE = ImageFont.truetype(f"{FONT_DIR}/Arial Bold.ttf", 11)
except Exception:
    default = ImageFont.load_default()
    FONT_TITLE = default
    FONT_BADGE = default
    FONT_SUB = default
    FONT_SUB_GATE = default

def load_and_prep_boxart():
    if not os.path.exists(BOXART_PATH):
        raise FileNotFoundError(f"Box art source not found at {BOXART_PATH}")

    box = Image.open(BOXART_PATH).convert("RGB")

    # Inpaint / clean the retail stickers on the bottom left:
    # 1. Blue system requirements sticker: x: [0, 220], y: [1185, 1370]
    # Sample clean door area from x: [230, 450], y: [1185, 1370]
    door = box.crop((230, 1185, 450, 1370)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    box.paste(door, (0, 1185))

    # 2. Round version sticker on jacket sleeve: x: [35, 125], y: [1085, 1175]
    jacket = box.crop((140, 1085, 230, 1175)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    box.paste(jacket, (35, 1085))

    # Soften seams
    seam_door = box.crop((200, 1185, 240, 1370)).filter(ImageFilter.GaussianBlur(radius=2))
    box.paste(seam_door, (200, 1185))
    seam_arm = box.crop((25, 1080, 135, 1180)).filter(ImageFilter.GaussianBlur(radius=1.5))
    box.paste(seam_arm, (25, 1080))

    return box

def extract_brush_logo(box):
    # Test Drive III brush script is approximately y: [420, 560], x: [140, 950]
    logo_crop = box.crop((140, 420, 950, 560))
    logo_rgba = logo_crop.convert("RGBA")
    data = logo_rgba.getdata()
    clean_data = []
    for item in data:
        # Cream background threshold
        if item[0] > 195 and item[1] > 175 and item[2] > 145:
            clean_data.append((255, 255, 255, 0))
        else:
            clean_data.append((item[0], item[1], item[2], 255))
    logo_rgba.putdata(clean_data)
    return logo_rgba

def create_bg(box):
    crop_w = 1089
    crop_h = int(crop_w / 1.68) # 648 px height to match 840x500 ratio (1.68)
    crop_y2 = 1380
    crop_y1 = crop_y2 - crop_h

    bg_crop = box.crop((0, crop_y1, crop_w, crop_y2))
    bg_resized = bg_crop.resize((840, 500), Image.Resampling.LANCZOS)

    # Subtle top vignette for the PS Vita system status bar and Manual icon
    vignette = Image.new("RGBA", (840, 500), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for y in range(90):
        alpha = int(110 * ((90 - y) / 90.0) ** 1.5)
        v_draw.line([(0, y), (839, y)], fill=(12, 14, 22, alpha))

    bg_final = Image.alpha_composite(bg_resized.convert("RGBA"), vignette).convert("RGB")
    out_path = os.path.join(OUTPUT_DIR, "bg.png")
    bg_final.save(out_path)
    print(f"Created {out_path} (840x500)")

def create_startup(brush_logo):
    im = Image.new("RGB", (280, 158), (14, 18, 28))
    draw = ImageDraw.Draw(im)

    # Subtle dark carbon gradient
    for y in range(158):
        ratio = y / 158.0
        r = int(12 + ratio * 16)
        g = int(15 + ratio * 12)
        b = int(24 + ratio * 20)
        draw.line([(0, y), (279, y)], fill=(r, g, b))

    # Outer gold & slate border
    draw.rectangle([0, 0, 279, 157], outline=(255, 183, 3), width=2)
    draw.rectangle([3, 3, 276, 154], outline=(40, 50, 70), width=1)

    # Scale brush logo into upper half
    target_w = 230
    target_h = int(brush_logo.height * (target_w / brush_logo.width))
    scaled_logo = brush_logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
    im.paste(scaled_logo, ((280 - target_w) // 2, 16), scaled_logo)

    # Crisp golden subtitle (leaves the bottom y: 95..145 clear for blue Start button)
    draw.text((80, 16 + target_h + 3), "T H E   P A S S I O N", font=FONT_SUB_GATE, fill=(255, 205, 110))

    out_path = os.path.join(OUTPUT_DIR, "startup.png")
    im.save(out_path)
    print(f"Created {out_path} (280x158)")

def create_icon(brush_logo):
    im = Image.new("RGB", (128, 128), (14, 18, 28))
    draw = ImageDraw.Draw(im)

    # Radial / subtle gradient
    for y in range(128):
        ratio = y / 128.0
        r = int(14 + ratio * 28)
        g = int(16 + ratio * 14)
        b = int(28 + ratio * 14)
        draw.line([(0, y), (127, y)], fill=(r, g, b))

    # Rounded gold border
    draw.rounded_rectangle([2, 2, 125, 125], radius=14, outline=(255, 183, 3), width=2)
    draw.rounded_rectangle([5, 5, 122, 122], radius=11, outline=(50, 60, 80), width=1)

    # Racing stripes
    draw.line([(12, 18), (115, 18)], fill=(220, 40, 60), width=2)
    draw.line([(12, 22), (115, 22)], fill=(255, 183, 3), width=1)

    # Scaled brush logo
    target_w = 110
    target_h = int(brush_logo.height * (target_w / brush_logo.width))
    scaled_logo = brush_logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
    im.paste(scaled_logo, ((128 - target_w) // 2, 36), scaled_logo)

    # Badge & subtext
    draw.rounded_rectangle([18, 76, 110, 94], radius=3, fill=(190, 25, 45), outline=(255, 120, 140), width=1)
    draw.text((23, 80), "THE PASSION", font=FONT_BADGE, fill=(255, 255, 255))
    draw.text((24, 104), "ACCOLADE 1990", font=FONT_SUB, fill=(170, 185, 210))

    out_path = os.path.join(OUTPUT_DIR, "icon0.png")
    im.save(out_path)
    print(f"Created {out_path} (128x128)")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    box = load_and_prep_boxart()
    brush = extract_brush_logo(box)

    create_bg(box)
    create_startup(brush)
    create_icon(brush)

    # Convert to 8-bit palette-indexed for strict Sony TRC compliance
    converter = os.path.join(SCRIPT_DIR, "convert_to_8bit_png.py")
    if os.path.exists(converter):
        import subprocess
        subprocess.check_call([
            sys.executable, converter,
            os.path.join(OUTPUT_DIR, "icon0.png"),
            os.path.join(OUTPUT_DIR, "startup.png"),
            os.path.join(OUTPUT_DIR, "bg.png")
        ])

if __name__ == "__main__":
    main()
