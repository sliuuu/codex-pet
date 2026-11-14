# Codex Pet

ChatGPT Desktop-inspired digital pets that live on the desktop, react to activity, and showcase animated character behaviors through Codex-compatible v2 sprite atlases.

This repository is a self-contained public showcase for seven animated pets. It includes installable pet folders, transparent spritesheets, generated screenshots, GIF demonstrations for every supported animation state, and a small asset pipeline for regenerating the showcase media from the committed spritesheets.

**Unofficial fan project:** The depicted characters, franchise designs, names, and trademarks belong to their respective rights holders. Public source availability, open-source licensing of code, or noncommercial use does not by itself grant rights to those characters or artwork. This repository has no `LICENSE` file; this notice grants no software or artwork license. See [Artwork Provenance and Rights](docs/ARTWORK_PROVENANCE.md).

## Feature Overview

- Desktop-pet style characters that can idle, move, wave, jump, wait, react to failure, show active work, review/scan, and look in 16 directions.
- Installable Codex pet folders with `pet.json`, `avatar.json`, and `assets/spritesheet.webp`.
- GitHub-rendered animation showcase using relative image paths only.
- Reproducible preview generation via `tools/render_showcase_assets.py`.
- All seven pets use `1536x2288` v2 atlases with an `8x11` grid and `192x208` cells. Live Pets service preflight accepts all seven sheets. The four added pets also pass the stricter local packaging/layout checks; the three original atlases fail its empty-slot check, as documented below. Strict 10% per-side padding and 80% occupancy checks belong to the historical Chibi Miku pipeline, not to every pet in this collection.

## Pets

| Pet | Style | Codex contract |
| --- | --- | --- |
| SD Gundam | Super-deformed mecha pixel-art mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| Chibi Asuka | Chibi red-suit mecha-pilot mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| Chibi Miku | Chibi teal twin-tail idol mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| Green Zaku | Green super-deformed mobile-suit mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| Red Zaku | Red super-deformed mobile-suit mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| Gouf | Blue, rounder and glossier mobile-suit mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| GM | Super-deformed GM mobile-suit mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |

All pets include the nine standard Codex animation rows plus two v2 look-direction rows covering 16 clockwise gaze directions.

## SD Gundam

![SD Gundam in action](showcase/sd-gundam-codex-pet/in-action.png)

### Animation Previews

| State | Preview |
| --- | --- |
| Idle | ![SD Gundam idle](showcase/sd-gundam-codex-pet/animations/idle.gif) |
| Run right / walk right | ![SD Gundam running right](showcase/sd-gundam-codex-pet/animations/running-right.gif) |
| Run left / walk left | ![SD Gundam running left](showcase/sd-gundam-codex-pet/animations/running-left.gif) |
| Wave / emote | ![SD Gundam waving](showcase/sd-gundam-codex-pet/animations/waving.gif) |
| Jump | ![SD Gundam jumping](showcase/sd-gundam-codex-pet/animations/jumping.gif) |
| Failed / sad emote | ![SD Gundam sad](showcase/sd-gundam-codex-pet/animations/sad.gif) |
| Waiting | ![SD Gundam waiting](showcase/sd-gundam-codex-pet/animations/waiting.gif) |
| Running / active work | ![SD Gundam running](showcase/sd-gundam-codex-pet/animations/running.gif) |
| Review / scanning | ![SD Gundam review](showcase/sd-gundam-codex-pet/animations/bouncing.gif) |
| 16 look directions | ![SD Gundam look directions](showcase/sd-gundam-codex-pet/animations/look-directions.gif) |

### Sprite Sheet QA

![SD Gundam contact sheet](showcase/sd-gundam-codex-pet/contact-sheet.png)

## Chibi Asuka

![Chibi Asuka in action](showcase/chibi-asuka/in-action.png)

### Animation Previews

| State | Preview |
| --- | --- |
| Idle | ![Chibi Asuka idle](showcase/chibi-asuka/animations/idle.gif) |
| Run right / walk right | ![Chibi Asuka running right](showcase/chibi-asuka/animations/running-right.gif) |
| Run left / walk left | ![Chibi Asuka running left](showcase/chibi-asuka/animations/running-left.gif) |
| Wave / emote | ![Chibi Asuka waving](showcase/chibi-asuka/animations/waving.gif) |
| Jump | ![Chibi Asuka jumping](showcase/chibi-asuka/animations/jumping.gif) |
| Failed / sad emote | ![Chibi Asuka sad](showcase/chibi-asuka/animations/sad.gif) |
| Waiting | ![Chibi Asuka waiting](showcase/chibi-asuka/animations/waiting.gif) |
| Running / active work | ![Chibi Asuka running](showcase/chibi-asuka/animations/running.gif) |
| Review / scanning | ![Chibi Asuka review](showcase/chibi-asuka/animations/bouncing.gif) |
| 16 look directions | ![Chibi Asuka look directions](showcase/chibi-asuka/animations/look-directions.gif) |

