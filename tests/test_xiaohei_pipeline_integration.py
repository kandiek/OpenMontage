from pathlib import Path

from tools.base_tool import ToolStatus
from tools.graphics.image_selector import ImageSelector


def test_image_selector_builds_xiaohei_prompt_before_provider_routing(monkeypatch):
    selector = ImageSelector()

    class FakeProvider:
        name = "fake_image"
        provider = "fake"
        input_schema = {"properties": {"prompt": {}, "negative_prompt": {}, "aspect_ratio": {}}}
        best_for = ["test"]
        supports = {}

        def get_status(self):
            return ToolStatus.AVAILABLE

        def get_info(self):
            return {"agent_skills": [], "usage_location": "test", "best_for": self.best_for}

        def execute(self, inputs):
            from tools.base_tool import ToolResult
            return ToolResult(success=True, data={"prompt_seen": inputs["prompt"]})

        def estimate_cost(self, inputs):
            return 0.0

    provider = FakeProvider()
    monkeypatch.setattr(selector, "_providers", lambda: [provider])
    monkeypatch.setattr(selector, "_select_best_tool", lambda inputs, candidates, task_context: (provider, None))
    result = selector.execute({
        "prompt": "短视频开头为什么要反常识",
        "visual_style": "xiaohei",
        "xiaohei_preset": "social_video_hook",
        "aspect_ratio": "9:16",
    })

    assert result.success
    prompt = result.data["prompt_seen"]
    assert prompt.startswith("9:16 Ian Xiaohei illustration prompt")
    assert "solid black absurd creature with white dot eyes, thin stick legs, and a blank neutral expression" in prompt
    assert "Xiaohei is not decoration" in prompt
    assert "generated_image" not in result.data


def test_image_selector_saves_xiaohei_prompt_asset_when_no_provider(monkeypatch, tmp_path):
    selector = ImageSelector()
    monkeypatch.setattr(selector, "_providers", lambda: [])

    result = selector.execute({
        "prompt": "把混乱想法变成竖屏短视频",
        "visual_style": "xiaohei",
        "xiaohei_preset": "messy_ideas_to_structured_short_form_video",
        "aspect_ratio": "9:16",
        "prompt_asset_dir": str(tmp_path),
    })

    assert result.success
    assert result.data["generated_image"] is False
    path = Path(result.data["prompt_asset_path"])
    assert path.exists()
    assert path.suffix == ".txt"
    text = path.read_text(encoding="utf-8")
    assert "9:16 Ian Xiaohei illustration prompt" in text
    assert "Do not use cute mascot style" in text


def test_image_selector_accepts_valid_manual_xiaohei_image(monkeypatch, tmp_path):
    selector = ImageSelector()
    monkeypatch.setattr(selector, "_providers", lambda: [])
    image_path = tmp_path / "manual-xiaohei.png"
    image_path.write_bytes(b"not a placeholder image fixture; validation only checks handoff path")

    result = selector.execute({
        "prompt": "手动小黑图",
        "visual_style": "xiaohei",
        "xiaohei_image": str(image_path),
    })

    assert result.success
    assert result.data["image_path"] == str(image_path)
    assert result.data["selected_provider"] == "manual"
    assert result.data["manual_image"] is True
    assert result.data["generated_image"] is False


def test_image_selector_fails_missing_manual_xiaohei_image(monkeypatch, tmp_path):
    selector = ImageSelector()
    monkeypatch.setattr(selector, "_providers", lambda: [])

    result = selector.execute({
        "prompt": "手动小黑图",
        "visual_style": "xiaohei",
        "xiaohei_image": str(tmp_path / "missing.png"),
    })

    assert not result.success
    assert "Xiaohei image not found" in result.error
    assert "assets/xiaohei-images" in result.error


def test_image_selector_fails_unsupported_manual_xiaohei_extension(monkeypatch, tmp_path):
    selector = ImageSelector()
    monkeypatch.setattr(selector, "_providers", lambda: [])
    image_path = tmp_path / "manual-xiaohei.gif"
    image_path.write_bytes(b"gif")

    result = selector.execute({
        "prompt": "手动小黑图",
        "visual_style": "xiaohei",
        "xiaohei_image": str(image_path),
    })

    assert not result.success
    assert "Unsupported Xiaohei image extension" in result.error
    assert ".png" in result.error


def test_manual_xiaohei_image_does_not_call_provider_or_fake_generation(monkeypatch, tmp_path):
    selector = ImageSelector()
    image_path = tmp_path / "manual-xiaohei.webp"
    image_path.write_bytes(b"manual fixture")

    class ExplodingProvider:
        name = "must_not_be_called"
        provider = "fake"

        def get_status(self):
            return ToolStatus.AVAILABLE

        def execute(self, inputs):  # pragma: no cover - should never run
            raise AssertionError("manual Xiaohei image path should not call image providers")

    monkeypatch.setattr(selector, "_providers", lambda: [ExplodingProvider()])

    result = selector.execute({
        "prompt": "手动小黑图",
        "visual_style": "xiaohei",
        "xiaohei_image": str(image_path),
    })

    assert result.success
    assert result.data["generated_image"] is False
    assert "prompt_asset_path" not in result.data
