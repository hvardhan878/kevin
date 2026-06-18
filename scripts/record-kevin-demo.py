#!/usr/bin/env python3
"""Build kevin demo GIF + transcript from crafted terminal script."""
from __future__ import annotations

import json
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_GIF = ROOT / "assets" / "kevin-demo.gif"
OUT_JSON = ROOT / "assets" / "kevin-demo.transcript.json"

W, H = 920, 540
PAD = 20
LINE_H = 18
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
FONT_SIZE = 13
MAX_COLS = 96

BG = (30, 30, 46)
FG = (205, 214, 244)
GREEN = (166, 227, 161)
CYAN = (137, 220, 235)
YELLOW = (249, 226, 175)
DIM = (108, 112, 134)

# kevin: illustrative demo — matches README email-validator example
DEMO = [
    {
        "prompt": (
            "Add email validation: AbstractFactory, Strategy pattern, Redis cache, "
            "full test suite, ARCHITECTURE.md"
        ),
        "response": (
            "Stop.\n\n"
            "You want check email or resume say \"designed enterprise validation platform\"?\n\n"
            '  "@" in email and "." in email.split("@")[-1]\n\n'
            "That it. Real validation = user click confirmation link.\n\n"
            "AbstractFactory for ONE check? Kevin spill chili on that."
        ),
    },
    {
        "prompt": "ok. javascript function.",
        "response": (
            "function validEmail(e) {\n"
            "  return e.includes('@') && e.split('@')[1]?.includes('.');\n"
            "}\n"
            "// kevin: naive check. real validation is the confirmation email."
        ),
    },
    {
        "prompt": "write 500 words on why Strategy pattern was the right choice",
        "response": (
            "Kevin pick one line. Not Strategy pattern.\n\n"
            "You want essay on architecture Kevin delete. Diff is proof."
        ),
    },
]


@dataclass
class Line:
    text: str
    color: tuple[int, int, int] = FG


@dataclass
class Frame:
    lines: list[Line]
    duration_ms: int


def wrap(text: str, prefix: str = "") -> list[str]:
    width = max(20, MAX_COLS - len(prefix))
    out: list[str] = []
    for raw in text.splitlines() or [""]:
        if not raw.strip():
            out.append(prefix.rstrip())
            continue
        chunks = textwrap.wrap(raw, width=width, break_long_words=False) or [raw]
        for chunk in chunks:
            out.append(prefix + chunk)
    return out or [prefix.rstrip()]


def add_prompt(frames: list[Frame], lines: list[Line], prompt: str, *, first: bool) -> None:
    if first:
        lines.append(Line("$ claude /kevin", CYAN))
        frames.append(Frame([Line(l.text, l.color) for l in lines], 600))
    for i, row in enumerate(wrap(prompt, "> ")):
        lines.append(Line(row, GREEN))
        frames.append(Frame([Line(l.text, l.color) for l in lines], 400 if i else 500))


def add_response(frames: list[Frame], lines: list[Line], response: str) -> None:
    lines.append(Line("", FG))
    lines.append(Line("kevin", YELLOW))
    frames.append(Frame([Line(l.text, l.color) for l in lines], 350))
    wrapped = wrap(response)
    shown: list[str] = []
    for row in wrapped:
        shown.append(row)
        preview = lines + [Line(r, FG) for r in shown]
        frames.append(Frame([Line(l.text, l.color) for l in preview], 90))
    lines.extend([Line(r, FG) for r in wrapped])
    frames.append(Frame([Line(l.text, l.color) for l in lines], 1800))


def render(lines: list[Line]) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    max_lines = (H - 2 * PAD) // LINE_H
    y = PAD
    for line in lines[-max_lines:]:
        draw.text((PAD, y), line.text, fill=line.color, font=font)
        y += LINE_H
    return img


def build() -> None:
    frames: list[Frame] = []
    lines: list[Line] = []
    for i, turn in enumerate(DEMO):
        add_prompt(frames, lines, turn["prompt"], first=i == 0)
        add_response(frames, lines, turn["response"])

    images = [render(f.lines) for f in frames]
    durations = [f.duration_ms for f in frames]
    durations[-1] = 2500
    OUT_GIF.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        OUT_GIF,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    transcript = {
        "demo": True,
        "note": "Illustrative terminal demo. Matches README email-validator example.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "turns": DEMO,
    }
    OUT_JSON.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_GIF} ({OUT_GIF.stat().st_size // 1024} KB)")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    build()
