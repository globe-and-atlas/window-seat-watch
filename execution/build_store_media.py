"""Prepare lossless store previews from the final native capture matrix."""
from pathlib import Path
from PIL import Image

MEDIA = Path(__file__).resolve().parents[1] / "media"
SCENES = ("day", "dusk", "night-12", "rain")


def verify_frames(path, expected):
    with Image.open(path) as gif:
        assert gif.n_frames == len(expected), path
        for index, frame in enumerate(expected):
            gif.seek(index)
            assert gif.size == frame.size and gif.convert("RGB").tobytes() == frame.tobytes(), path


def main():
    output = MEDIA / "store"
    output.mkdir(exist_ok=True)
    for platform, size in (("emery", (200, 228)), ("gabbro", (260, 260))):
        frames = []
        for scene in SCENES:
            with Image.open(MEDIA / f"{platform}-{scene}.png") as source:
                assert source.size == size
                frames.append(source.convert("RGB"))
        animation = output / f"{platform}_01_scenes.gif"
        frames[0].save(animation, save_all=True, append_images=frames[1:],
                       duration=[1650, 1850, 1650, 1850], loop=0, disposal=2, optimize=False)
        verify_frames(animation, frames)
        for index, (scene, frame) in enumerate(zip(SCENES, frames, strict=True), 2):
            still = output / f"{platform}_{index:02d}_{scene}.gif"
            frame.save(still, optimize=False)
            verify_frames(still, [frame])
    with Image.open(MEDIA.parent / "watchface/resources/images/gabbro-dusk.png") as source:
        crop = source.crop((2, 0, 185, 183))
        for name, size in (("small", 80), ("large", 144)):
            crop.resize((size, size), Image.Resampling.LANCZOS).save(output / f"icon-{name}.png")


if __name__ == "__main__":
    main()
