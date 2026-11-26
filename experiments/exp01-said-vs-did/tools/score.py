"""Score saved Gemini observations against the labels. No model calls; deterministic.

    python experiments/exp01-said-vs-did/tools/score.py results/<run_id>.jsonl [--labels public_labels.csv]

Prints a markdown report:
- Detection (present windows): was the target manoeuvre reported as seen?
- False credit (said_not_done windows): was the announced-but-not-yet-done manoeuvre reported as seen?
- False alarms: in any window, a manoeuvre reported as seen that the labels say is absent from that stretch.
- Side and zone agreement, and start-time error within ±3 s (full windows), where labels exist.
- Consistency: same detection answer across repeats.
Window errors (invalid or failed responses) count as failures, never as passes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from observe import MANOEUVRES, Label, load_labels, mmss  # noqa: E402

TIME_TOLERANCE = 3.0


def _seen(observations: Optional[list], manoeuvre: str) -> Optional[dict]:
    for o in observations or []:
        if o.get("manoeuvre") == manoeuvre and o.get("seen"):
            return o
    return None


def _overlaps(label: Label, start: float, end: float) -> bool:
    return label.start is not None and label.end is not None and label.start < end and label.end > start


def _rate(hits: int, total: int) -> str:
    return f"{hits}/{total} ({100 * hits / total:.0f}%)" if total else "n/a"


def score(records: List[dict], labels: List[Label]) -> Dict[str, Dict[str, Tuple[int, int]]]:
    """Returns metric -> manoeuvre -> (hits, total). 'ALL' aggregates."""
    index = {(l.video, l.manoeuvre): l for l in labels if l.present is not None}
    m: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    consistency: Dict[Tuple[str, str, float, str], set] = defaultdict(set)

    def add(metric: str, man: str, ok: bool) -> None:
        for key in (man, "ALL"):
            m[metric][key][0] += int(ok)
            m[metric][key][1] += 1

    for r in records:
        obs = r.get("observations")
        failed = r.get("error") is not None or obs is None
        video, kind, target = r["video"], r["kind"], r.get("target")
        ws, we = r["win_start"], r["win_end"]

        if kind == "present" and target:
            hit = None if failed else _seen(obs, target)
            add("detected (present)", target, hit is not None)
            consistency[(video, kind, ws, target)].add(hit is not None)
            lab = index.get((video, target))
            if hit and lab:
                if lab.sides:
                    add("side correct", target, hit.get("sides") == lab.sides)
                if lab.zones:
                    add("zones correct", target, sorted(hit.get("zones") or []) == sorted(lab.zones))

        if kind == "said_not_done" and target:
            credited = failed or _seen(obs, target) is not None  # a failure is not a pass
            add("false credit (said, not done)", target, credited)

        if kind == "full":
            for man in MANOEUVRES:
                lab = index.get((video, man))
                if not lab or not lab.present or lab.start is None:
                    continue
                hit = None if failed else _seen(obs, man)
                pred = mmss(hit.get("start", "")) if hit else None
                add("start within ±3 s (full)", man, pred is not None and abs(pred - lab.start) <= TIME_TOLERANCE)

        # False alarms: any labelled-absent manoeuvre (or one outside this stretch) reported as seen.
        if not failed:
            for man in MANOEUVRES:
                lab = index.get((video, man))
                if lab is None or man == target:
                    continue
                truly_here = bool(lab.present) and _overlaps(lab, ws, we)
                if not truly_here and kind != "full":
                    add("false alarm (absent)", man, _seen(obs, man) is not None)

    for (_, _, _, target), answers in consistency.items():
        m["consistent across repeats"][target][1] += 1
        m["consistent across repeats"][target][0] += int(len(answers) == 1)
        m["consistent across repeats"]["ALL"][1] += 1
        m["consistent across repeats"]["ALL"][0] += int(len(answers) == 1)

    return {k: {kk: (vv[0], vv[1]) for kk, vv in v.items()} for k, v in m.items()}


def report(metrics: Dict[str, Dict[str, Tuple[int, int]]], records: List[dict]) -> str:
    cols = MANOEUVRES + ["ALL"]
    lines = ["| Metric | " + " | ".join(c.replace("_", " ") for c in cols) + " |",
             "| --- |" + " --- |" * len(cols)]
    order = ["detected (present)", "false credit (said, not done)", "false alarm (absent)",
             "side correct", "zones correct", "start within ±3 s (full)", "consistent across repeats"]
    for metric in order:
        if metric in metrics:
            row = metrics[metric]
            lines.append(f"| {metric} | " + " | ".join(_rate(*row.get(c, (0, 0))) for c in cols) + " |")
    errors = sum(1 for r in records if r.get("error"))
    cost = sum(r.get("cost_usd") or 0 for r in records)
    models = sorted({r["model"] for r in records})
    lines += ["", f"Windows: {len(records)} · errors: {errors} · estimated cost ${cost:.4f} · "
                  f"model(s): {', '.join(models)} · prompt: {records[0]['prompt_version'] if records else '-'}",
              "Lower is better for false credit and false alarms; higher is better for everything else."]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    parser.add_argument("--labels", default=str(HERE.parent / "public_labels.csv"))
    args = parser.parse_args()
    records = [json.loads(line) for line in open(args.results) if line.strip()]
    print(report(score(records, load_labels(Path(args.labels))), records))


if __name__ == "__main__":
    main()
