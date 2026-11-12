#!/usr/bin/env python3
"""Read-only packaging and atlas-layout checks, not an artistic quality verdict."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
COUNTS = (6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8)
STATES = ("idle", "running-right", "running-left", "waving", "jumping", "sad", "waiting", "running", "bouncing")
CELL = (192, 208)
SIZE = (1536, 2288)


def inspect_sheet(image: Image.Image) -> dict:
    report = {"ok": False, "dimensions": list(image.size), "errors": [], "warnings": [], "rows": []}
    errors = report["errors"]
    if image.size != SIZE:
        errors.append(f"Expected {SIZE}, got {image.size}")
        return report
    if "A" not in image.getbands() and "transparency" not in image.info:
        errors.append("Image has no transparency channel")
    image = image.convert("RGBA")
    for row, count in enumerate(COUNTS):
        frames = []
        for col in range(8):
            alpha = image.crop((col * 192, row * 208, (col + 1) * 192, (row + 1) * 208)).getchannel("A")
            bbox = alpha.getbbox()
            if col >= count:
                if bbox:
                    errors.append(f"Artwork in unused cell {row},{col}")
                continue
            if not bbox:
                errors.append(f"Missing artwork in cell {row},{col}")
                continue
            margins = (bbox[0], bbox[1], 192 - bbox[2], 208 - bbox[3])
            if min(margins) <= 0:
                errors.append(f"Artwork touches a cell boundary at {row},{col}")
            frames.append({"column": col, "bounds": list(bbox), "margins_px": list(margins), "height_px": bbox[3] - bbox[1]})
        report["rows"].append({"row": row, "expected_frames": count, "frames": frames})
    all_frames = [frame for row in report["rows"] for frame in row["frames"]]
    if all_frames:
        report["minimum_margin_px"] = min(min(frame["margins_px"]) for frame in all_frames)
        report["strict_ten_percent_padding"] = all(frame["margins_px"][0] >= 20 and frame["margins_px"][2] >= 20 and frame["margins_px"][1] >= 21 and frame["margins_px"][3] >= 21 for frame in all_frames)
        if not report["strict_ten_percent_padding"]:
            report["warnings"].append("Does not meet the optional strict 10% per-side padding target; source artwork is preserved.")
    idle = report["rows"][0]["frames"]
    jump = report["rows"][4]["frames"]
    if idle and jump:
        baseline = max(frame["bounds"][3] for frame in idle)
        report["jump_lift_from_idle_px"] = baseline - min(frame["bounds"][3] for frame in jump)
        if report["jump_lift_from_idle_px"] <= 0:
            report["warnings"].append("No measurable upward jump displacement relative to the idle alpha bounds.")
    report["ok"] = not errors
    return report


def inspect_pet(pet_dir: Path) -> dict:
    result = {"pet": pet_dir.name, "ok": False, "errors": []}
    try:
        pet = json.loads((pet_dir / "pet.json").read_text())
        avatar = json.loads((pet_dir / "avatar.json").read_text())
        for key in ("id", "displayName", "spriteVersionNumber", "spritesheetPath", "frameWidth", "frameHeight", "columns", "rows"):
            if pet.get(key) != avatar.get(key):
                result["errors"].append(f"Manifest mismatch: {key}")
        for key, expected in (("id", pet_dir.name), ("spriteVersionNumber", 2), ("frameWidth", 192), ("frameHeight", 208), ("columns", 8), ("rows", 11)):
            if pet.get(key) != expected:
                result["errors"].append(f"Unexpected {key}: {pet.get(key)!r}")
        path = (pet_dir / pet["spritesheetPath"]).resolve()
        if not path.is_relative_to(pet_dir.resolve()):
            raise ValueError("Sprite sheet path escapes pet directory")
        for row, state in enumerate(STATES):
            expected = list(range(row * 8, row * 8 + COUNTS[row]))
            config = pet.get("animations", {}).get(state, {})
            if config.get("frames") != expected:
                result["errors"].append(f"Incorrect frame indices for {state}")
            if not isinstance(config.get("fps"), (int, float)) or not 0 < config["fps"] <= 60:
                result["errors"].append(f"Invalid fps for {state}")
        with Image.open(path) as image:
            result["layout"] = inspect_sheet(image)
        result["file_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        result["ok"] = not result["errors"] and result["layout"]["ok"]
    except (OSError, ValueError, KeyError) as exc:
        result["errors"].append(str(exc))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pets-dir", type=Path, default=ROOT / "pets")
    parser.add_argument("--pets", nargs="+", help="Validate only these pet folder names.")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    paths = sorted(args.pets_dir.iterdir()) if not args.pets else [args.pets_dir / name for name in args.pets]
    results = [inspect_pet(path) for path in paths if path.is_dir() or args.pets]
    report = {"scope": "Manifest consistency, exact v2 dimensions, required and unused cells, transparency, cell edges, measured margins and jump displacement. This does not prove animation semantics, gaze directions, art consistency, or rights clearance.", "ok": bool(results) and all(pet["ok"] for pet in results), "pets": results}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n")
    for pet in results:
        print(f"{pet['pet']}: {'PASS' if pet['ok'] else 'FAIL'}")
        for error in pet["errors"] + pet.get("layout", {}).get("errors", []):
            print(f"  ERROR: {error}")
        for warning in pet.get("layout", {}).get("warnings", []):
            print(f"  NOTE: {warning}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
