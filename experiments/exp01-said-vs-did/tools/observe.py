"""Shared pieces for Experiment 1: label parsing, the observation schema, and the Gemini call.

Gemini only ever returns observations here. Scoring lives in score.py and never calls a model.
"""
from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

PROMPT_VERSION = "obs-v2"  # default; see PROMPTS

MANOEUVRES = [
    "asterixis", "tracheal_position", "chest_expansion_front", "percussion_front",
    "auscultation_front", "chest_expansion_back", "percussion_back", "auscultation_back",
]

# USD per million tokens (Gemini API paid tier, standard rates, checked 2026-11-26).
PRICES = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
    "gemini-3.8-flash": (0.75, 3.75),  # rises to 1.50 / 7.50 from 2027-01-01
}

Manoeuvre = Literal[
    "asterixis", "tracheal_position", "chest_expansion_front", "percussion_front",
    "auscultation_front", "chest_expansion_back", "percussion_back", "auscultation_back", "other",
]


class Observation(BaseModel):
    manoeuvre: Manoeuvre
    start: str = Field(description="MM:SS when the examiner's hands begin the manoeuvre")
    end: str = Field(description="MM:SS when it ends")
    seen: bool = Field(description="True only if the manoeuvre is visible on screen, not merely mentioned")
    sides: Literal["left", "right", "both", "not_applicable", "unclear"]
    zones: List[Literal["upper", "middle", "lower"]]
    note: str = Field(description="One short sentence on what is visible")


class Answer(BaseModel):
    observations: List[Observation]


PROMPT = """You are observing a clip from a demonstration of a respiratory examination.
List each of these manoeuvres that you can SEE being performed in this clip:
asterixis, tracheal_position, chest_expansion_front, percussion_front, auscultation_front,
chest_expansion_back, percussion_back, auscultation_back. Use "other" for anything else worth noting.
Rules:
- Report only what is visible. If a manoeuvre is announced or described but the hands are not seen doing it, set seen=false.
- If you see none of the manoeuvres, return an empty list.
- Sides are the patient's left and right; use not_applicable for midline steps such as the trachea.
- Zones: upper, middle, lower chest. Do not guess zones you cannot see.
- Times are MM:SS from the start of the full video, not the clip."""


PROMPT_V2 = """You are an OSCE examiner watching a clip from a respiratory examination.
Your only job is to report physical manoeuvres you can SEE the examiner's hands performing.
Ignore everything that is said. An announcement such as "I'm now going to percuss the chest",
an explanation, or a description of what would be done is NEVER evidence that it was done.

A manoeuvre counts as seen only from the first frame where this is visible:
- asterixis: the patient's arms are outstretched with wrists cocked back.
- tracheal_position: the examiner's finger(s) in contact with the suprasternal notch.
- chest_expansion_front / chest_expansion_back: the examiner's hands flat on the patient's lower ribs
  (front or back), and the patient breathes in.
- percussion_front / percussion_back: a finger striking a finger placed on the chest (front or back).
- auscultation_front / auscultation_back: the stethoscope head in contact with the chest (front or back).
Hands moving towards the patient, positioning the patient, or gesturing do not count.
If the hands are hidden, off camera or out of shot, set seen=false even if sounds suggest it happened.
start is the first frame of contact as defined above, not when it was announced.

Sides are the patient's left and right; use not_applicable for asterixis and the trachea.
Zones (percussion and auscultation only): upper = apices and above the nipple line or upper third of
the back; middle = around the nipple line or mid back; lower = below the nipple line or lung bases.
List only zones you saw contact in; do not guess.
Use "other" for anything else worth noting. If you see none of the manoeuvres, return an empty list.
Times are MM:SS from the start of the full video, not the clip."""

PROMPTS = {"obs-v1": PROMPT, "obs-v2": PROMPT_V2}


def mmss(value: str) -> Optional[float]:
    value = (value or "").strip()
    if not value:
        return None
    parts = value.split(":")
    try:
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    except ValueError:
        return None
    return None


@dataclass
class Label:
    video: str
    manoeuvre: str
    present: Optional[bool]
    announce: Optional[float]
    start: Optional[float]
    end: Optional[float]
    sides: str
    zones: List[str] = field(default_factory=list)
    visibility: str = ""


def _col(row: Dict[str, str], prefix: str) -> str:
    for key, value in row.items():
        if key and key.split(" (")[0].strip() == prefix:
            return (value or "").strip()
    return ""


def load_labels(path: Path) -> List[Label]:
    labels = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            present = _col(row, "present").lower()
            labels.append(Label(
                video=_col(row, "video_url"),
                manoeuvre=_col(row, "manoeuvre"),
                present=True if present == "yes" else False if present == "no" else None,
                announce=mmss(_col(row, "announce")),
                start=mmss(_col(row, "start")),
                end=mmss(_col(row, "end")),
                sides=_col(row, "sides").lower(),
                zones=[z.strip() for z in _col(row, "zones").lower().replace(",", "|").split("|") if z.strip()],
                visibility=_col(row, "visibility").lower(),
            ))
    return labels


def load_key() -> str:
    env = Path(".env.local")
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                name, value = line.split("=", 1)
                name = name.strip().lstrip("\\")
                os.environ.setdefault(name, value.strip().strip('"').strip("'"))
    for name in ("GEMINI_API_KEY", "GEMINI_OSCME_API_KEY"):
        if os.environ.get(name):
            return os.environ[name]
    sys.exit("No key found: add GEMINI_API_KEY=... to .env.local in the repository root.")


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    if model not in PRICES:
        return None
    pin, pout = PRICES[model]
    return input_tokens * pin / 1e6 + output_tokens * pout / 1e6


def ask_gemini(client, model: str, url: str, start: float, end: float, prompt_version: str = PROMPT_VERSION):
    """One structured question about one clip. Returns (Answer, input_tokens, output_tokens)."""
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=types.Content(parts=[
            types.Part(
                file_data=types.FileData(file_uri=url),
                video_metadata=types.VideoMetadata(start_offset=f"{int(start)}s", end_offset=f"{int(end)}s"),
            ),
            types.Part(text=PROMPTS[prompt_version]),
        ]),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Answer,
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
        ),
    )
    answer = Answer.model_validate_json(response.text)
    usage = response.usage_metadata
    inp = usage.prompt_token_count or 0
    out = (usage.candidates_token_count or 0) + (getattr(usage, "thoughts_token_count", None) or 0)
    return answer, inp, out
