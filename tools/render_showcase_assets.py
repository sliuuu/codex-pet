#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PETS = [
    ("sd-gundam-codex-pet", "SD Gundam"),
    ("chibi-asuka", "Chibi Asuka"),
]
CELL_W = 192
CELL_H = 208
SCALE = 2
GIF_PADDING = {
    ("chibi-asuka", "sad"): (0, 24, 0, 0),
}


def font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT_SM = font(14)
FONT_MD = font(20)
FONT_LG = font(32)


def checker(size: tuple[int, int], tile: int = 16) -> Image.Image:
    img = Image.new("RGBA", size, "#f8fafc")
    draw = ImageDraw.Draw(img)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill="#e5e7eb")
    return img


def crop_cell(sheet: Image.Image, frame_index: int) -> Image.Image:
    row, col = divmod(frame_index, 8)
    box = (col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H)
    return sheet.crop(box).convert("RGBA")


def scale_cell(cell: Image.Image, scale: int = SCALE) -> Image.Image:
    return cell.resize((CELL_W * scale, CELL_H * scale), Image.Resampling.NEAREST)


def pad_cell(cell: Image.Image, padding: tuple[int, int, int, int]) -> Image.Image:
    left, top, right, bottom = padding
    if not any(padding):
        return cell
    out = Image.new("RGBA", (cell.width + left + right, cell.height + top + bottom), (0, 0, 0, 0))
    out.alpha_composite(cell, (left, top))
    return out


def composite_cell(cell: Image.Image, bg: str = "#f8fafc") -> Image.Image:
    out = Image.new("RGBA", cell.size, bg)
    out.alpha_composite(cell)
    return out.convert("P", palette=Image.Palette.ADAPTIVE)


def save_gif(
    sheet: Image.Image,
    frames: list[int],
    out: Path,
    fps: int,
    padding: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> None:
    scaled_padding = tuple(value * SCALE for value in padding)
    rendered = [composite_cell(pad_cell(scale_cell(crop_cell(sheet, idx)), scaled_padding)) for idx in frames]
    duration = max(60, int(1000 / max(1, fps)))
    rendered[0].save(
        out,
        save_all=True,
        append_images=rendered[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def save_contact_sheet(sheet: Image.Image, pet_json: dict, out: Path) -> None:
    row_h = CELL_H + 42
    out_img = Image.new("RGBA", (CELL_W * 8, row_h * 11 + 44), "#ffffff")
    draw = ImageDraw.Draw(out_img)
    title = f"{pet_json['displayName']} - v{pet_json.get('spriteVersionNumber', 2)} 8x11 sprite atlas"
    draw.text((12, 10), title, fill="#111827", font=FONT_MD)
    rows = [
        "idle",
        "running-right",
        "running-left",
        "waving",
        "jumping",
        "failed / sad",
        "waiting",
        "running / active work",
        "review / scanning",
        "look: 000-157.5",
        "look: 180-337.5",
    ]
    y0 = 44
    for row, label in enumerate(rows):
        y = y0 + row * row_h
        draw.rectangle((0, y, out_img.width, y + 24), fill="#111827")
        draw.text((8, y + 4), f"row {row}: {label}", fill="#ffffff", font=FONT_SM)
        for col in range(8):
            x = col * CELL_W
            bg = checker((CELL_W, CELL_H), 16)
            bg.alpha_composite(sheet.crop((x, row * CELL_H, x + CELL_W, (row + 1) * CELL_H)).convert("RGBA"))
            out_img.alpha_composite(bg, (x, y + 26))
            draw.rectangle((x, y + 26, x + CELL_W - 1, y + 26 + CELL_H - 1), outline="#d1d5db")
            draw.text((x + 4, y + 29), str(col), fill="#111827", font=FONT_SM)
    out_img.save(out)


def save_look_gif(sheet: Image.Image, out: Path) -> None:
    frames = list(range(72, 88))
    save_gif(sheet, frames, out, 8)


def save_screenshot(sheet: Image.Image, pet_name: str, out: Path) -> None:
    canvas = Image.new("RGBA", (1200, 760), "#0f172a")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((48, 48, 1152, 712), radius=18, fill="#111827", outline="#334155", width=2)
    draw.rectangle((48, 48, 1152, 112), fill="#1f2937")
    draw.text((80, 68), "Codex pet showcase", fill="#f8fafc", font=FONT_LG)
    draw.text((80, 122), pet_name, fill="#fde68a", font=FONT_LG)
    draw.text((80, 170), "Validated v2 pet with standard animations and 16 look directions", fill="#cbd5e1", font=FONT_MD)
    states = [
        ("Idle", 0),
        ("Wave", 24),
        ("Run", 8),
        ("Review", 64),
        ("Look right", 76),
        ("Look left", 84),
    ]
    card_h = 252
    for i, (label, frame) in enumerate(states):
        x = 82 + (i % 3) * 352
        y = 236 + (i // 3) * 262
        draw.rounded_rectangle((x, y, x + 300, y + card_h), radius=14, fill="#f8fafc")
        draw.text((x + 16, y + 14), label, fill="#111827", font=FONT_MD)
        cell = scale_cell(crop_cell(sheet, frame), 1)
        canvas.alpha_composite(cell, (x + 54, y + 36))
    canvas.convert("RGB").save(out)


def main() -> None:
    for pet_id, pet_name in PETS:
        pet_dir = ROOT / "pets" / pet_id
        showcase_dir = ROOT / "showcase" / pet_id
        animations_dir = showcase_dir / "animations"
        animations_dir.mkdir(parents=True, exist_ok=True)

        pet_json = json.loads((pet_dir / "pet.json").read_text())
        sheet_path = pet_dir / pet_json.get("spritesheetPath", "assets/spritesheet.webp")
        sheet = Image.open(sheet_path).convert("RGBA")

        save_contact_sheet(sheet, pet_json, showcase_dir / "contact-sheet.png")
        save_screenshot(sheet, pet_name, showcase_dir / "in-action.png")

        for state, cfg in pet_json["animations"].items():
            padding = GIF_PADDING.get((pet_id, state), (0, 0, 0, 0))
            save_gif(sheet, cfg["frames"], animations_dir / f"{state}.gif", cfg.get("fps", 8), padding)
        save_look_gif(sheet, animations_dir / "look-directions.gif")


if __name__ == "__main__":
    main()
