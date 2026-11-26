# Experiment 1: "Said versus did" (respiratory)

Status: draft for Nevin's review, 26 November 2026.

## Question

From a single phone, can any pipeline confirm that a respiratory-examination manoeuvre was physically performed, on the correct side and zones, without relying on what the student says?

## People

- 3 student examiners (E1 to E3) and 2 practice partners (P1, P2). Everyone signs `consent.md` before recording.
- Partners wear a vest or sports top. Stethoscope over thin clothing is fine. Nothing intimate is filmed.
- One person (usually Nevin) runs the session: reads the next run's script aloud, starts and stops both phones.

## Equipment

- 2 phones on tripods or clamps, landscape, 1080p 30 fps, using the phones' own camera apps.
- Couch with the backrest at 45 degrees, or an upright chair if no couch.
- Stethoscope. Ordinary room lighting; avoid a bright window behind the patient.
- A printout of `run_scripts.csv`, one sheet per run.

## Camera positions (both phones record every run)

| Camera | Position | Height | Distance |
| --- | --- | --- | --- |
| `side` | Patient's left, perpendicular to the patient | Patient's chest height | 2 to 2.5 m, both people fully in frame |
| `diagonal` | 45 degrees from the patient's front-left | Patient's chest height | 2 to 2.5 m, both people fully in frame |

The examiner works from the patient's right as usual, and moves behind the patient for the back of the chest.

## Each run (about 4 minutes)

1. Start both phones. Everyone claps once (this syncs the two videos).
2. Calibration: the examiner raises their right hand, then the partner raises their right hand.
3. Examiner gives a normal introduction and consent request.
4. Examiner performs the 8 manoeuvres in order (M1 to M8), each following its condition in the script.
5. Examiner says "Examination finished". Stop both phones.
6. Rename both files: `R07_side.mp4`, `R07_diagonal.mp4`.

The script fixes which of six conditions applies to each manoeuvre:

| Code | Condition |
| --- | --- |
| C1 | Do it correctly and say it out loud |
| C2 | Do it correctly in silence |
| C3 | Say you are doing it, then move on without doing it |
| C4 | Skip it: do not do it, do not mention it |
| C5 | Do it wrongly (the script says how), narrating normally |
| C6 | Do it correctly and narrate, but block the side-on camera with your body |

Across each examiner–partner pair's 6 runs, every manoeuvre gets every condition exactly once (a balanced Latin square). In total: 36 runs, 288 manoeuvre instances, each filmed from two angles.

Suggested sessions: two sessions of about 2.5 hours (18 runs each, with breaks).

## Manoeuvres

| ID | Manoeuvre | What counts as done |
| --- | --- | --- |
| M1 | Asterixis | Patient's arms outstretched, wrists cocked back, held for about 15 s |
| M2 | Tracheal position | Examiner's finger(s) in the sternal notch |
| M3 | Chest expansion, front | Both hands on the lower anterior chest, thumbs meeting, patient breathes in |
| M4 | Percussion, front | Upper, middle and lower zones, both sides, compared side to side |
| M5 | Auscultation, front | Upper, middle and lower zones, both sides, compared side to side |
| M6 | Chest expansion, back | Both hands on the lower posterior chest |
| M7 | Percussion, back | Upper, middle and lower zones, both sides |
| M8 | Auscultation, back | Upper, middle and lower zones, both sides |

Nevin to check these definitions clinically before the first session.

## Labelling (after recording)

Fill `labels_template.csv`: one row per run, camera and manoeuvre (576 rows). Record what actually happened, not what the script intended: a slip is fine, just label it. Times are mm:ss from the start of that camera's file. `visibility` is judged per camera.

## Pipelines compared

1. Gemini on the whole run with audio.
2. Gemini on the whole run, muted.
3. MediaPipe pose and hands with hand-written rules.
4. Hybrid (main design): speech cues and pose flag candidate moments; Gemini Flash-Lite looks closely at each short muted clip; rules decide. Marks require visual confirmation.

Cost controls: runs locally on Nevin's Mac; Gemini paid tier via Batch API (half price), Flash-Lite models by default, a Pro-class model only on a sample of about 40 clips. Expected AI spend $5 to $15.

## Pass thresholds (agreed before seeing results)

| Measure | Pass | Fail |
| --- | --- | --- |
| Silent manoeuvres detected (C2) | ≥ 85% | < 70% |
| False credit for said-only (C3) | ≤ 10% | > 25% |
| Correct side, and zones for M4/M5/M7/M8 | ≥ 90% | < 80% |
| Timestamp within ±3 s | ≥ 90% | < 75% |
| Says "insufficient evidence" when blocked (C6) | ≥ 70% | < 40% |
| Same answer on 3 repeat runs | ≥ 90% | < 80% |

Pass = one pipeline and camera position meets every threshold on at least 6 of the 8 manoeuvres.

## Data handling

- Videos stay on Nevin's Mac and the team's agreed storage. They never go into Git.
- Videos are sent only to the paid Gemini API, which does not use them to improve Google's products.
- These recordings are for internal development. Nothing is published without ethics approval.
- All raw videos are deleted within 12 months, or sooner on any participant's request.