### Sprite Sheet QA

![Chibi Asuka contact sheet](showcase/chibi-asuka/contact-sheet.png)

## Chibi Miku

![Chibi Miku in action](showcase/chibi-miku/in-action.png)

### Animation Previews

| State | Preview |
| --- | --- |
| Idle | ![Chibi Miku idle](showcase/chibi-miku/animations/idle.gif) |
| Run right / walk right | ![Chibi Miku running right](showcase/chibi-miku/animations/running-right.gif) |
| Run left / walk left | ![Chibi Miku running left](showcase/chibi-miku/animations/running-left.gif) |
| Wave / happy emote | ![Chibi Miku waving](showcase/chibi-miku/animations/waving.gif) |
| Jump / excited | ![Chibi Miku jumping](showcase/chibi-miku/animations/jumping.gif) |
| Failed / sad emote | ![Chibi Miku sad](showcase/chibi-miku/animations/sad.gif) |
| Waiting / thinking | ![Chibi Miku waiting](showcase/chibi-miku/animations/waiting.gif) |
| Running / active work | ![Chibi Miku running](showcase/chibi-miku/animations/running.gif) |
| Review / celebrate | ![Chibi Miku review](showcase/chibi-miku/animations/bouncing.gif) |
| Sleep showcase | ![Chibi Miku sleep](showcase/chibi-miku/animations/sleep.gif) |
| 16 look directions | ![Chibi Miku look directions](showcase/chibi-miku/animations/look-directions.gif) |

### Combined Preview

![Chibi Miku combined preview](showcase/chibi-miku/animations/combined-preview.gif)

### Sprite Sheet QA

![Chibi Miku contact sheet](showcase/chibi-miku/contact-sheet.png)

### Cell Safety QA

![Chibi Miku cell safety overlay](showcase/chibi-miku/cell-safety-overlay.png)

Blue marks each `192x208` cell, red marks the 10% safe boundary, and green marks the detected character bounds. The build rejects boundary contact, overflow, non-transparent unused cells, scale drift, and lower-body anchor drift before generating GIF previews.

The [Chibi Miku source lineage](showcase/chibi-miku/source-lineage.json) records the generation-to-atlas gates. Generated rows must first pass source-canvas edge, slot padding, occupancy, and transparent-gutter validation; failed source art cannot proceed to extraction or GIF export.

## Green Zaku

### Animation Previews

| State | Preview |
| --- | --- |
| Idle | ![Green Zaku idle](showcase/green-zaku/animations/idle.gif) |
| Run right / walk right | ![Green Zaku running-right](showcase/green-zaku/animations/running-right.gif) |
| Run left / walk left | ![Green Zaku running-left](showcase/green-zaku/animations/running-left.gif) |
| Wave / emote | ![Green Zaku waving](showcase/green-zaku/animations/waving.gif) |
| Jump | ![Green Zaku jumping](showcase/green-zaku/animations/jumping.gif) |
| Failed / sad emote | ![Green Zaku sad](showcase/green-zaku/animations/sad.gif) |
| Waiting | ![Green Zaku waiting](showcase/green-zaku/animations/waiting.gif) |
| Running / active work | ![Green Zaku running](showcase/green-zaku/animations/running.gif) |
| Review / scanning | ![Green Zaku bouncing](showcase/green-zaku/animations/bouncing.gif) |
| 16 look directions | ![Green Zaku look-directions](showcase/green-zaku/animations/look-directions.gif) |

### Sprite Sheet Contact Sheet

![Green Zaku contact sheet](showcase/green-zaku/contact-sheet.png)

## Red Zaku

### Animation Previews

| State | Preview |
| --- | --- |
| Idle | ![Red Zaku idle](showcase/red-zaku/animations/idle.gif) |
| Run right / walk right | ![Red Zaku running-right](showcase/red-zaku/animations/running-right.gif) |
| Run left / walk left | ![Red Zaku running-left](showcase/red-zaku/animations/running-left.gif) |
| Wave / emote | ![Red Zaku waving](showcase/red-zaku/animations/waving.gif) |
| Jump | ![Red Zaku jumping](showcase/red-zaku/animations/jumping.gif) |
| Failed / sad emote | ![Red Zaku sad](showcase/red-zaku/animations/sad.gif) |
| Waiting | ![Red Zaku waiting](showcase/red-zaku/animations/waiting.gif) |
| Running / active work | ![Red Zaku running](showcase/red-zaku/animations/running.gif) |
| Review / scanning | ![Red Zaku bouncing](showcase/red-zaku/animations/bouncing.gif) |
| 16 look directions | ![Red Zaku look-directions](showcase/red-zaku/animations/look-directions.gif) |

