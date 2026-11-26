# Experiment 1: "Said versus did" (respiratory)

Status: v2 draft, 26 November 2026. v1 relied on 36 filmed runs. v2 replaces most of that filming with public demonstration videos (decision D-006). One short filming session remains for the cases that public videos cannot provide.

## Question

Can a pipeline confirm that a respiratory-examination manoeuvre was physically performed, on the correct side and zones, without relying on what was said?

## Three tiers

| Tier | Source | Conditions it tests | Nevin's time |
| --- | --- | --- | --- |
| A | 20 to 40 public YouTube demonstrations, read by Gemini directly from the URL (no download) | Correct performance (C1), timing, side and zone, sequence; "said, not yet done" and "absent" windows (below) | About 2 to 3 hours labelling, or correcting draft labels |
| B | Local copies of videos whose licence allows it, or whose creator has given permission | Muted video (C2); narration spliced over a clip with the manoeuvre removed (C3); manoeuvre removed entirely (C4) | None |
| C | One filming session, about 1 hour, two phones | Wrong technique (C5), blocked view (C6), real phone conditions | About 1 hour plus volunteers |

Tier A runs first. Tier C happens before any student uses OSC.ME, not before building starts.

## Tier A details

**Inclusion:** real footage (not animation); continuous enough to follow each manoeuvre; both anterior and posterior chest shown; public on YouTube. Record the number of camera cuts per minute as a covariate.

**Exclusion:** slideshows, narrated diagrams, and compilations without a full examination.

**Windows instead of edits.** Gemini accepts start and end offsets on YouTube URLs, so negative cases can be made without editing:
- *Said, not yet done (C3-like):* a window that ends after the examiner announces a manoeuvre but before their hands start it.
- *Absent (C4-like):* a window from another part of the examination, asked about a manoeuvre that does not occur in it.
- *Present (C1):* a window that contains the whole manoeuvre.

Limits: we cannot mute a YouTube URL, so vision-only performance is measured in Tier B. Demo videos flatter accuracy (good light, multiple angles, edited). Results are an upper bound, not the product's real accuracy.

## Manoeuvres

| ID | Manoeuvre | What counts as done |
| --- | --- | --- |
| M1 | Asterixis | Patient's arms outstretched, wrists cocked back, held for about 15 s |
| M2 | Tracheal position | Examiner's finger(s) in the sternal notch |
| M3 | Chest expansion, front | Both hands on the lower anterior chest, thumbs meeting, patient breathes in |
| M4 | Percussion, front | Upper, middle and lower zones, both sides, compared |
| M5 | Auscultation, front | Upper, middle and lower zones, both sides, compared |
| M6 | Chest expansion, back | Both hands on the lower posterior chest |
| M7 | Percussion, back | Upper, middle and lower zones, both sides |
| M8 | Auscultation, back | Upper, middle and lower zones, both sides |

Nevin to check these definitions clinically.

## Labels

For each video and manoeuvre: present or absent, start and end (mm:ss), sides, zones, whether it was narrated, and visibility. Claude can produce draft labels for Nevin to correct. Correcting is faster, but it risks anchoring the labeller on the model's view, so 5 videos are labelled blind first and compared.

## Pipelines

1. Gemini on the window, with audio (Tier A and B).
2. Gemini on the window, muted (Tier B only).
3. MediaPipe pose and hands with rules (Tier B and C: needs local video).
4. Hybrid: speech cues and pose propose windows; Gemini Flash-Lite judges muted clips; rules decide (Tier B and C).

## Thresholds

Unchanged from v1 (see docs/VALIDATION.md). Tier A results alone cannot pass Gate 1, because C2 and C5 are not tested there.

## Copyright and data handling

- Public videos are used only for internal evaluation. They are never shown in OSC.ME, redistributed, or used to train models.
- Tier A sends only the YouTube URL to Gemini; no copy is made.
- Tier B uses only Creative Commons videos that allow it, or videos whose creator has given written permission.
- Before any public accuracy claim, ask the creators whose videos were used for permission.
- Tier C follows the consent form in `consent.md`.

## Files

- `candidates.csv`: candidate videos with licence status (to be checked by opening each video's description).
- `run_scripts.csv`, `labels_template.csv`: v1 materials, kept for Tier C. Tier C will use a cut-down script of about 10 runs.
