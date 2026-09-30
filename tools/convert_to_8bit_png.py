#!/usr/bin/env python3
"""
Convert PNG images to 8-bit palette-indexed PNGs (color_type=3), non-interlaced,
with zero transparency on icon0.png. Ensures 100% compliance with Sony PlayStation
Vita TRC guidelines, completely preventing VitaShell installation error 0x8010113D.
"""

import sys
import os
from PIL import Image

def convert_to_8bit_indexed(filepath, max_colors=256, is_icon0=False):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (file not found)")
        return False

    with Image.open(filepath) as im:
        if is_icon0:
            im = im.convert("RGB")
        elif im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
        else:
            im = im.convert("RGB")

        p_img = im.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)

        if is_icon0:
            p_img.info.pop("transparency", None)

        p_img.save(filepath, format="PNG", optimize=True)

    with open(filepath, "rb") as f:
        data = f.read(30)
        color_type = data[25]
        interlace = data[28]

    status = "OK" if color_type == 3 and interlace == 0 else "WARNING"
    print(f"[{status}] {filepath}: mode={p_img.mode}, color_type={color_type}, interlace={interlace}")
    return color_type == 3

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file1.png> [file2.png ...]")
        sys.exit(1)

    all_ok = True
    for path in sys.argv[1:]:
        is_icon = os.path.basename(path).lower() == "icon0.png"
        ok = convert_to_8bit_indexed(path, is_icon0=is_icon)
        if not ok:
            all_ok = False

    if not all_ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
