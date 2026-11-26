# Status

Last updated 2026-11-26.

## Implemented
- Nothing user-facing yet.
- Experiment 1 pack (v2 protocol using public demo videos; v1 run scripts kept for the short filming session): protocol, 36 balanced run scripts (`tools/gen_runs.py` regenerates them), consent form, labelling template.

## In progress
- M0 Foundation: repository, docs, Experiment 1 pack. Waiting on Nevin's clinical review of the manoeuvre definitions and the draft respiratory rubric.

## Next
- M1 (v2, D-006): confirm candidate videos and licences, label 20 to 40 public demos, build the evaluation harness (Gemini on YouTube URLs with clip windows), then Tier B on licensed copies. One 1-hour filming session (Tier C) before Gate 1.

## Experimental
- None yet.

## Known limitations (by design)
- Auscultation: placement only, not technique or findings.
- Single camera: the examiner will sometimes block the view, so coverage will be below 100%.

## Open questions
- Which Gemini models are served in Vertex AI `europe-west2`? Check before the pilot.
- Vercel plan pricing for commercial use: verify before M3.
