"""Reusable Xiaohei prompt builder for OpenMontage visual assets.

The builder intentionally creates prompt text only. It does not generate or
pretend to create image files; generation remains the responsibility of the
configured image provider selected by the pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AspectRatio = Literal["16:9", "9:16"]
PresetName = Literal[
    "messy_ideas_to_structured_short_form_video",
    "parable_explanation",
    "news_quote_explanation",
    "social_video_hook",
]

XIAOHEI_STYLE_LOCK: tuple[str, ...] = (
    "pure white background",
    "thin black wobbly hand-drawn line art",
    "lots of whitespace",
    "solid black Xiaohei creature",
    "white dot eyes",
    "thin stick legs",
    "blank neutral expression",
    "sparse red/orange/blue handwritten Chinese annotations",
)

XIAOHEI_NEGATIVE_STYLE = (
    "Do not use cute mascot style, colorful cartoon, anime, Pixar, Disney, "
    "glossy vector illustration, polished corporate illustration, PPT infographic style, "
    "realistic humans, shadows, gradients, paper texture, beige background, excessive text, "
    "or any replacement for Xiaohei."
)


@dataclass(frozen=True)
class XiaoheiPreset:
    """A reusable Xiaohei prompt preset."""

    name: PresetName
    title: str
    default_aspect_ratio: AspectRatio
    metaphor_frame: str
    core_action_template: str
    annotation_suggestions: tuple[str, ...]


PRESETS: dict[PresetName, XiaoheiPreset] = {
    "messy_ideas_to_structured_short_form_video": XiaoheiPreset(
        name="messy_ideas_to_structured_short_form_video",
        title="messy ideas to structured short-form video",
        default_aspect_ratio="9:16",
        metaphor_frame="a chaotic thought cloud being squeezed into a clean vertical video spine",
        core_action_template=(
            "Xiaohei actively gathers scattered messy idea scraps and threads them into "
            "a simple short-form video sequence: hook, turn, payoff"
        ),
        annotation_suggestions=("乱想法", "钩子", "转折", "收束"),
    ),
    "parable_explanation": XiaoheiPreset(
        name="parable_explanation",
        title="parable explanation",
        default_aspect_ratio="16:9",
        metaphor_frame="a small absurd fable scene where one concrete object reveals a larger lesson",
        core_action_template=(
            "Xiaohei actively performs the parable's central action so the lesson emerges "
            "from the scene instead of from a diagram"
        ),
        annotation_suggestions=("表层故事", "真正的坑", "寓意"),
    ),
    "news_quote_explanation": XiaoheiPreset(
        name="news_quote_explanation",
        title="news quote explanation",
        default_aspect_ratio="16:9",
        metaphor_frame="a quoted sentence treated like a heavy object that must be weighed, opened, or decoded",
        core_action_template=(
            "Xiaohei actively examines the quoted line with a simple absurd tool, separating "
            "what was said from what it means"
        ),
        annotation_suggestions=("原话", "语境", "真正意思"),
    ),
    "social_video_hook": XiaoheiPreset(
        name="social_video_hook",
        title="social video hook",
        default_aspect_ratio="9:16",
        metaphor_frame="a tiny visual trapdoor that makes the viewer stop scrolling",
        core_action_template=(
            "Xiaohei actively triggers a surprising hook mechanism that turns a familiar "
            "problem into an immediate question"
        ),
        annotation_suggestions=("停一下", "反常识", "想知道"),
    ),
}


def list_xiaohei_presets() -> list[str]:
    """Return supported Xiaohei preset names."""

    return list(PRESETS)


def build_xiaohei_prompt(
    *,
    concept: str,
    preset: PresetName | str,
    aspect_ratio: AspectRatio | None = None,
    core_action: str | None = None,
    chinese_annotations: list[str] | tuple[str, ...] | None = None,
    context: str | None = None,
) -> str:
    """Build a Xiaohei image prompt for an OpenMontage pipeline asset.

    Args:
        concept: The specific idea, quote, hook, scene beat, or judgment to visualize.
        preset: One of the reusable Xiaohei preset names.
        aspect_ratio: Optional override. Defaults to the preset's ratio.
        core_action: Optional explicit action Xiaohei performs. If omitted, the preset action is used.
        chinese_annotations: Optional sparse Chinese labels; defaults to preset suggestions.
        context: Optional extra pipeline context, such as narration beat or source quote.

    Returns:
        A provider-neutral prompt string that preserves the Xiaohei style lock.
    """

    if preset not in PRESETS:
        valid = ", ".join(list_xiaohei_presets())
        raise ValueError(f"Unknown Xiaohei preset '{preset}'. Valid presets: {valid}")

    selected = PRESETS[preset]  # type: ignore[index]
    ratio = aspect_ratio or selected.default_aspect_ratio
    if ratio not in ("16:9", "9:16"):
        raise ValueError("Xiaohei prompts support only 16:9 and 9:16 aspect ratios")

    annotations = tuple(chinese_annotations or selected.annotation_suggestions)
    sparse_annotations = "、".join(annotations[:5])
    action = core_action or selected.core_action_template

    context_line = f"Pipeline context: {context}." if context else ""

    style_lock = "; ".join(XIAOHEI_STYLE_LOCK)
    return " ".join(
        part
        for part in (
            f"{ratio} Ian Xiaohei illustration prompt for OpenMontage.",
            f"Concept: {concept}.",
            context_line,
            f"Use one core metaphor only: {selected.metaphor_frame}.",
            f"Core action: {action}.",
            "Xiaohei must be the solid black absurd creature with white dot eyes, thin stick legs, and a blank neutral expression.",
            f"Preserve exactly this visual language: {style_lock}.",
            f"Use only sparse handwritten Chinese annotations in red, orange, and blue, such as: {sparse_annotations}.",
            "Xiaohei is not decoration; Xiaohei actively performs the core action in the image.",
            "Keep the composition calm, clever, absurd, clean, crisp, and mostly empty.",
            XIAOHEI_NEGATIVE_STYLE,
        )
        if part
    )


def build_xiaohei_prompt_template(preset: PresetName | str) -> dict[str, object]:
    """Return a serializable prompt-template descriptor for pipeline UIs or docs."""

    if preset not in PRESETS:
        valid = ", ".join(list_xiaohei_presets())
        raise ValueError(f"Unknown Xiaohei preset '{preset}'. Valid presets: {valid}")
    selected = PRESETS[preset]  # type: ignore[index]
    return {
        "name": selected.name,
        "title": selected.title,
        "default_aspect_ratio": selected.default_aspect_ratio,
        "supported_aspect_ratios": ["16:9", "9:16"],
        "style_lock": list(XIAOHEI_STYLE_LOCK),
        "metaphor_frame": selected.metaphor_frame,
        "core_action_template": selected.core_action_template,
        "annotation_suggestions": list(selected.annotation_suggestions),
    }