### Sprite Sheet Contact Sheet

![Red Zaku contact sheet](showcase/red-zaku/contact-sheet.png)

## Gouf

### Animation Previews

| State | Preview |
| --- | --- |
| Idle | ![Gouf idle](showcase/gouf/animations/idle.gif) |
| Run right / walk right | ![Gouf running-right](showcase/gouf/animations/running-right.gif) |
| Run left / walk left | ![Gouf running-left](showcase/gouf/animations/running-left.gif) |
| Wave / emote | ![Gouf waving](showcase/gouf/animations/waving.gif) |
| Jump | ![Gouf jumping](showcase/gouf/animations/jumping.gif) |
| Failed / sad emote | ![Gouf sad](showcase/gouf/animations/sad.gif) |
| Waiting | ![Gouf waiting](showcase/gouf/animations/waiting.gif) |
| Running / active work | ![Gouf running](showcase/gouf/animations/running.gif) |
| Review / scanning | ![Gouf bouncing](showcase/gouf/animations/bouncing.gif) |
| 16 look directions | ![Gouf look-directions](showcase/gouf/animations/look-directions.gif) |

### Sprite Sheet Contact Sheet

![Gouf contact sheet](showcase/gouf/contact-sheet.png)

## GM

### Animation Previews

| State | Preview |
| --- | --- |
| Idle | ![GM idle](showcase/gm/animations/idle.gif) |
| Run right / walk right | ![GM running-right](showcase/gm/animations/running-right.gif) |
| Run left / walk left | ![GM running-left](showcase/gm/animations/running-left.gif) |
| Wave / emote | ![GM waving](showcase/gm/animations/waving.gif) |
| Jump | ![GM jumping](showcase/gm/animations/jumping.gif) |
| Failed / sad emote | ![GM sad](showcase/gm/animations/sad.gif) |
| Waiting | ![GM waiting](showcase/gm/animations/waiting.gif) |
| Running / active work | ![GM running](showcase/gm/animations/running.gif) |
| Review / scanning | ![GM bouncing](showcase/gm/animations/bouncing.gif) |
| 16 look directions | ![GM look-directions](showcase/gm/animations/look-directions.gif) |

### Sprite Sheet Contact Sheet

![GM contact sheet](showcase/gm/contact-sheet.png)

## Mobile-Suit Lineup

![Mobile suits at a shared preview scale](showcase/mobile-suit-lineup.png)

The lineup uses a shared preview scale for comparison. Gouf retains its existing rounder, glossier style; this update does not repaint it to match the other mobile suits. See the [mobile-suit validation report](docs/validation/mobile-suits.json) for recorded layout checks.

## Animation Summary

| Codex row | State | Frames | Purpose |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | Resting loop with subtle breathing/blink variation |
| 1 | `running-right` | 8 | Directional movement to the right, useful for walk/run drag motion |
| 2 | `running-left` | 8 | Directional movement to the left, useful for walk/run drag motion |
| 3 | `waving` | 4 | Friendly wave emote |
| 4 | `jumping` | 5 | Vertical jump/bounce action |
| 5 | `sad` / failed | 8 | Failure or sad reaction emote |
| 6 | `waiting` | 6 | Waiting for user input or approval |
| 7 | `running` | 6 | Active work / processing loop |
| 8 | `bouncing` / review | 6 | Review, scanning, or focused work loop |
| 9 | look directions `000` to `157.5` | 8 | Up through right and down-right gaze directions |
| 10 | look directions `180` to `337.5` | 8 | Down through left and up-left gaze directions |

There is no dedicated attack row in the Codex pet contract used here. Combat-style actions should map to the existing jump, wave/emote, sad/failed, or active-work loops unless a future renderer adds a formal attack state.

## Installation

Copy any pet folder into your local Codex pets directory:

```bash
mkdir -p ~/.codex/pets
for pet in sd-gundam-codex-pet chibi-asuka chibi-miku green-zaku red-zaku gouf gm; do
  cp -R "pets/$pet" ~/.codex/pets/
done
```

Each pet folder contains:

```text
pet.json
avatar.json
assets/spritesheet.webp
```

