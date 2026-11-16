"""Prepare native display resources from the approved two-panel carriage art."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCENES = ("day", "dusk", "night", "rain_day", "rain_dusk", "rain_night")
LEVELS = (0, 85, 170, 255)
PALETTE = Image.new("P", (1, 1))
RGB = [channel for r in LEVELS for g in LEVELS for b in LEVELS for channel in (r, g, b)]
PALETTE.putpalette(RGB + [0] * (768 - len(RGB)))


def light_scene(image, phase):
    if phase == "dusk":
        return image
    width, height = image.size
    result = image.copy()
    pixels = result.load()
    for y in range(height):
        for x in range(width):
            nx, ny = x / width, y / height
            r, g, b = pixels[x, y]
            glass = 0.16 < nx < 0.89 and 0.065 < ny < 0.59
            if not glass:
                continue
            if phase == "day":
                # Cool the sky while retaining the brass and warm cabin lights.
                if b >= r or ny < 0.44:
                    pixels[x, y] = (min(255, int(r * .70 + 25)),
                                    min(255, int(g * .80 + 65)),
                                    min(255, int(b * .76 + 75)))
            elif not (ny > 0.46 and r > 175 and g > 100 and r > b * 1.4):
                pixels[x, y] = (int(r * .38), int(g * .48), min(255, int(b * .80 + 12)))
    return result


def main():
    source = Image.open(ROOT / "assets/source/carriage.png").convert("RGB")
    width, height = source.size
    for target, size in (("emery", (200, 228)), ("gabbro", (260, 260))):
        for scene in SCENES:
            wet = scene.startswith("rain_")
            phase = scene.removeprefix("rain_")
            left = width // 2 if wet else 0
            panel = source.crop((left, 0, left + width // 2, height))
            panel = panel.resize(size, Image.Resampling.LANCZOS)
            panel = light_scene(panel, phase)
            # The C renderer draws the clock panel separately.
            panel = panel.crop((0, 0, size[0], int(size[1] * .705)))
            panel.quantize(palette=PALETTE, dither=Image.Dither.NONE).convert("RGB").save(
                ROOT / f"watchface/resources/images/{target}-{scene}.png"
            )


if __name__ == "__main__":
    main()
