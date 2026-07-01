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
