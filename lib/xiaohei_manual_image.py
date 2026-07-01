"""Validation helpers for manually supplied Xiaohei image assets."""

from __future__ import annotations

from pathlib import Path

SUPPORTED_XIAOHEI_IMAGE_EXTENSIONS = frozenset({".png", ".webp", ".jpg", ".jpeg"})


def validate_xiaohei_image_path(path: str | Path) -> Path:
    """Validate a manually generated Xiaohei image path.

    OpenMontage intentionally does not create placeholder or fake Xiaohei image
    files. The caller must place a real image exported from a manual image tool
    (for example ChatGPT Images) in the repository and pass that path in.
    """

    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(
            f"Xiaohei image not found: {image_path}. Generate the image manually, "
            "then place it under assets/xiaohei-images/ and pass that file path."
        )
    if not image_path.is_file():
        raise ValueError(f"Xiaohei image path is not a file: {image_path}")
    if image_path.suffix.lower() not in SUPPORTED_XIAOHEI_IMAGE_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_XIAOHEI_IMAGE_EXTENSIONS))
        raise ValueError(
            f"Unsupported Xiaohei image extension '{image_path.suffix}'. "
            f"Supported extensions: {supported}."
        )
    return image_path
