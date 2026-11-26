# Decisions

Numbered records. Each one has the decision, the reason, and who made it. Supersede a decision with a new entry rather than editing an old one.

## D-001 Validate the core before building the platform (2026-11-26, Nevin)
The first milestone is Experiment 1, "Said versus did". No platform features get built before Gate 1 is passed.
**Why:** published evidence (Kang et al., medRxiv 2026) shows multimodal models mark OSCE physical exams mostly from audio: visual-only agreement was about κ 0.20. Whether a single phone can confirm physical execution is the assumption the product rests on.

## D-002 First station: respiratory examination (2026-11-26, Nevin)
Cardiovascular is the second station.
**Why:** it's a standard, high-value station with gross bilateral manoeuvres (expansion, percussion) at the front and back. Limits accepted: auscultation can only be checked for placement (side and zone), not quality. Partners stay in a vest or sports top.

## D-003 Seen, not said (2026-11-26, Nevin)
Speech never earns marks for a physical step. A spoken step is used to point the system at the right moment, which is then examined more closely.

## D-004 Cheapest pipeline first (2026-11-26, Nevin)
Experiment 1 runs locally on Nevin's Mac. Gemini calls use the paid tier, through the Batch API where latency allows, with Flash-Lite models by default. Pro-class models are used only on a sample, or for clips the cheap model marks as unclear. The free Gemini tier is never used for recordings of people. Fixed infrastructure stays at $0 until the proof of concept (M2).
**Target:** $0.03 to $0.10 per assessment.

## D-005 Stack (2026-11-26, proposed by Claude, accepted with the plan)
Next.js on Vercel; Supabase in the London region; Python worker; Gemini behind a provider interface. Before any external user, AI calls move to Vertex AI `europe-west2`. See ARCHITECTURE.md.

## D-006 Public demonstration videos replace most filming (2026-11-26, Nevin)
Experiment 1 starts with 20 to 40 public respiratory demonstration videos. Gemini reads them from their YouTube URLs, with no download. Negative cases come from clipping windows, and from edited local copies only where the licence or the creator's permission allows. One short filming session of about 1 hour remains, for wrong technique, blocked views and real phone conditions, and it happens before any student uses OSC.ME.
**Why:** Nevin wants minimal filming involvement, and gold-standard demonstrations are widely available. **Accepted limits:** demonstrations show only correct technique and flatter accuracy, so they give an upper bound. Their copyright status restricts them to internal evaluation.
