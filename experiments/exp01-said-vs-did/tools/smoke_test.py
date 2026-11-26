"""Smoke test: ask Gemini one structured question about one public demo video.

Checks that the API key, paid tier, YouTube URL input, clipping and structured output all work.
It prints what Gemini observed, its token usage and an estimated cost. It never prints the key.

Usage (from the repository root):
    python experiments/exp01-said-vs-did/tools/smoke_test.py [youtube_url] [--model MODEL] [--end SECONDS]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

DEFAULT_URL = "https://www.youtube.com/watch?v=Y48np9EyzBI"

# USD per million tokens (Gemini API, paid tier, standard rates, checked 2026-11-26). Update if pricing changes.
# Gemini 2.5 models are no longer available to new API users.
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
    sides: Literal["left", "right", "both", "unclear"]
    zones: list[Literal["upper", "middle", "lower"]]
    note: str = Field(description="One short sentence on what is visible")


class Answer(BaseModel):
    observations: list[Observation]


PROMPT = """You are observing a demonstration of a respiratory examination.
List each of these manoeuvres that you can SEE being performed in this clip:
asterixis, tracheal_position, chest_expansion_front, percussion_front, auscultation_front,
chest_expansion_back, percussion_back, auscultation_back. Use "other" for anything else worth noting.
Rules: report only what is visible. If something is said but not seen, set seen=false.
Sides are the patient's left and right. Do not guess zones you cannot see."""


def load_key() -> str:
    env = Path(".env.local")
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                name, value = line.split("=", 1)
                name = name.strip().lstrip("\\")  # tolerate a stray backslash left by rich-text editors
                os.environ.setdefault(name, value.strip().strip('"').strip("'"))
    for name in ("GEMINI_API_KEY", "GEMINI_OSCME_API_KEY"):
        if os.environ.get(name):
            return os.environ[name]
    sys.exit("No key found: add GEMINI_API_KEY=... to .env.local in the repository root.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs="?", default=DEFAULT_URL)
    parser.add_argument("--model", default="gemini-3.5-flash-lite")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=300, help="seconds; keeps the first test small")
    args = parser.parse_args()

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=load_key())
    response = client.models.generate_content(
        model=args.model,
        contents=types.Content(parts=[
            types.Part(
                file_data=types.FileData(file_uri=args.url),
                video_metadata=types.VideoMetadata(start_offset=f"{args.start}s", end_offset=f"{args.end}s"),
            ),
            types.Part(text=PROMPT),
        ]),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Answer,
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
        ),
    )

    answer = Answer.model_validate_json(response.text)  # fails loudly on invalid output
    print(json.dumps(answer.model_dump(), indent=2))

    usage = response.usage_metadata
    inp = usage.prompt_token_count or 0
    out = (usage.candidates_token_count or 0) + (getattr(usage, "thoughts_token_count", None) or 0)
    print(f"\nmodel={args.model} window={args.start}-{args.end}s input_tokens={inp} output_tokens={out}")
    if args.model in PRICES:
        pin, pout = PRICES[args.model]
        print(f"estimated cost if billed: ${inp * pin / 1e6 + out * pout / 1e6:.4f} "
              "(YouTube input is free during preview)")


if __name__ == "__main__":
    main()
