# OSC.ME

An AI OSCE examiner that gives medical students feedback on the physical examination they actually performed, using a smartphone recording.

**Status:** Phase 0, product discovery. No application code yet. The first milestone is Experiment 1, "Said versus did" ([protocol](experiments/exp01-said-vs-did/protocol.md)). It tests whether a single phone video can confirm that a respiratory-examination manoeuvre was physically performed, without relying on what the student says.

## Repository layout

```
docs/          product, architecture, assessment method, privacy, validation, decisions, status
content/       clinical content: stations, rubrics, the manoeuvre vocabulary (versioned YAML)
experiments/   experiment protocols, scripts, label templates and results (never videos)
```

Planned, not yet created: `apps/web` (Next.js), `worker/` (Python processing), `engine/` (pure Python assessment engine), `supabase/` (migrations). See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Rules

- Recordings never go in Git (`.gitignore` blocks common video formats).
- Secrets live in `.env.local`, never in Git. See `.env.example`.
- [docs/STATUS.md](docs/STATUS.md) says what is real and what is planned. Nothing is described as working until it works.

## Founding plan

The full first-assignment write-up (evaluation, research, architecture, costs, roadmap) is kept outside the repository as a shared document. This repository holds the decisions that came from it.
