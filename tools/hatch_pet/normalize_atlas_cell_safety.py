#!/usr/bin/env python3
"""Normalize a Codex pet atlas with one shared scale and stable row anchors."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image

COLUMNS = 8
CELL_WIDTH = 192
CELL_HEIGHT = 208
ROW_FRAME_COUNTS = [6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]
NEUTRAL_CELL = (0, 6)
VERTICAL_MOTION_ROWS = {4}


def used_cell(row: int, column: int, row_count: int) -> bool:
    return column < ROW_FRAME_COUNTS[row] or (row_count == 11 and (row, column) == NEUTRAL_CELL)


def cell_bbox(cell: Image.Image) -> tuple[int, int, int, int] | None:
    return cell.getchannel("A").getbbox()


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


def clear_transparent_rgb(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    data = bytearray(rgba.tobytes())
    for index in range(0, len(data), 4):
        if data[index + 3] == 0:
            data[index] = data[index + 1] = data[index + 2] = 0
    return Image.frombytes("RGBA", rgba.size, bytes(data))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas")
    parser.add_argument("--output", required=True)
    parser.add_argument("--webp-output")
    parser.add_argument("--json-out")
    parser.add_argument("--min-padding-percent", type=float, default=10.0)
    parser.add_argument("--max-occupancy-percent", type=float, default=80.0)
    args = parser.parse_args()

    atlas_path = Path(args.atlas).expanduser().resolve()
    with Image.open(atlas_path) as opened:
        atlas = opened.convert("RGBA")
    if atlas.width != COLUMNS * CELL_WIDTH or atlas.height not in {9 * CELL_HEIGHT, 11 * CELL_HEIGHT}:
        raise SystemExit(f"expected 1536x1872 or 1536x2288 atlas, got {atlas.width}x{atlas.height}")

    row_count = atlas.height // CELL_HEIGHT
    padding_x = math.ceil(CELL_WIDTH * args.min_padding_percent / 100.0)
    padding_y = math.ceil(CELL_HEIGHT * args.min_padding_percent / 100.0)
    max_width = min(
        math.floor(CELL_WIDTH * args.max_occupancy_percent / 100.0),
        CELL_WIDTH - 2 * padding_x,
    )
    max_height = min(
        math.floor(CELL_HEIGHT * args.max_occupancy_percent / 100.0),
        CELL_HEIGHT - 2 * padding_y,
    )

    cells: dict[tuple[int, int], tuple[Image.Image, tuple[int, int, int, int]]] = {}
    for row in range(row_count):
        for column in range(COLUMNS):
            if not used_cell(row, column, row_count):
                continue
            box = (
                column * CELL_WIDTH,
                row * CELL_HEIGHT,
                (column + 1) * CELL_WIDTH,
                (row + 1) * CELL_HEIGHT,
            )
            cell = atlas.crop(box)
            bbox = cell_bbox(cell)
            if bbox is None:
                raise SystemExit(f"used cell row {row} column {column} is empty")
            cells[(row, column)] = (cell, bbox)

    target_anchor_x = CELL_WIDTH / 2.0
    target_ground_bottom = CELL_HEIGHT - padding_y
    widest = max(bbox[2] - bbox[0] for _, bbox in cells.values())
    tallest = max(bbox[3] - bbox[1] for _, bbox in cells.values())
    shared_scale = min(1.0, max_width / widest, max_height / tallest)

    # Bounding-box width alone is insufficient when the lower-body anchor is
    # off-center, as in a running pose with trailing hair. Constrain the one
    # shared scale by both sides of the actual anchor before any placement.
    for cell, bbox in cells.values():
        left, _, right, _ = bbox
        anchor = lower_anchor_x(cell, bbox) - left
        left_extent = anchor
        right_extent = (right - left) - anchor
        if left_extent > 0:
            shared_scale = min(shared_scale, (target_anchor_x - padding_x) / left_extent)
        if right_extent > 0:
            shared_scale = min(
                shared_scale,
                (CELL_WIDTH - padding_x - target_anchor_x) / right_extent,
            )

    for row in range(row_count):
        row_items = [
            (column, *cells[(row, column)])
            for column in range(COLUMNS)
            if (row, column) in cells
        ]
        row_ground = max(bbox[3] for _, _, bbox in row_items)
        if row in VERTICAL_MOTION_ROWS:
            tallest_travel = max(row_ground - bbox[1] for _, _, bbox in row_items)
            shared_scale = min(
                shared_scale,
                (target_ground_bottom - padding_y) / tallest_travel,
            )
    output = Image.new("RGBA", atlas.size, (0, 0, 0, 0))
    manifest_cells: list[dict[str, object]] = []

    for row in range(row_count):
        row_items = [(column, *cells[(row, column)]) for column in range(COLUMNS) if (row, column) in cells]
        row_ground = max(bbox[3] for _, _, bbox in row_items)
        for column, cell, bbox in row_items:
            left, top, right, bottom = bbox
            sprite = cell.crop(bbox)
            size = (
                max(1, round(sprite.width * shared_scale)),
                max(1, round(sprite.height * shared_scale)),
            )
            if sprite.size != size:
                sprite = sprite.resize(size, Image.Resampling.LANCZOS)

            source_anchor_x = lower_anchor_x(cell, bbox) - left
            target_left = round(target_anchor_x - source_anchor_x * shared_scale)
            if row in VERTICAL_MOTION_ROWS:
                target_bottom = target_ground_bottom - round((row_ground - bottom) * shared_scale)
            else:
                target_bottom = target_ground_bottom
            target_top = target_bottom - sprite.height
            if target_left < padding_x or target_left + sprite.width > CELL_WIDTH - padding_x:
                raise SystemExit(f"normalized row {row} column {column} exceeds horizontal safety area")
            if target_top < padding_y or target_bottom > CELL_HEIGHT - padding_y:
                raise SystemExit(f"normalized row {row} column {column} exceeds vertical safety area")

            normalized = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
            normalized.alpha_composite(sprite, (target_left, target_top))
            output.alpha_composite(normalized, (column * CELL_WIDTH, row * CELL_HEIGHT))
            manifest_cells.append(
                {
                    "row": row,
                    "column": column,
                    "source_bbox": list(bbox),
                    "output_bbox": list(cell_bbox(normalized) or ()),
                    "scale": shared_scale,
                    "anchor_x": target_anchor_x,
                    "anchor_bottom": target_bottom,
                    "vertical_motion_preserved": row in VERTICAL_MOTION_ROWS,
                }
            )

    output = clear_transparent_rgb(output)
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.save(output_path)
    if args.webp_output:
        webp_path = Path(args.webp_output).expanduser().resolve()
        webp_path.parent.mkdir(parents=True, exist_ok=True)
        output.save(webp_path, format="WEBP", lossless=True, quality=100, method=6, exact=True)
    if args.json_out:
        json_path = Path(args.json_out).expanduser().resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {
                    "ok": True,
                    "source": str(atlas_path),
                    "shared_scale": shared_scale,
                    "min_padding_percent": args.min_padding_percent,
                    "max_occupancy_percent": args.max_occupancy_percent,
                    "padding_x": padding_x,
                    "padding_y": padding_y,
                    "max_sprite_width": max_width,
                    "max_sprite_height": max_height,
                    "anchor_x": target_anchor_x,
                    "ground_bottom": target_ground_bottom,
                    "vertical_motion_rows": sorted(VERTICAL_MOTION_ROWS),
                    "cells": manifest_cells,
                },
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({"ok": True, "shared_scale": shared_scale, "output": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
