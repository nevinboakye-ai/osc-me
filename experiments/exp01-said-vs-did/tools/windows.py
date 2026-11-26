"""Turn labels into the clip windows that Experiment 1 sends to Gemini.

Window kinds:
- full: the whole labelled stretch of a video (for timing and order).
- present: one labelled manoeuvre plus a few seconds either side (should be reported as seen).
- said_not_done: from just before the examiner announces a manoeuvre to just before their hands
  start it (should NOT be reported as seen). Only made when that gap is at least 3 s.
Non-target manoeuvres inside any window give the "absent" cases for free.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from observe import Label

PAD = 5.0
MIN_SAID_GAP = 3.0


@dataclass(frozen=True)
class Window:
    video: str
    kind: str  # full | present | said_not_done
    target: Optional[str]
    start: float
    end: float


def build_windows(labels: List[Label]) -> List[Window]:
    by_video: Dict[str, List[Label]] = {}
    for label in labels:
        if label.present is not None:
            by_video.setdefault(label.video, []).append(label)

    windows: List[Window] = []
    for video, rows in by_video.items():
        present = [r for r in rows if r.present and r.start is not None and r.end is not None]
        if not present:
            continue
        last_end = max(r.end for r in present)
        windows.append(Window(video, "full", None, 0.0, last_end + 10))
        for r in present:
            windows.append(Window(video, "present", r.manoeuvre, max(0.0, r.start - PAD), r.end + PAD))
            if r.announce is not None and r.start - r.announce >= MIN_SAID_GAP:
                windows.append(Window(video, "said_not_done", r.manoeuvre,
                                      max(0.0, r.announce - 8), r.start - 1))
    return windows
