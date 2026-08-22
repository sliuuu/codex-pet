#!/usr/bin/env python3
from __future__ import annotations

from collections import deque
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PETS = [
    ("sd-gundam-codex-pet", "SD Gundam"),
    ("chibi-asuka", "Chibi Asuka"),
    ("chibi-miku", "Chibi Miku"),
]
CELL_W = 192
CELL_H = 208
SCALE = 2
GIF_PADDING = {
    ("chibi-asuka", "sad"): (0, 24, 0, 0),
}
ROW_FRAME_COUNTS = {
    0: ("idle", 6),
    1: ("running-right", 8),
    2: ("running-left", 8),
    3: ("waving", 4),
    4: ("jumping", 5),
    5: ("failed", 8),
    6: ("waiting", 6),
    7: ("running", 6),
    8: ("review", 6),
    9: ("look-000-to-157.5", 8),
    10: ("look-180-to-337.5", 8),
}
CELL_SAFETY_PETS = {"chibi-miku"}
MIN_CELL_MARGIN = 10
MIN_PADDING_PERCENT = 10.0
MAX_OCCUPANCY_PERCENT = 80.0
MAX_ANCHOR_X_DRIFT = 2.0
MAX_ANCHOR_Y_DRIFT = 2.0
VERTICAL_MOTION_ROWS = {4}


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


def connected_components(cell: Image.Image, threshold: int) -> list[dict[str, object]]:
    alpha = cell.getchannel("A")
    pixels = alpha.load()
    seen: set[tuple[int, int]] = set()
    components: list[dict[str, object]] = []
    for y in range(CELL_H):
        for x in range(CELL_W):
            if pixels[x, y] < threshold or (x, y) in seen:
                continue
            queue: deque[tuple[int, int]] = deque([(x, y)])
            seen.add((x, y))
            area = 0
            min_x = max_x = x
            min_y = max_y = y
            while queue:
                px, py = queue.popleft()
                area += 1
                min_x = min(min_x, px)
                max_x = max(max_x, px)
                min_y = min(min_y, py)
                max_y = max(max_y, py)
                for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)):
                    if (
                        0 <= nx < CELL_W
                        and 0 <= ny < CELL_H
                        and pixels[nx, ny] >= threshold
                        and (nx, ny) not in seen
                    ):
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            components.append(
                {
                    "area": area,
                    "bbox": [min_x, min_y, max_x + 1, max_y + 1],
                    "width": max_x - min_x + 1,
                    "height": max_y - min_y + 1,
                }
            )
    return sorted(components, key=lambda item: item["area"], reverse=True)


def lower_anchor_x(cell: Image.Image, bbox: tuple[int, int, int, int]) -> float:
    alpha = cell.getchannel("A")
    left, top, right, bottom = bbox
    lower_top = top + round((bottom - top) * 0.72)
    weighted_x = 0.0
    weight = 0
    for y in range(lower_top, bottom):
        for x in range(left, right):
            value = alpha.getpixel((x, y))
            if value:
                weighted_x += x * value
                weight += value
    return weighted_x / weight if weight else (left + right) / 2.0


