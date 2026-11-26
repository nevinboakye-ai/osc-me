"""Send every Experiment 1 window to Gemini and save the raw observations.

Run from the repository root:
    python experiments/exp01-said-vs-did/tools/run.py --dry-run
    python experiments/exp01-said-vs-did/tools/run.py --model gemini-3.8-flash --prompt obs-v2 --repeats 1 --max-cost 1.00

Results go to experiments/exp01-said-vs-did/results/<run_id>.jsonl, one line per window and repeat.
The run stops before it would pass --max-cost (estimated from the tokens actually used so far).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from observe import PROMPTS, PROMPT_VERSION, ask_gemini, estimate_cost, load_key, load_labels  # noqa: E402
from windows import build_windows  # noqa: E402

TOKENS_PER_SECOND_LOW = 110  # measured: ~109/s over 106 windows (26 Nov 2026)
OUTPUT_TOKENS = {"gemini-3.8-flash": 1100}  # thinking tokens; measured mean 1,088 per window
DEFAULT_OUTPUT_TOKENS = 400


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default=str(HERE.parent / "public_labels.csv"))
    parser.add_argument("--model", default="gemini-3.8-flash")  # D-007
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--kinds", default="full,present,said_not_done")
    parser.add_argument("--max-cost", type=float, default=1.00, help="USD ceiling for this run")
    parser.add_argument("--prompt", default=PROMPT_VERSION, choices=sorted(PROMPTS))
    parser.add_argument("--only", help="comma-separated video ids to include (e.g. to rerun a subset)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    kinds = set(args.kinds.split(","))
    windows = [w for w in build_windows(load_labels(Path(args.labels))) if w.kind in kinds]
    if args.only:
        ids = set(args.only.split(","))
        windows = [w for w in windows if w.video.rsplit("=", 1)[-1] in ids]
    seconds = sum(w.end - w.start for w in windows) * args.repeats
    est = estimate_cost(args.model, int(seconds * TOKENS_PER_SECOND_LOW), OUTPUT_TOKENS.get(args.model, DEFAULT_OUTPUT_TOKENS) * len(windows) * args.repeats)
    print(f"{len(windows)} windows x {args.repeats} repeats, {seconds / 60:.1f} min of video, "
          f"estimated ${est or 0:.3f} if billed (YouTube input is free during preview)")
    for kind in sorted(kinds):
        print(f"  {kind}: {sum(1 for w in windows if w.kind == kind)}")
    if args.dry_run or not windows:
        return

    from google import genai

    client = genai.Client(api_key=load_key())
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{args.model}_{args.prompt}"
    out_dir = HERE.parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{run_id}.jsonl"
    spent = 0.0
    with open(out_path, "w") as out:
        for repeat in range(args.repeats):
            for i, w in enumerate(windows, 1):
                if spent >= args.max_cost:
                    print(f"Stopped: reached --max-cost ${args.max_cost:.2f}")
                    break
                record = {"run_id": run_id, "model": args.model, "prompt_version": args.prompt,
                          "video": w.video, "kind": w.kind, "target": w.target,
                          "win_start": w.start, "win_end": w.end, "repeat": repeat}
                try:
                    answer, inp, outp = ask_gemini(client, args.model, w.video, w.start, w.end, args.prompt)
                    cost = estimate_cost(args.model, inp, outp) or 0.0
                    spent += cost
                    record.update(observations=[o.model_dump() for o in answer.observations],
                                  input_tokens=inp, output_tokens=outp, cost_usd=round(cost, 6), error=None)
                except Exception as exc:  # keep going; failures are scored as failures, never guessed
                    record.update(observations=None, error=f"{type(exc).__name__}: {str(exc)[:300]}")
                out.write(json.dumps(record) + "\n")
                out.flush()
                status = "error" if record["error"] else f"{len(record['observations'])} obs"
                print(f"[{repeat + 1}.{i}/{len(windows)}] {w.kind:<14} {w.target or '-':<22} {status}")
                time.sleep(0.5)
    print(f"\nSaved {out_path}  estimated spend ${spent:.4f}")
    print(f"Score it: python experiments/exp01-said-vs-did/tools/score.py {out_path}")


if __name__ == "__main__":
    main()
