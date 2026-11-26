# Labelling public videos (Tier A)

Open `public_labels.csv` in Numbers, Excel or Google Sheets. There's one row per video and manoeuvre. Save it back as CSV.

For each row:
- **present:** `yes` if the examiner's hands perform it in the video, `no` if they don't. Leave it blank for videos you haven't watched; blank rows are ignored.
- **announce:** mm:ss when the examiner first says they're about to do it. Leave it blank if they don't say it. This is what creates the "said, not yet done" test windows.
- **start / end:** mm:ss when the hands start and finish the manoeuvre.
- **sides:** `left`, `right` or `both` (the patient's sides). Leave it blank for the trachea and asterixis.
- **zones:** for percussion and auscultation, the zones covered, separated by `|`, for example `upper|middle|lower`.
- **visibility:** `clear`, `partial` or `blocked`.
- **labeller:** your initials.

About 5 minutes per video. Label the first 5 videos without looking at any Gemini output, so we can check that the model isn't steering the labels.

To add a video, add it to `candidates.csv` and copy 8 rows (one per manoeuvre) into `public_labels.csv`.

## Running and scoring (from the repository root)
```
.venv/bin/python experiments/exp01-said-vs-did/tools/run.py --dry-run      # shows windows and estimated cost
.venv/bin/python experiments/exp01-said-vs-did/tools/run.py --max-cost 0.50
.venv/bin/python experiments/exp01-said-vs-did/tools/score.py experiments/exp01-said-vs-did/results/<file>.jsonl
```