The manifests point to `assets/spritesheet.webp` and declare `spriteVersionNumber: 2`, so Codex can load the 11-row v2 atlas including look directions.

## Validation

The original three pets retain their historical validation records below. These are not a fresh semantic or motion-quality review of the seven-pet collection:

| Pet | Result | Dimensions | Notes |
| --- | --- | --- | --- |
| SD Gundam | Pass | `1536x2288` | No clipping, no transparent RGB residue, no validator warnings |
| Chibi Asuka | Pass | `1536x2288` | No clipping, no transparent RGB residue, no validator warnings |
| Chibi Miku | Pass | `1536x2288` | One shared scale across all frames; 10% per-side transparent padding, 80% maximum occupancy, stable lower-body anchors, transparent unused cells, and no clipping, overflow, detached fragments, or validator warnings |

The four added pets are existing custom ChatGPT pet exports, packaged as lossless `1536x2288` WebP atlases. The stricter local packaging/layout validator passes these four additions and reports inherited empty-slot failures for the original three pets. Live Pets service preflight accepts all seven sheets; it does not reject the originals for those extra cells. The latest mobile-suit exports have minimum margins of only 1–9 pixels: they do not clip, but they do **not** satisfy the historical Miku pipeline's 10% padding requirement. No collection-wide strict-padding pass is claimed.

Run the packaging/layout checks and regression tests with:

```bash
python tools/validate_pet_assets.py --pets green-zaku red-zaku gouf gm --json-out docs/validation/mobile-suits.json
python -m unittest discover -s tests

# Expected nonzero exit until the inherited idle-cell issues are repaired:
python tools/validate_pet_assets.py --json-out docs/validation/all-pets.json
```

The [mobile-suit validation report](docs/validation/mobile-suits.json) records passing checks for the four additions. Tests cover the new assets and validator behavior; they do not imply that all original assets pass.

**Known inherited issue:** SD Gundam, Chibi Asuka, and Chibi Miku each have artwork in idle row 0, column 6 (zero-based), while the contract uses only columns 0–5 for that row. The stricter local unused-cell check therefore fails for all three originals, as recorded in the [full repository validation report](docs/validation/all-pets.json). The original files and pet sections remain unchanged. Historical pass records above are separate from today’s service preflight and stricter local validation results. These checks distinguish atlas structure and boundary safety from whether every pose, movement, or gaze direction communicates the intended state. This update does not claim a fresh semantic or motion-quality pass.

### Current Pets Service Preflight

Live service preflight accepts all seven sheets, including the originals with extra idle-cell artwork. This is distinct from both the historical records above and the stricter local empty-slot check. Recorded service results:

- [SD Gundam](docs/validation/sd-gundam-codex-pet-pets-preflight.json)
- [Chibi Asuka](docs/validation/chibi-asuka-pets-preflight.json)
- [Chibi Miku](docs/validation/chibi-miku-pets-preflight.json)
- [Green Zaku](docs/validation/green-zaku-pets-preflight.json)
- [Red Zaku](docs/validation/red-zaku-pets-preflight.json)
- [Gouf](docs/validation/gouf-pets-preflight.json)
- [GM](docs/validation/gm-pets-preflight.json)

The generated contact sheets above are rendered directly from the committed `assets/spritesheet.webp` files. The contract reserves unused slots in variable-length animation rows; the inherited exceptions are noted above. Preview frames are cropped to `192x208` cells and render on transparent backgrounds.

## Regenerate Showcase Assets

The preview GIFs, screenshots, contact sheets, and Chibi Miku cell-safety QA overlay can be regenerated from the committed spritesheets:

```bash
python3 tools/render_showcase_assets.py
```

To refresh only the four additions and the shared-scale lineup, without regenerating the original previews:

```bash
python3 tools/render_showcase_assets.py --pets green-zaku red-zaku gouf gm
python3 tools/render_mobile_suit_lineup.py
```

These scripts do not alter the pet manifests or sprite sheets; they only refresh files under `showcase/`.

The historical Chibi Miku source-stage boundary enforcement is tracked under [`tools/hatch_pet`](tools/hatch_pet/README.md). The guarded extractor blocks sprite-sheet creation unless every generated row first passes the 10% padding, 80% occupancy, transparent-gutter, and source-edge checks.


## Artwork Provenance and Rights

See [Artwork Provenance](docs/ARTWORK_PROVENANCE.md) for the November 12, 2026 export source, preservation notes, and rights limitations. This repository has no `LICENSE` file. Inclusion here does not establish rights clearance or grant a broad license to the artwork or depicted characters. Pet-generation pipeline fixes are separate work and are not included in this asset-packaging update.
