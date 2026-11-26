"""Deterministic tests for windows and scoring. Run: python -m pytest experiments/exp01-said-vs-did/tools"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from observe import load_labels, mmss  # noqa: E402
from score import score  # noqa: E402
from windows import build_windows  # noqa: E402

V = "https://www.youtube.com/watch?v=test"


def write_labels(tmp_path, rows):
    p = tmp_path / "labels.csv"
    cols = ["video_url", "manoeuvre", "present (yes/no)", "announce (mm:ss)", "start (mm:ss)", "end (mm:ss)",
            "sides (left/right/both)", "zones (e.g. upper|middle|lower)", "visibility (clear/partial/blocked)",
            "labeller", "notes"]
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow(r + [""] * (len(cols) - len(r)))
    return load_labels(p)


def obs(man, start="00:00", seen=True, sides="both", zones=("upper", "middle", "lower")):
    return {"manoeuvre": man, "start": start, "end": start, "seen": seen, "sides": sides,
            "zones": list(zones), "note": ""}


def rec(kind, target, ws, we, observations, error=None):
    return {"video": V, "kind": kind, "target": target, "win_start": ws, "win_end": we,
            "observations": observations, "error": error, "model": "m", "prompt_version": "p"}


def test_mmss():
    assert mmss("03:58") == 238
    assert mmss("") is None
    assert mmss("bad") is None


def test_windows(tmp_path):
    labels = write_labels(tmp_path, [
        [V, "percussion_front", "yes", "04:00", "04:09", "04:24", "both", "upper|middle|lower"],
        [V, "asterixis", "no"],
        [V, "trachea_unlabelled", ""],
    ])
    ws = build_windows(labels)
    kinds = sorted(w.kind for w in ws)
    assert kinds == ["full", "present", "said_not_done"]
    said = [w for w in ws if w.kind == "said_not_done"][0]
    assert said.end == 248 and said.start == 232  # announce-8 .. start-1


def test_score_detection_false_credit_and_alarm(tmp_path):
    labels = write_labels(tmp_path, [
        [V, "percussion_front", "yes", "04:00", "04:09", "04:24", "both", "upper|middle|lower"],
        [V, "asterixis", "no"],
    ])
    records = [
        rec("present", "percussion_front", 244, 269, [obs("percussion_front"), obs("asterixis")]),
        rec("said_not_done", "percussion_front", 232, 248, [obs("percussion_front", seen=False)]),
        rec("full", None, 0, 274, [obs("percussion_front", start="04:11")]),
    ]
    m = score(records, labels)
    assert m["detected (present)"]["percussion_front"] == (1, 1)
    assert m["false credit (said, not done)"]["percussion_front"] == (0, 1)
    assert m["false alarm (absent)"]["asterixis"] == (1, 2)  # present + said_not_done windows
    assert m["side correct"]["percussion_front"] == (1, 1)
    assert m["zones correct"]["percussion_front"] == (1, 1)
    assert m["start within ±3 s (full)"]["percussion_front"] == (1, 1)


def test_errors_never_count_as_passes(tmp_path):
    labels = write_labels(tmp_path, [[V, "percussion_front", "yes", "04:00", "04:09", "04:24"]])
    records = [
        rec("present", "percussion_front", 244, 269, None, error="ValidationError"),
        rec("said_not_done", "percussion_front", 232, 248, None, error="Timeout"),
    ]
    m = score(records, labels)
    assert m["detected (present)"]["percussion_front"] == (0, 1)
    assert m["false credit (said, not done)"]["percussion_front"] == (1, 1)


def test_blocked_rewards_abstaining_and_zones_parse(tmp_path):
    labels = write_labels(tmp_path, [
        [V, "percussion_back", "yes", "", "01:00", "01:20", "both", "upper, middle, lower", "blocked"],
    ])
    assert labels[0].zones == ["upper", "middle", "lower"]
    abstain = score([rec("present", "percussion_back", 55, 85, [])], labels)
    assert abstain["abstained (blocked)"]["ALL"] == (1, 1)
    assert "detected (present)" not in abstain
    credited = score([rec("present", "percussion_back", 55, 85, [obs("percussion_back")])], labels)
    assert credited["abstained (blocked)"]["ALL"] == (0, 1)
