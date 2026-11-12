#!/usr/bin/env python3
"""Render the five suits at identical magnification, feet aligned without resizing."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PETS = (("sd-gundam-codex-pet", "SD Gundam"), ("green-zaku", "Green Zaku"), ("red-zaku", "Red Zaku"), ("gouf", "Gouf"), ("gm", "GM"))


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def main():
    scale, tile = 2, 416
    canvas = Image.new("RGB", (tile * 5 + 80, 630), "#eef2f6")
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 24), "Mobile suit lineup", font=font(32), fill="#0f172a")
    draw.text((40, 72), "First idle pose | identical 2x magnification | feet aligned | no per-character resizing", font=font(21), fill="#475569")
    baseline = 540
    draw.line((40, baseline, canvas.width - 40, baseline), fill="#94a3b8", width=2)
    measurements = []
    for index, (slug, name) in enumerate(PETS):
        sheet = Image.open(ROOT / "pets" / slug / "assets/spritesheet.webp").convert("RGBA")
        cell = sheet.crop((0, 0, 192, 208))
        bounds = cell.getchannel("A").getbbox()
        image = cell.resize((384, 416), Image.Resampling.NEAREST)
        x = 40 + index * tile + 16
        y = baseline - bounds[3] * scale
        canvas.paste(image, (x, y), image)
        draw.text((40 + index * tile + tile // 2, 558), name, anchor="mt", font=font(25), fill="#0f172a")
        height = bounds[3] - bounds[1]
        draw.text((40 + index * tile + tile // 2, 596), f"Visible height: {height} px", anchor="mt", font=font(18), fill="#475569")
        measurements.append({"pet": slug, "frame": "idle[0]", "visible_height_px": height, "alpha_bounds": list(bounds)})
    target = ROOT / "showcase/mobile-suit-lineup.png"
    canvas.save(target)
    report = {"scale_factor": scale, "method": "Identical integer magnification; vertical translation aligns the alpha bounds' bottom. Source atlas pixels remain unchanged.", "scope": "One first-idle frame per pet, not a claim about every frame or canon proportions.", "measurements": measurements}
    (ROOT / "docs/validation/lineup.json").write_text(json.dumps(report, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
