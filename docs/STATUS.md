# Status

Last updated 2026-11-26.

## Implemented
- Nothing user-facing yet.
- Experiment 1 pack: protocol, 36 balanced run scripts (`tools/gen_runs.py` regenerates them), consent form, labelling template.

## In progress
- M0 Foundation: repository, docs, Experiment 1 pack. Waiting on Nevin's clinical review of the manoeuvre definitions and the draft respiratory rubric.

## Next
- M1: record the 36 runs (two sessions), label them, build the evaluation harness, run the four pipelines, decide Gate 1.

## Experimental
- None yet.

## Known limitations (by design)
- Auscultation: placement only, not technique or findings.
- Single camera: the examiner will sometimes block the view, so coverage will be below 100%.

## Open questions
- Which Gemini models are served in Vertex AI `europe-west2`? Check before the pilot.
- Vercel plan pricing for commercial use: verify before M3.
