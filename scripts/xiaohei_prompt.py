#!/usr/bin/env python3
"""Create a Xiaohei prompt asset from a topic without generating an image."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.xiaohei_manual_image import validate_xiaohei_image_path
from lib.xiaohei_prompt_builder import build_xiaohei_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Xiaohei prompt asset from a topic.")
    parser.add_argument("topic", nargs="?", help="Topic, hook, quote, or idea to visualize")
    parser.add_argument("--aspect-ratio", default="9:16", choices=["9:16", "16:9"])
    parser.add_argument("--preset", default="social_video_hook")
    parser.add_argument("--output-dir", default="assets/xiaohei-prompts")
    parser.add_argument(
        "--xiaohei-image",
        help=(
            "Validate a manually generated Xiaohei image path (PNG/WebP/JPG/JPEG) "
            "for OpenMontage/Remotion handoff. Does not generate images."
        ),
    )
    args = parser.parse_args()

    if args.xiaohei_image:
        try:
            image_path = validate_xiaohei_image_path(args.xiaohei_image)
        except (FileNotFoundError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        print(image_path)
        return

    if not args.topic:
        parser.error("topic is required unless --xiaohei-image is used")

    prompt = build_xiaohei_prompt(
        concept=args.topic,
        preset=args.preset,
        aspect_ratio=args.aspect_ratio,  # type: ignore[arg-type]
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in args.topic).strip("-")[:60] or "xiaohei-prompt"
    path = output_dir / f"{slug}.txt"
    path.write_text(prompt + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
