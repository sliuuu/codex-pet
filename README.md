# Codex Pet

ChatGPT Desktop-inspired digital pets that live on the desktop, react to activity, and showcase animated character behaviors through Codex-compatible v2 sprite atlases.

This repository is a self-contained public showcase for three polished animated pets. It includes installable pet folders, transparent spritesheets, generated screenshots, GIF demonstrations for every supported animation state, and a small asset pipeline for regenerating the showcase media from the committed spritesheets.

## Feature Overview

- Desktop-pet style characters that can idle, move, wave, jump, wait, react to failure, show active work, review/scan, and look in 16 directions.
- Installable Codex pet folders with `pet.json`, `avatar.json`, and `assets/spritesheet.webp`.
- GitHub-rendered animation showcase using relative image paths only.
- Reproducible preview generation via `tools/render_showcase_assets.py`.
- Validated v2 sprite contract: `1536x2288` atlas, `8x11` grid, `192x208` cells, transparent backgrounds, and no validator warnings.

## Pets

| Pet | Style | Codex contract |
| --- | --- | --- |
| SD Gundam | Super-deformed mecha pixel-art mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| Chibi Asuka | Chibi red-suit mecha-pilot mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |
| Chibi Miku | Chibi teal twin-tail idol mascot | `spriteVersionNumber: 2`, `1536x2288`, `8x11`, `192x208` cells |

Both pets include the nine standard Codex animation rows plus two v2 look-direction rows covering 16 clockwise gaze directions.

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

Copy either pet folder into your local Codex pets directory:

```bash
mkdir -p ~/.codex/pets
cp -R pets/sd-gundam-codex-pet ~/.codex/pets/
cp -R pets/chibi-asuka ~/.codex/pets/
cp -R pets/chibi-miku ~/.codex/pets/
```

Each pet folder contains:

```text
pet.json
avatar.json
assets/spritesheet.webp
```

The manifests point to `assets/spritesheet.webp` and declare `spriteVersionNumber: 2`, so Codex can load the 11-row v2 atlas including look directions.

## Validation

Both installed source atlases were validated with the hatch-pet atlas validator before this repo was prepared:

| Pet | Result | Dimensions | Notes |
| --- | --- | --- | --- |
| SD Gundam | Pass | `1536x2288` | No clipping, no transparent RGB residue, no validator warnings |
| Chibi Asuka | Pass | `1536x2288` | No clipping, no transparent RGB residue, no validator warnings |
| Chibi Miku | Pass | `1536x2288` | No clipping, no transparent RGB residue, no validator warnings; sad/failed row regenerated to remove hair ghosting and alignment drift |

The generated contact sheets above are rendered directly from the committed `assets/spritesheet.webp` files. Empty cells are intentional unused slots in variable-length animation rows; populated cells are clipped to `192x208` and render on transparent backgrounds.

## Regenerate Showcase Assets

The preview GIFs, screenshots, and contact sheets can be regenerated from the committed spritesheets:

```bash
python3 tools/render_showcase_assets.py
```

The script does not alter the pet manifests or sprite sheets; it only refreshes files under `showcase/`.
