#!/usr/bin/env python3
"""Reject generated row art that is unsafe before frame extraction or atlas packing."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from extract_strip_frames import parse_hex_color, remove_chroma_background


def alpha_count(image: Image.Image) -> int:
    return sum(image.getchannel("A").histogram()[1:])


def checker(size: tuple[int, int], square: int = 24) -> Image.Image:
    output = Image.new("RGBA", size, (239, 241, 244, 255))
    draw = ImageDraw.Draw(output)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle(
                    (x, y, min(size[0] - 1, x + square - 1), min(size[1] - 1, y + square - 1)),
                    fill=(222, 226, 232, 255),
                )
    return output


def validate_strip_image(
    strip: Image.Image,
    frame_count: int,
    min_padding_percent: float = 10.0,
    max_occupancy_percent: float = 80.0,
) -> dict[str, object]:
    rgba = strip.convert("RGBA")
    width, height = rgba.size
    errors: list[str] = []
    frames: list[dict[str, object]] = []
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    if width < frame_count:
        errors.append(f"canvas width {width}px is smaller than the {frame_count} frame slots")

    slot_width = width / frame_count
    margin_y = math.ceil(height * min_padding_percent / 100.0)
    for index in range(frame_count):
        slot_left = round(index * slot_width)
        slot_right = round((index + 1) * slot_width)
        slot = rgba.crop((slot_left, 0, slot_right, height))
        bbox = slot.getbbox()
        frame_errors: list[str] = []
        local_width = slot_right - slot_left
        margin_x = math.ceil(local_width * min_padding_percent / 100.0)
        safe = (margin_x, margin_y, local_width - margin_x, height - margin_y)

        if bbox is None:
            frame_errors.append("slot is empty")
            bounds = None
            occupancy_width = 0.0
            occupancy_height = 0.0
            margins = None
        else:
            left, top, right, bottom = bbox
            bounds = [left + slot_left, top, right + slot_left, bottom]
            occupancy_width = (right - left) / local_width * 100.0
            occupancy_height = (bottom - top) / height * 100.0
            margins = {"left": left, "right": local_width - right, "top": top, "bottom": height - bottom}
            if left < safe[0]:
                frame_errors.append(f"left padding {left}px is below required {safe[0]}px")
            if right > safe[2]:
                frame_errors.append(f"right padding {local_width - right}px is below required {margin_x}px")
            if top < safe[1]:
                frame_errors.append(f"top padding {top}px is below required {safe[1]}px")
            if bottom > safe[3]:
                frame_errors.append(f"bottom padding {height - bottom}px is below required {margin_y}px")
            if occupancy_width > max_occupancy_percent:
                frame_errors.append(
                    f"width occupancy {occupancy_width:.2f}% exceeds {max_occupancy_percent:.2f}%"
                )
            if occupancy_height > max_occupancy_percent:
                frame_errors.append(
                    f"height occupancy {occupancy_height:.2f}% exceeds {max_occupancy_percent:.2f}%"
                )

        for message in frame_errors:
            errors.append(f"frame {index}: {message}")
        frames.append(
            {
                "index": index,
                "slot": [slot_left, 0, slot_right, height],
                "safe_boundary": [slot_left + safe[0], safe[1], slot_left + safe[2], safe[3]],
                "bbox": bounds,
                "margins": margins,
                "occupancy_percent": {"width": round(occupancy_width, 4), "height": round(occupancy_height, 4)},
                "errors": frame_errors,
            }
        )

    guard_violations: list[dict[str, object]] = []
    for boundary_index in range(1, frame_count):
        boundary = round(boundary_index * slot_width)
        guard = max(1, math.ceil(slot_width * min_padding_percent / 100.0))
        left = max(0, boundary - guard)
        right = min(width, boundary + guard)
        pixels = alpha_count(rgba.crop((left, 0, right, height)))
        if pixels:
            errors.append(
                f"boundary {boundary_index}: {pixels} non-transparent alpha values in the {left}:{right} source guard band"
            )
            guard_violations.append(
                {"boundary_index": boundary_index, "x": boundary, "guard": [left, right], "alpha": pixels}
            )

    return {
        "ok": not errors,
        "canvas": {"width": width, "height": height},
        "frame_count": frame_count,
        "policy": {
            "min_padding_percent": min_padding_percent,
            "max_occupancy_percent": max_occupancy_percent,
            "internal_guard_bands_must_be_transparent": True,
        },
        "frames": frames,
        "guard_violations": guard_violations,
        "errors": errors,
    }


def write_overlay(strip: Image.Image, report: dict[str, object], output: Path) -> None:
    canvas = checker(strip.size)
    canvas.alpha_composite(strip)
    draw = ImageDraw.Draw(canvas)
    for frame in report["frames"]:
        slot = frame["slot"]
        safe = frame["safe_boundary"]
        color = (230, 35, 35, 255) if frame["errors"] else (40, 100, 245, 255)
        draw.rectangle((slot[0], slot[1], slot[2] - 1, slot[3] - 1), outline=color, width=3)
        draw.rectangle(tuple(safe), outline=(245, 60, 60, 255), width=3)
        if frame["bbox"] is not None:
            draw.rectangle(tuple(frame["bbox"]), outline=(20, 180, 70, 255), width=3)
        draw.text((slot[0] + 8, 8), str(frame["index"]), fill=(10, 20, 35, 255))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("strip")
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--chroma-key", default="#FF00FF")
    parser.add_argument("--key-threshold", type=float, default=96.0)
    parser.add_argument("--min-padding-percent", type=float, default=10.0)
    parser.add_argument("--max-occupancy-percent", type=float, default=80.0)
    parser.add_argument("--json-out")
    parser.add_argument("--overlay-out")
    parser.add_argument("--transparent-out")
    args = parser.parse_args()

    source = Path(args.strip).expanduser().resolve()
    with Image.open(source) as opened:
        transparent = remove_chroma_background(opened, parse_hex_color(args.chroma_key), args.key_threshold)
    report = validate_strip_image(
        transparent, args.frames, args.min_padding_percent, args.max_occupancy_percent
    )
    report["source"] = str(source)
    if args.transparent_out:
        output = Path(args.transparent_out).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        transparent.save(output)
        report["transparent_output"] = str(output)
    if args.overlay_out:
        overlay = Path(args.overlay_out).expanduser().resolve()
        write_overlay(transparent, report, overlay)
        report["overlay"] = str(overlay)
    if args.json_out:
        json_output = Path(args.json_out).expanduser().resolve()
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
