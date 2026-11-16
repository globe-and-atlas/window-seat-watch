"""Build native Window Seat 0.2.0 store galleries from the verified route captures."""
import json

from PIL import Image

from build_route_preview import ROOT, SHOTS
from build_store_media import verify_frames

SCENES = ("day", "dusk", "night", "rain")
STILLS = (("alpine", "day"), ("sydney", "dusk"), ("london", "night"), ("city", "rain"))


def main():
    output = ROOT / "media/store/0.2.0"
    output.mkdir(exist_ok=True)
    routes = json.loads((ROOT / "assets/routes.json").read_text())
    tour = [slug for _, slug in routes if slug not in ("san_francisco", "countryside")]
    tour.append("countryside")
    opening = [("san_francisco", scene) for scene in SCENES]
    frames = opening + [(slug, SCENES[index % len(SCENES)]) for index, slug in enumerate(tour)]
    durations = [1350, 1250, 1350, 1350] + [900] * (len(tour) - 1) + [1150]
    for platform, size in (("emery", (200, 228)), ("gabbro", (260, 260))):
        captures = {}
        for route, scene in dict.fromkeys(frames + list(STILLS)):
            with Image.open(SHOTS / f"{platform}-{route}-{scene}.png") as screenshot:
                assert screenshot.size == size
                captures[route, scene] = screenshot.convert("RGB")
        animation = output / f"{platform}_01_route-tour.gif"
        images = [captures[key] for key in frames]
        images[0].save(animation, save_all=True, append_images=images[1:],
                       duration=durations, loop=0, disposal=2, optimize=True)
        verify_frames(animation, images)
        for index, (route, scene) in enumerate(STILLS, 2):
            path = output / f"{platform}_{index:02d}_{route}-{scene}.gif"
            frame = captures[route, scene]
            frame.save(path, optimize=True)
            verify_frames(path, [frame])
    (output / "sequence.json").write_text(json.dumps(
        [{"route": route, "scene": scene, "duration_ms": duration}
         for (route, scene), duration in zip(frames, durations, strict=True)], indent=2
    ) + "\n")


if __name__ == "__main__":
    main()