def summarize_rows(cells: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for row, (state, frame_count) in ROW_FRAME_COUNTS.items():
        row_cells = [
            cell for cell in cells
            if cell["row"] == row
            and int(cell["column"]) < frame_count
            and isinstance(cell["bbox"], list)
        ]
        if not row_cells:
            continue
        centers_x = []
        centers_y = []
        bottoms = []
        widths = []
        heights = []
        margins = []
        for cell in row_cells:
            left, top, right, bottom = cell["bbox"]
            centers_x.append(float(cell["anchor_x"]))
            centers_y.append((top + bottom) / 2)
            bottoms.append(bottom)
            widths.append(right - left)
            heights.append(bottom - top)
            cell_margins = cell["margins"]
            if isinstance(cell_margins, dict):
                margins.extend(int(value) for value in cell_margins.values())
        summaries.append(
            {
                "row": row,
                "state": state,
                "frame_count": len(row_cells),
                "minimum_margin": min(margins),
                "center_x_range": round(max(centers_x) - min(centers_x), 2),
                "center_y_range": round(max(centers_y) - min(centers_y), 2),
                "bottom_range": max(bottoms) - min(bottoms),
                "width_range": max(widths) - min(widths),
                "height_range": max(heights) - min(heights),
            }
        )
    return summaries


def save_cell_safety(sheet: Image.Image, out_json: Path, out_overlay: Path, min_margin: int = MIN_CELL_MARGIN) -> dict[str, object]:
    rows = sheet.height // CELL_H
    safety_margin_x = max(min_margin, math.ceil(CELL_W * MIN_PADDING_PERCENT / 100.0))
    safety_margin_y = max(min_margin, math.ceil(CELL_H * MIN_PADDING_PERCENT / 100.0))
    cells: list[dict[str, object]] = []
    errors: list[str] = []
    overlay = Image.new("RGBA", (CELL_W * 8 * 2, rows * (CELL_H + 26) * 2), "#ffffff")
    draw = ImageDraw.Draw(overlay)

    for row in range(rows):
        state, frame_count = ROW_FRAME_COUNTS[row]
        y0 = row * (CELL_H + 26) * 2
        draw.rectangle((0, y0, overlay.width, y0 + 52), fill="#111827")
        draw.text((8, y0 + 8), f"row {row}: {state}", fill="#ffffff", font=FONT_SM)
        for col in range(8):
            x = col * CELL_W
            cell = sheet.crop((x, row * CELL_H, x + CELL_W, (row + 1) * CELL_H)).convert("RGBA")
            used = col < frame_count or (row == 0 and col == 6)
            bbox = cell.getchannel("A").getbbox()
            cell_errors: list[str] = []
            margins = None
            if used and bbox is None:
                cell_errors.append("used cell is empty")
            if not used and bbox is not None:
                cell_errors.append("unused cell contains visible pixels")
            if used and bbox is not None:
                left, top, right, bottom = bbox
                margins = {
                    "left": left,
                    "top": top,
                    "right": CELL_W - right,
                    "bottom": CELL_H - bottom,
                }
                required = {
                    "left": safety_margin_x,
                    "right": safety_margin_x,
                    "top": safety_margin_y,
                    "bottom": safety_margin_y,
                }
                low = {side: value for side, value in margins.items() if value < required[side]}
                if low:
                    cell_errors.append(
                        "visible pixels violate safety margin: "
                        + ", ".join(f"{side}={value}" for side, value in low.items())
                    )
                width_percent = (right - left) / CELL_W * 100.0
                height_percent = (bottom - top) / CELL_H * 100.0
                if width_percent > MAX_OCCUPANCY_PERCENT + 1e-9:
                    cell_errors.append(
                        f"visible width occupies {width_percent:.2f}% of cell; "
                        f"maximum is {MAX_OCCUPANCY_PERCENT:.2f}%"
                    )
                if height_percent > MAX_OCCUPANCY_PERCENT + 1e-9:
                    cell_errors.append(
                        f"visible height occupies {height_percent:.2f}% of cell; "
                        f"maximum is {MAX_OCCUPANCY_PERCENT:.2f}%"
                    )
                fragments = [
                    component
                    for component in connected_components(cell, 192)[1:]
                    if int(component["area"]) >= 40
                ]
                if fragments:
                    cell_errors.append(f"high-opacity detached fragment(s) detected: {fragments[:6]}")

            bg = checker((CELL_W, CELL_H), 16)
            bg.alpha_composite(cell)
            local_draw = ImageDraw.Draw(bg)
            local_draw.rectangle((0, 0, CELL_W - 1, CELL_H - 1), outline="#2563eb")
            local_draw.rectangle(
                (
                    safety_margin_x - 1,
                    safety_margin_y - 1,
                    CELL_W - safety_margin_x,
                    CELL_H - safety_margin_y,
                ),
                outline="#ef4444",
            )
            if bbox:
                local_draw.rectangle(bbox, outline="#16a34a")
            overlay.alpha_composite(bg.resize((CELL_W * 2, CELL_H * 2), Image.Resampling.NEAREST), (col * CELL_W * 2, y0 + 52))

            cell_info = {
                "state": state,
                "row": row,
                "column": col,
                "used": used,
                "bbox": list(bbox) if bbox else None,
                "margins": margins,
                "occupancy_percent": {
                    "width": round((bbox[2] - bbox[0]) / CELL_W * 100.0, 2),
                    "height": round((bbox[3] - bbox[1]) / CELL_H * 100.0, 2),
                } if bbox else None,
                "anchor_x": round(lower_anchor_x(cell, bbox), 2) if bbox else None,
                "anchor_bottom": bbox[3] if bbox else None,
                "errors": cell_errors,
            }
            cells.append(cell_info)
            for message in cell_errors:
                errors.append(f"{state} row {row} column {col}: {message}")

    row_summaries = summarize_rows(cells)
    for summary in row_summaries:
        row_errors = []
        if float(summary["center_x_range"]) > MAX_ANCHOR_X_DRIFT:
            row_errors.append(
                f"horizontal anchor drift is {summary['center_x_range']}px; maximum is {MAX_ANCHOR_X_DRIFT}px"
            )
        if int(summary["row"]) not in VERTICAL_MOTION_ROWS and float(summary["bottom_range"]) > MAX_ANCHOR_Y_DRIFT:
            row_errors.append(
                f"vertical anchor drift is {summary['bottom_range']}px; maximum is {MAX_ANCHOR_Y_DRIFT}px"
            )
        summary["vertical_motion_exempt"] = int(summary["row"]) in VERTICAL_MOTION_ROWS
        summary["errors"] = row_errors
        errors.extend(f"{summary['state']} row {summary['row']}: {message}" for message in row_errors)

    report = {
        "ok": not errors,
        "rows": rows,
        "columns": 8,
        "cell_width": CELL_W,
        "cell_height": CELL_H,
        "min_margin": min_margin,
        "min_padding_percent": MIN_PADDING_PERCENT,
        "max_occupancy_percent": MAX_OCCUPANCY_PERCENT,
        "safety_margin_x": safety_margin_x,
        "safety_margin_y": safety_margin_y,
        "max_anchor_x_drift": MAX_ANCHOR_X_DRIFT,
        "max_anchor_y_drift": MAX_ANCHOR_Y_DRIFT,
        "errors": errors,
        "warnings": [],
        "row_summaries": row_summaries,
        "cells": cells,
    }
    out_json.write_text(json.dumps(report, indent=2) + "\n")
    overlay.convert("RGB").save(out_overlay)
    return report


def save_look_gif(sheet: Image.Image, out: Path) -> None:
    frames = list(range(72, 88))
    save_gif(sheet, frames, out, 8)


def save_combined_preview(sheet: Image.Image, pet_json: dict, out: Path) -> None:
    animations = list(pet_json["animations"].items())[:9]
    tile_w = CELL_W
    tile_h = CELL_H + 28
    frames: list[Image.Image] = []
    for tick in range(24):
        canvas = Image.new("RGBA", (tile_w * 3, tile_h * 3), "#0f172a")
        draw = ImageDraw.Draw(canvas)
        for index, (state, config) in enumerate(animations):
            row, column = divmod(index, 3)
            x = column * tile_w
            y = row * tile_h
            draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), fill="#111827")
            draw.text((x + 8, y + 6), state, fill="#f8fafc", font=FONT_SM)
            animation_frames = config["frames"]
            frame_index = animation_frames[tick % len(animation_frames)]
            background = checker((CELL_W, CELL_H), 16)
            background.alpha_composite(crop_cell(sheet, frame_index))
            canvas.alpha_composite(background, (x, y + 28))
        frames.append(canvas.convert("P", palette=Image.Palette.ADAPTIVE))
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
        disposal=2,
        optimize=False,
    )


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

        if pet_id in CELL_SAFETY_PETS:
            safety_report = save_cell_safety(
                sheet,
                showcase_dir / "cell-safety.json",
                showcase_dir / "cell-safety-overlay.png",
            )
            if not safety_report["ok"]:
                errors = "\n".join(str(error) for error in safety_report["errors"])
                raise SystemExit(f"{pet_name} failed cell-safety validation before GIF export:\n{errors}")

        save_contact_sheet(sheet, pet_json, showcase_dir / "contact-sheet.png")
        save_screenshot(sheet, pet_name, showcase_dir / "in-action.png")

        for state, cfg in pet_json["animations"].items():
            padding = GIF_PADDING.get((pet_id, state), (0, 0, 0, 0))
            save_gif(sheet, cfg["frames"], animations_dir / f"{state}.gif", cfg.get("fps", 8), padding)
        save_look_gif(sheet, animations_dir / "look-directions.gif")
        combined_preview = animations_dir / "combined-preview.gif"
        if combined_preview.exists() or pet_id == "chibi-miku":
            save_combined_preview(sheet, pet_json, combined_preview)


if __name__ == "__main__":
    main()
