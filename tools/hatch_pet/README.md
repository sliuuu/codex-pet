# Hatch-Pet Safety Tools

These tracked copies mirror the installed Hatch-Pet skill guardrails used to build Chibi Miku.

The pipeline is fail-closed:

1. `validate_source_strip_safety.py` rejects empty slots, source-edge contact, pixels inside internal guard bands, less than 10% transparent padding, or more than 80% occupancy.
2. `normalize_source_strip_safety.py` may move complete disconnected poses onto a larger transparent source canvas using one shared scale. It refuses missing, connected, or potentially cropped poses.
3. `extract_strip_frames.py` runs source validation automatically and refuses extraction when it fails.
4. `normalize_atlas_cell_safety.py` applies a shared atlas scale while accounting for lower-body anchor extents and preserving intentional jump travel.

Example source validation:

```bash
python3 tools/hatch_pet/validate_source_strip_safety.py row.png \
  --frames 6 \
  --chroma-key '#FF00FF' \
  --json-out source-safety.json \
  --overlay-out source-safety-overlay.png
```

Only source rows with an `ok: true` report may proceed to extraction and atlas creation.
