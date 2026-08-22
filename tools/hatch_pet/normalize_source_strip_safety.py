#!/usr/bin/env python3
"""Place complete generated poses into source-safe slots without reconstructing artwork."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image

from extract_strip_frames import (
    component_bounds,
    component_frame_groups,
    connected_components,
    parse_hex_color,
    remove_chroma_background,
)
from validate_source_strip_safety import validate_strip_image, write_overlay


def major_components(image: Image.Image) -> list[dict[str, object]]:
    components = connected_components(image)
    if not components:
        return []
    largest = max(component["area"] for component in components)
    threshold = max(120, largest * 0.20)
    return [component for component in components if component["area"] >= threshold]


def render_group(
    source: Image.Image,
    group: list[dict[str, object]],
    bbox: tuple[int, int, int, int],
) -> Image.Image:
    left, top, right, bottom = bbox
    output = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
    source_pixels = source.load()
    target_pixels = output.load()
    width = source.width
    for component in group:
        for pixel_index in component["pixels"]:
            x = pixel_index % width
            y = pixel_index // width
            target_pixels[x - left, y - top] = source_pixels[x, y]
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--json-out")
    parser.add_argument("--overlay-out")
    parser.add_argument("--chroma-key", default="#FF00FF")
    parser.add_argument("--key-threshold", type=float, default=96.0)
    parser.add_argument("--slot-width", type=int, default=400)
    parser.add_argument("--height", type=int, default=500)
    parser.add_argument("--min-padding-percent", type=float, default=10.0)
    parser.add_argument("--max-occupancy-percent", type=float, default=80.0)
    parser.add_argument("--min-raw-edge-percent", type=float, default=2.0)
    parser.add_argument("--preserve-vertical-motion", action="store_true")
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    with Image.open(source_path) as opened:
        transparent = remove_chroma_background(
            opened, parse_hex_color(args.chroma_key), args.key_threshold
        )

    majors = major_components(transparent)
    if len(majors) != args.frames:
        raise SystemExit(
            f"refusing source normalization: expected exactly {args.frames} complete major pose "
            f"components, found {len(majors)}; connected or missing poses require regeneration"
        )
    groups = component_frame_groups(transparent, args.frames)
    if groups is None:
        raise SystemExit("refusing source normalization: complete pose groups could not be recovered")
    bboxes = [component_bounds(group) for group in groups]

    edge_x = max(1, math.ceil(transparent.width * args.min_raw_edge_percent / 100.0))
    edge_y = max(1, math.ceil(transparent.height * args.min_raw_edge_percent / 100.0))
    raw_errors = []
    for index, (left, top, right, bottom) in enumerate(bboxes):
        if left < edge_x or right > transparent.width - edge_x:
            raw_errors.append(f"frame {index} approaches the raw left/right canvas edge")
        if top < edge_y or bottom > transparent.height - edge_y:
            raw_errors.append(f"frame {index} approaches the raw top/bottom canvas edge")
    if raw_errors:
        raise SystemExit(
            "refusing source normalization because artwork may already be cropped:\n- "
            + "\n- ".join(raw_errors)
        )

    sprites = [render_group(transparent, group, bbox) for group, bbox in zip(groups, bboxes)]
    safe_width = math.floor(args.slot_width * args.max_occupancy_percent / 100.0)
    safe_height = math.floor(args.height * args.max_occupancy_percent / 100.0)
    scale = min(
        1.0,
        min(safe_width / sprite.width for sprite in sprites),
        min(safe_height / sprite.height for sprite in sprites),
    )
    if scale < 1.0:
        sprites = [
            sprite.resize(
                (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))),
                Image.Resampling.LANCZOS,
            )
            for sprite in sprites
        ]

    output = Image.new(
        "RGBA", (args.slot_width * args.frames, args.height), (0, 0, 0, 0)
    )
    original_centers = [(top + bottom) / 2 for _, top, _, bottom in bboxes]
    median_center = sorted(original_centers)[len(original_centers) // 2]
    safe_top = math.ceil(args.height * args.min_padding_percent / 100.0)
    safe_bottom = args.height - safe_top
    placements = []
    for index, sprite in enumerate(sprites):
        left = index * args.slot_width + (args.slot_width - sprite.width) // 2
        if args.preserve_vertical_motion:
            desired_center = args.height / 2 + (original_centers[index] - median_center) * scale
            top = round(desired_center - sprite.height / 2)
            top = max(safe_top, min(top, safe_bottom - sprite.height))
        else:
            top = safe_bottom - sprite.height
        output.alpha_composite(sprite, (left, top))
        placements.append(
            {"index": index, "left": left, "top": top, "width": sprite.width, "height": sprite.height}
        )

    report = validate_strip_image(
        output, args.frames, args.min_padding_percent, args.max_occupancy_percent
    )
    report.update(
        {
            "source": str(source_path),
            "normalization": {
                "shared_scale": scale,
                "raw_major_components": len(majors),
                "raw_edge_percent": args.min_raw_edge_percent,
                "preserve_vertical_motion": args.preserve_vertical_motion,
                "placements": placements,
            },
        }
    )
    if not report["ok"]:
        raise SystemExit(
            "normalized source did not pass the source safety gate:\n- "
            + "\n- ".join(report["errors"])
        )

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.save(output_path)
    report["output"] = str(output_path)
    if args.overlay_out:
        overlay = Path(args.overlay_out).expanduser().resolve()
        write_overlay(output, report, overlay)
        report["overlay"] = str(overlay)
    if args.json_out:
        json_path = Path(args.json_out).expanduser().resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
