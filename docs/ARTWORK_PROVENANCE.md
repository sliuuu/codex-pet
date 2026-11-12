# Artwork Provenance and Rights

## Scope and source

On November 12, 2026, the existing custom ChatGPT pets Green Zaku, Red Zaku, Gouf, and GM were exported from the owner's pet collection for addition to this repository. They join the existing SD Gundam, Chibi Asuka, and Chibi Miku assets. These are AI-assisted fan artworks derived from user-provided references, not newly commissioned or freshly repainted artwork for this repository update. Ownership of a custom pet collection is not a claim of intellectual-property ownership in the depicted characters.

The original reference images are not included. No rights clearance for the references, generated artwork, character designs, names, or associated franchises is claimed.

## Asset preservation

- The four added spritesheets are packaged as lossless WebP at `1536x2288`, preserving the v2 `8x11` atlas layout and `192x208` cells.
- The existing SD Gundam's current PNG export is pixel-identical to the committed WebP. Its original committed asset is retained unchanged.
- The existing SD Gundam, Chibi Asuka, and Chibi Miku pet sections and assets remain part of the collection.
- Gouf retains its rounder, glossier appearance. This is a known visual-review point, not a new repaint or a claim that every mobile suit has an identical art style.

## Validation boundaries

Live Pets service preflight accepts all seven sheets, including the originals with extra idle-cell artwork. Service reports are saved as `docs/validation/<slug>-pets-preflight.json` and linked individually from the README. This service result is distinct from the historical validation records and the stricter local checker.

The four additions pass the stricter local packaging and atlas-layout checks. The full seven-pet local check reports three inherited failures: SD Gundam, Chibi Asuka, and Chibi Miku each contain artwork in idle row 0, column 6 (zero-based), which is unused under the six-frame idle contract. Their original files remain unchanged. See the [full repository report](validation/all-pets.json); historical validation records are not current local pass results, and these local failures do not mean that service preflight rejects the originals. The strict 10% per-side transparent-padding and 80% occupancy rules documented for historical Chibi Miku source generation do not describe the four latest exports. Those exports have minimum cell margins of 1–9 pixels and do not clip, but do not meet the 10% padding threshold.

Generated previews and contact sheets support inspection; they do not establish a fresh semantic or motion-quality pass. See [the mobile-suit report](validation/mobile-suits.json) and run:

```bash
python tools/validate_pet_assets.py --pets green-zaku red-zaku gouf gm --json-out docs/validation/mobile-suits.json
python -m unittest discover -s tests

# Expected nonzero exit until the inherited idle-cell issues are repaired:
python tools/validate_pet_assets.py --json-out docs/validation/all-pets.json
```

Tests cover the new assets and validator behavior, not a claim that the original three atlases pass.

Pet-generation pipeline fixes are separate work and are not included in this asset-packaging update.

## Rights and reuse

This repository has no `LICENSE` file. Do not infer a broad license from public availability or from inclusion of these assets. No ownership or licensing authority is asserted over Gundam-related designs, Hatsune Miku, Asuka, or their associated names and intellectual property. Anyone considering redistribution, modification, or commercial use must independently establish the necessary permissions.
