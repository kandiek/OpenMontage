import pytest

from lib.xiaohei_prompt_builder import (
    PRESETS,
    XIAOHEI_STYLE_LOCK,
    build_xiaohei_prompt,
    build_xiaohei_prompt_template,
    list_xiaohei_presets,
)


REQUIRED_PHRASES = [
    "pure white background",
    "thin black wobbly hand-drawn line art",
    "solid black Xiaohei creature",
    "white dot eyes",
    "thin stick legs",
    "blank neutral expression",
    "sparse red/orange/blue handwritten Chinese annotations",
]


def test_all_required_presets_exist():
    assert set(list_xiaohei_presets()) == {
        "messy_ideas_to_structured_short_form_video",
        "parable_explanation",
        "news_quote_explanation",
        "social_video_hook",
    }


def test_prompt_preserves_style_lock_for_every_preset():
    for preset in PRESETS:
        prompt = build_xiaohei_prompt(concept="测试概念", preset=preset)
        for phrase in REQUIRED_PHRASES:
            assert phrase in prompt
        assert "solid black absurd creature with white dot eyes, thin stick legs, and a blank neutral expression" in prompt
        assert "Xiaohei is not decoration" in prompt


def test_supported_aspect_ratio_override():
    prompt = build_xiaohei_prompt(
        concept="一条新闻金句被拆开解释",
        preset="news_quote_explanation",
        aspect_ratio="9:16",
    )
    assert prompt.startswith("9:16 Ian Xiaohei illustration prompt")


def test_invalid_aspect_ratio_rejected():
    with pytest.raises(ValueError, match="16:9 and 9:16"):
        build_xiaohei_prompt(
            concept="bad ratio",
            preset="social_video_hook",
            aspect_ratio="1:1",  # type: ignore[arg-type]
        )


def test_template_is_serializable_and_includes_style_lock():
    template = build_xiaohei_prompt_template("parable_explanation")
    assert template["default_aspect_ratio"] == "16:9"
    assert template["supported_aspect_ratios"] == ["16:9", "9:16"]
    assert template["style_lock"] == list(XIAOHEI_STYLE_LOCK)
