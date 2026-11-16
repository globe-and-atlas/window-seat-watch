"""Compose native scene captures for review at one screen pixel per image pixel."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
BOLD = FONT.with_name("Arial Bold.ttf")


def main():
    canvas = Image.new("RGB", (1176, 686), "#171c24")
    draw = ImageDraw.Draw(canvas)
    draw.text((588, 26), "Window Seat", font=ImageFont.truetype(str(BOLD), 28),
              anchor="mm", fill="#fbedd2")
    body = ImageFont.truetype(str(FONT), 14)
    cases = [("day", "Day"), ("dusk", "Dusk"), ("rain", "Rain"), ("rain-night-24", "Rain at night")]
    for column, (_, title) in enumerate(cases):
        draw.text((153 + 290 * column, 64), title, font=body, anchor="mm", fill="#fbedd2")
    for platform, top, label in [("emery", 103, "Pebble Time 2"), ("gabbro", 375, "Pebble Round 2")]:
        draw.text((588, top - 14), label, font=body, anchor="mm", fill="#b7c3d4")
        for column, (case, _) in enumerate(cases):
            with Image.open(MEDIA / f"{platform}-{case}.png") as screenshot:
                pos = (153 + 290 * column - screenshot.width // 2, top)
                if platform == "gabbro":
                    mask = Image.new("1", screenshot.size)
                    ImageDraw.Draw(mask).ellipse((0, 0, screenshot.width - 1, screenshot.height - 1), fill=1)
                    canvas.paste(screenshot, pos, mask)
                else:
                    canvas.paste(screenshot, pos)
    draw.text((588, 664), "Native emulator captures with sample weather", font=body,
              anchor="mm", fill="#b7c3d4")
    canvas.save(MEDIA / "native-comparison.png")


if __name__ == "__main__":
    main()
