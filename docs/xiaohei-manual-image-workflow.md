# Manual Xiaohei Image Workflow

OpenMontage stays the pipeline controller for Xiaohei visuals, but it does **not** need an image-generation API key for this workflow. It creates locked Xiaohei prompt files, you manually create the image in ChatGPT Images, then OpenMontage/Remotion consumes the saved local image.

## Folder convention

- `assets/xiaohei-prompts/` — generated Xiaohei prompt `.txt` files.
- `assets/xiaohei-images/` — manually generated `.png`, `.webp`, `.jpg`, or `.jpeg` images.

Do not commit fake image files or placeholder images. Save only images you manually created and want a composition to use.

## Steps

1. Generate a locked Xiaohei prompt:

   ```bash
   python scripts/xiaohei_prompt.py "Topic: why short videos need a counterintuitive hook" \
     --preset social_video_hook \
     --aspect-ratio 9:16
   ```

2. Open the emitted file in `assets/xiaohei-prompts/` and copy the full prompt.
3. Paste the prompt into ChatGPT Images and generate the image manually.
4. Download the result as PNG, WebP, JPG, or JPEG.
5. Place the file in `assets/xiaohei-images/`, for example:

   ```text
   assets/xiaohei-images/counterintuitive-hook.png
   ```

6. Validate and hand the image to OpenMontage/Remotion:

   ```bash
   python scripts/xiaohei_prompt.py --xiaohei-image assets/xiaohei-images/counterintuitive-hook.png
   ```

   Pipeline/tool callers can pass the same path as `xiaohei_image` to `image_selector`. The selector validates the file and returns it as a manual asset without calling an image-generation provider.

## Full example

**Topic:** “Why short videos need a counterintuitive hook.”

**Prompt generation:**

```bash
python scripts/xiaohei_prompt.py "短视频开头为什么要反常识" \
  --preset social_video_hook \
  --aspect-ratio 9:16
```

**Generated Xiaohei prompt:** saved under `assets/xiaohei-prompts/`. The prompt preserves the Xiaohei Style Lock: pure white background, thin black wobbly hand-drawn line art, lots of whitespace, sparse red/orange/blue handwritten Chinese annotations, and Xiaohei as the solid black absurd creature with white dot eyes, thin stick legs, and a blank neutral expression actively performing the core action.

**Manual ChatGPT image:** paste the prompt into ChatGPT Images, generate the illustration, and download it.

**Saved image:**

```text
assets/xiaohei-images/counterintuitive-hook.png
```

**OpenMontage/Remotion input:**

```python
from tools.graphics.image_selector import ImageSelector

result = ImageSelector().execute({
    "prompt": "短视频开头为什么要反常识",
    "visual_style": "xiaohei",
    "xiaohei_image": "assets/xiaohei-images/counterintuitive-hook.png",
})

# Use result.data["image_path"] in the scene plan, asset manifest, or Remotion props.
```

If the path does not exist, OpenMontage fails clearly. If the extension is not `.png`, `.webp`, `.jpg`, or `.jpeg`, OpenMontage fails clearly. No `OPENAI_API_KEY` is required.
