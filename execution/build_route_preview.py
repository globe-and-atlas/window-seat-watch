"""Compose the route galleries from captured native emulator frames."""
import json

from PIL import Image, ImageDraw, ImageFont

from build_preview import BOLD, FONT, MEDIA, ROOT

SHOTS = ROOT / ".tmp/native/route-shots"
PLATFORMS = (("emery", "Pebble Time 2"), ("gabbro", "Pebble Round 2"))
SCENES = (("day", "Day"), ("dusk", "Dusk"), ("night", "Night"), ("rain", "Rain"))
BACKGROUND = "#171c24"
TEXT = "#fbedd2"
SECONDARY = "#b7c3d4"


def paste_screen(canvas, platform, route, scene, center, top):
    with Image.open(SHOTS / f"{platform}-{route}-{scene}.png") as screenshot:
        position = (center - screenshot.width // 2, top)
        mask = None
        if platform == "gabbro":
            mask = Image.new("1", screenshot.size)
            ImageDraw.Draw(mask).ellipse((0, 0, screenshot.width - 1, screenshot.height - 1), fill=1)
        canvas.paste(screenshot, position, mask)


def gallery(platform, device, routes, title_font, label_font):
    columns, cell_width = 5, 282
    cell_height = 272 if platform == "emery" else 304
    rows = (len(routes) + columns - 1) // columns
    width = columns * cell_width
    canvas = Image.new("RGB", (width, rows * cell_height + 72), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((width // 2, 32), f"Window Seat · {device}", font=title_font,
              anchor="mm", fill=TEXT)
    for index, (label, route) in enumerate(routes):
        row, column = divmod(index, columns)
        routes_in_row = min(columns, len(routes) - row * columns)
        center = (width - routes_in_row * cell_width) // 2 + column * cell_width + cell_width // 2
        top = 70 + row * cell_height
        paste_screen(canvas, platform, route, "dusk", center, top)
        draw.text((center, top + cell_height - 22), label, font=label_font,
                  anchor="mm", fill=TEXT)
    canvas.save(MEDIA / f"routes-{platform}.png", optimize=True)


def scene_comparison(title_font, label_font):
    canvas = Image.new("RGB", (1152, 664), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((576, 28), "Window Seat · San Francisco", font=title_font,
              anchor="mm", fill=TEXT)
    for row, (platform, device) in enumerate(PLATFORMS):
        top = (110, 376)[row]
        draw.text((576, top - 20), device, font=label_font, anchor="mm", fill=SECONDARY)
        for column, (scene, label) in enumerate(SCENES):
            center = 144 + column * 288
            if not row:
                draw.text((center, 62), label, font=label_font, anchor="mm", fill=TEXT)
            paste_screen(canvas, platform, "san_francisco", scene, center, top)
    canvas.save(MEDIA / "route-scenes.png", optimize=True)


def main():
    routes = json.loads((ROOT / "assets/routes.json").read_text())
    title_font = ImageFont.truetype(str(BOLD), 28)
    label_font = ImageFont.truetype(str(FONT), 18)
    for platform, device in PLATFORMS:
        gallery(platform, device, routes, title_font, label_font)
    scene_comparison(title_font, label_font)


if __name__ == "__main__":
    main()
