# Status

Last updated 2026-11-26.

## Implemented
- Nothing user-facing yet.
- Experiment 1 pack (v2 protocol using public demo videos; v1 run scripts kept for the short filming session): protocol, 36 balanced run scripts (`tools/gen_runs.py` regenerates them), consent form, labelling template.

## In progress
- M1 Experiment 1 (public videos): harness and first results done. Next: reduce false credit below 10% (sustained-contact rule, tighter labels, muted-audio Tier B). Still waiting on Nevin's clinical review of the manoeuvre definitions and the draft respiratory rubric.

## Next
- M1 (v2, D-006): confirm candidate videos and licences, label 20 to 40 public demos, build the evaluation harness (Gemini on YouTube URLs with clip windows), then Tier B on licensed copies. One 1-hour filming session (Tier C) before Gate 1.

## Experimental
- Experiment 1 evaluation harness (`experiments/exp01-said-vs-did/tools`): runs Gemini on YouTube clip windows and scores against human labels. Works end to end on Nevin's Mac. 8 public videos labelled by Nevin (64 rows).
- First results, 26 Nov 2026, obs-v2 prompt, 93 windows per model, 1 repeat (internal evaluation only, n is small):

| Metric | gemini-3.5-flash-lite | gemini-3.8-flash | Threshold |
| --- | --- | --- | --- |
| Detected when done | 59/59 | 59/59 | ≥85% |
| False credit when only announced | 17/32 (53%) | 7/32 (22%) | ≤10% |
| Credited steps the labeller could not see (blocked) | 2/2 | 2/2 | ≤30% |
| False alarm | 2% | 1% | — |
| Side correct | 100% | 94% | ≥90% |
| Zones correct | 69% | 93% | ≥90% |
| Cost for 93 windows | $0.10 | $0.56 | — |

  Neither model passes the false-credit threshold yet. All 7 of 3.8-flash's false credits are 2–4 s before the labelled start; flash-lite's include 10–17 s early. obs-v1 vs obs-v2 prompt made no difference for flash-lite (44% vs 46%). Total spend on Experiment 1 so far about $1.27.

## Known limitations (by design)
- Auscultation: placement only, not technique or findings.
- Single camera: the examiner will sometimes block the view, so coverage will be below 100%.

## Open questions
- Which Gemini models are served in Vertex AI `europe-west2`? Check before the pilot.
- Vercel plan pricing for commercial use: verify before M3.
