# Architecture

Status: planned. Nothing below is built yet except where STATUS.md says so.

## Parts
| Part | Technology | Role |
| --- | --- | --- |
| Web app | Next.js (App Router), TypeScript, Tailwind, restyled shadcn/ui, on Vercel | Station pages, camera setup check, recorder, reports |
| Platform | Supabase (London): Postgres + RLS, Auth, private Storage (TUS resumable uploads), `jobs` table | Data, login, video storage, job queue |
| Worker | Python on Modal (or Cloud Run, London) | Normalise video, pose and hand tracking, transcription, Gemini clip checks, ledger, scoring, feedback |
| Engine | Pure Python package, no network | Evidence ledger in, criterion statuses, scores and coverage out |
| AI | Gemini behind `analyse_clip(clip, question, schema)` | Observations only, structured JSON, model and prompt version stored |

## Data flow
1. Phone: setup check (MediaPipe in the browser), calibration clip, recording in 1 to 2 s chunks saved to IndexedDB, Screen Wake Lock.
2. Resumable upload to a private bucket; a row in `jobs` is created.
3. Worker: ffprobe validation → FFmpeg normalisation (720p H.264, 16 kHz mono WAV) → MediaPipe pose and hands at 10 to 15 fps → local Whisper transcript with word timestamps.
4. Candidate windows come from speech cues ("I'll now percuss…") and pose events. Gemini Flash-Lite looks at each short muted clip at higher fps. Unclear clips may escalate to a stronger model.
5. Observations are written to the evidence ledger (Supabase).
6. The engine applies the rubric rules → statuses, score and coverage.
7. The feedback writer gets only the ledger and the rubric guidance, and must cite observation IDs. A validator rejects anything unsupported.
8. The report is available on any device, with links that jump to the evidence timestamps.

## Data location
- Experiment 1: local Mac plus the Gemini paid API, with consented team recordings only.
- Before any external user: Vertex AI `europe-west2` regional endpoint, caching disabled (zero retention), Supabase London.

## Recording constraints (iOS)
Record in a Safari tab, not an installed PWA (there are reported getUserMedia failures after relaunch). Avoid assembling one huge Blob in memory. Cap stations at about 10 minutes. Use 720p at about 2.5 Mbps.

## Future native apps
An Expo app reuses Supabase auth, storage and jobs. Only the recorder is web-specific.
