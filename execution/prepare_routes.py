"""Fit route artwork into the shared carriage and generate native resource metadata."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from prepare_art import PALETTE, ROOT

SOURCE = ROOT / "assets/source/routes"
WATCHFACE = ROOT / "watchface"
ROUTES = json.loads((ROOT / "assets/routes.json").read_text())
TARGETS = {"emery": (200, 228), "gabbro": (260, 260)}


def panels(name):
    with Image.open(SOURCE / name) as image:
        image = image.convert("RGB")
        width, height = image.size
        return [image.crop((width * col // 3, height * row // 2,
                            width * (col + 1) // 3, height * (row + 1) // 2))
                for row in range(2) for col in range(3)]


def landscapes():
    # Inside edges of the glass in the approved, labeled concept sheet.
    with Image.open(SOURCE / "approved.png") as approved:
        four = [approved.convert("RGB").crop(box) for box in
                ((238, 176, 554, 406), (806, 176, 1124, 406),
                 (238, 691, 554, 922), (806, 691, 1124, 922))]
    return four + panels("landmarks-1.png") + panels("landmarks-2.png")


def glass_mask(width, height):
    mask = Image.new("L", (width, height))
    box = (round(width * .165), round(height * .108),
           round(width * .887), round(height * .850))
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=round(width * .085), fill=255)
    return box, mask


def main():
    art = landscapes()
    assert len(art) == len(ROUTES) - 1
    package_path = WATCHFACE / "package.json"
    package = json.loads(package_path.read_text())
    resources = package["pebble"]["resources"]
    resources["media"] = [item for item in resources["media"] if "_ROUTE_" not in item["name"]]
    header = ["/* Generated from assets/routes.json by execution/prepare_routes.py. */",
              "#pragma once", f"#define WS_ROUTE_COUNT {len(ROUTES)}"]
    index = {}
    for platform, (width, height) in TARGETS.items():
        base = Image.open(WATCHFACE / f"resources/images/{platform}-dusk.png").convert("RGB")
        box, mask = glass_mask(*base.size)
        left, top, right, bottom = box
        mask = mask.crop((left, top, right + 1, bottom + 1))
        ids = []
        for (_, slug), landscape in zip(ROUTES[1:], art, strict=True):
            route = base.copy()
            view = ImageOps.fit(landscape, mask.size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.15))
            view = view.quantize(palette=PALETTE, dither=Image.Dither.NONE).convert("RGB")
            route.paste(view, (left, top), mask)
            resource = f"{platform.upper()}_ROUTE_{slug.upper()}"
            filename = f"images/{platform}-route-{slug}.png"
            dest = WATCHFACE / "resources" / filename
            route.save(dest, optimize=True)
            index[filename] = hashlib.sha256(dest.read_bytes()).hexdigest()
            ids.append("RESOURCE_ID_" + resource)
            resources["media"].append({"type": "bitmap", "name": resource, "file": filename,
                                        "memoryFormat": "8Bit", "storageFormat": "png",
                                        "targetPlatforms": [platform]})
        header += ["#ifdef PBL_ROUND" if platform == "gabbro" else "#ifndef PBL_ROUND",
                   "static const uint32_t route_ids[] = {", "    " + ",\n    ".join(ids), "};",
                   "static const uint16_t glass_spans[][2] = {"]
        # A shared pixel mask ensures tint and raindrops never cover the interior.
        full_mask = Image.new("L", base.size)
        full_mask.paste(mask, (left, top))
        for y in range(base.height):
            span = full_mask.crop((0, y, width, y + 1)).getbbox()
            header.append(f"    {{{span[0]}, {span[2]}}}," if span else "    {0, 0},")
        header += ["};", "#endif"]
    package_path.write_text(json.dumps(package, indent=2) + "\n")
    (WATCHFACE / "src/c/route_resources.h").write_text("\n".join(header) + "\n")
    (WATCHFACE / "src/pkjs/routes.js").write_text(
        "/* Generated from assets/routes.json. */\nmodule.exports = " +
        json.dumps([label for label, _ in ROUTES]) + ";\n")
    work = ROOT / ".tmp"
    work.mkdir(exist_ok=True)
    (work / "route-resources.json").write_text(json.dumps(index, indent=2) + "\n")


if __name__ == "__main__":
    main()
