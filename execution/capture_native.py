"""Serial native SDK captures with foreground, placement, and persistence checks."""
from pathlib import Path
import argparse,json,re,shutil,socket,subprocess,time
from datetime import datetime, timedelta
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.tmp/native'

def command(args):
 result=subprocess.run(args,cwd=ROOT/'watchface',capture_output=True,text=True,timeout=100)
 with (OUT/'emulator.log').open('a') as log:log.write(result.stdout+result.stderr)
 if result.returncode:raise RuntimeError(f'{args[:3]} failed; see .tmp/native/emulator.log')

def monitors():
 found={}
 result=subprocess.run(['ps','-axo','pid,comm,args'],capture_output=True,text=True,check=True)
 for line in result.stdout.splitlines():
  if re.match(r'^\s*\d+\s+qemu-pebble\s',line) and '/Pebble SDK/' in line:
   match=re.search(r'-monitor tcp::(\d+)',line)
   if match:found[int(line.split()[0])]=int(match.group(1))
 return found

def close(port):
 with socket.create_connection(('localhost',port),timeout=5) as sock:sock.recv(65536);sock.sendall(b'quit\n')

def capture(peak=255):
 values=monitors()
 if len(values)!=1:raise RuntimeError('Expected one owned SDK emulator')
 path=OUT/'native.ppm';path.unlink(missing_ok=True)
 with socket.create_connection(('localhost',next(iter(values.values()))),timeout=5) as sock:
  sock.recv(65536);sock.sendall(f'screendump "{path}"\n'.encode());deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   sock.recv(65536)
   try:im=Image.open(path).convert('RGB');break
   except (OSError,FileNotFoundError):continue
  else:raise TimeoutError('Native screendump incomplete')
 maximum=max(max(pixel) for pixel in im.get_flattened_data());im=im.point(lambda channel:round(channel/max(maximum,1)*peak/85)*85);path.unlink(missing_ok=True);return im

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["emery", "gabbro"], required=True)
    parser.add_argument("--reset-emulator", action="store_true")
    parser.add_argument("--routes", action="store_true")
    parser.add_argument("--route-nights-only", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    platform = args.platform
    width, height = (200, 228) if platform == "emery" else (260, 260)
    if monitors():
        raise RuntimeError("An emulator is already active. Confirm ownership before capture.")
    if args.reset_emulator:
        sdk = Path.home() / "Library/Application Support/Pebble SDK"
        for flash in sdk.glob("*/*/*flash*.bin"):
            backup = OUT / "emulator-backups" / flash.relative_to(sdk)
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                shutil.copy2(flash, backup)
        command(["pebble", "wipe"])

    fixture = OUT / "fixture.pbw"
    keys = json.loads((OUT / "message_keys.json").read_text())
    uuid = json.loads((ROOT / "watchface/package.json").read_text())["pebble"]["uuid"]
    install = ["pebble", "install", "--emulator", platform, str(fixture)]

    def send(values):
        command(["pebble", "send-app-message", "--emulator", platform, "--app-uuid", uuid, "--int"]
                + [f"{keys.get(key, key)}={value}" for key, value in values.items()])

    def shot(values):
        send({**values, 11022: 1})
        for _ in range(30):
            im = capture()
            if im.size == (width, height) and im.getpixel((width // 2 - 3, 18)) == (255, 0, 255):
                assert im.getpixel((width // 2 + 3, 18)) == (0, 255, 0)
                break
            time.sleep(.12)
        else:
            raise AssertionError("Window Seat fixture not in foreground")

        send({11022: 0})
        return settled()

    def settled():
        previous = None
        repeats = 0
        for _ in range(30):
            time.sleep(.12)
            im = capture()
            if im.getpixel((width // 2 - 3, 18)) == (255, 0, 255):
                continue
            raw = im.tobytes()
            repeats = repeats + 1 if previous == raw else 0
            previous = raw
            if repeats >= 2:
                assert im.size == (width, height)
                return im
        raise AssertionError("Native framebuffer did not settle")

    def capture_routes():
        catalog = json.loads((ROOT / "assets/routes.json").read_text())
        output = OUT / "route-shots"
        output.mkdir(exist_ok=True)
        cases = [("day", 12, 0), ("dusk", 17, 0), ("night", 0, 0),
                 ("rain", 17, 3), ("rain-day", 12, 3), ("rain-night", 0, 3)]
        start = datetime(2026, 11, 8)
        divider = height * 705 // 1000
        box = (width // 4, 40, width * 3 // 4, divider - 4)
        records = []
        distinct_routes = set()

        for route, (label, slug) in enumerate(catalog):
            distinct_states = set()
            for index, (mode, hour, kind) in enumerate(cases):
                if args.route_nights_only and mode not in ("night", "rain-night"):
                    continue
                stamp = int((start + timedelta(days=route * len(cases) + index, hours=hour, minutes=43)).timestamp())
                values = {11002: stamp, "Route": route, "SceneMode": 0,
                          "WeatherEnabled": 1, "TimeFormat": 1, "DateFormat": 0,
                          "WeatherAt": stamp, "ForecastAt": (stamp // 3600 + 1) * 3600,
                          "CurrentKind": kind, "Forecast0": kind, "Forecast1": 0, "Forecast2": 1}
                if not records:
                    image = shot(values)
                else:
                    send(values)
                    image = settled()
                view = image.crop(box).tobytes()
                assert len(set(image.crop(box).get_flattened_data())) > 4, (slug, mode, "missing art")
                ink = image.crop((width // 4, divider + 4, width * 3 // 4, divider + 42))
                assert sum(pixel == (255, 255, 170) for pixel in ink.get_flattened_data()) > 100, (slug, mode, "missing clock")
                assert view not in distinct_states, (slug, mode, "scene did not change")
                distinct_states.add(view)
                if mode == "dusk":
                    assert view not in distinct_routes, (slug, "route did not change")
                    distinct_routes.add(view)
                path = output / f"{platform}-{slug}-{mode}.png"
                image.save(path)
                records.append({"route": label, "scene": mode, "image": path.name, "size": image.size})
            print(platform, label, "night scenes" if args.route_nights_only else "six automatic scenes", flush=True)
        suffix = "route-nights" if args.route_nights_only else "routes"
        (OUT / f"{platform}-{suffix}-verification.json").write_text(json.dumps(records, indent=2) + "\n")

    cases = [
        ("dusk", 17, 0, 3, 1, 0, False),
        ("rain", 17, 3, 3, 1, 0, False),
        ("day", 12, 0, 1, 2, 1, False),
        ("rain-day", 12, 3, 3, 2, 2, False),
        ("night-12", 0, 0, 0, 1, 0, False),
        ("rain-night-24", 0, 3, 3, 2, 3, False),
        ("expired", 17, 3, 3, 1, 0, True),
    ]
    evidence = []
    previous = {}
    try:
        command(install)
        time.sleep(1)
        command(install)
        if args.routes or args.route_nights_only:
            capture_routes()
            return
        for index, (name, hour, current, forecast, fmt, date, expired) in enumerate(cases):
            stamp = int(datetime(2026, 11, 8 + index, hour, 43 if hour else 0).timestamp())
            now = stamp + 4501 if expired else stamp
            values = {11002: stamp,
                      "WeatherAt": stamp, "ForecastAt": (stamp // 3600 + 1) * 3600,
                      "CurrentKind": current, "Forecast0": forecast, "Forecast1": 0, "Forecast2": 1,
                      "TimeFormat": fmt, "DateFormat": date, "WeatherEnabled": 1, "SceneMode": 0}
            image = shot(values)
            if expired:
                image = shot({11002: now})
            previous[name] = image
            path = ROOT / f"media/{platform}-{name}.png"
            image.save(path)
            evidence.append({"case": name, "image": path.name, "size": image.size})
            print(platform, name, flush=True)
        divider = height * 705 // 1000
        art_box = (width // 4, 40, width * 3 // 4, divider - 1)
        assert previous["dusk"].crop(art_box).tobytes() != previous["rain"].crop(art_box).tobytes()
        assert previous["dusk"].crop(art_box).tobytes() == previous["expired"].crop(art_box).tobytes()
        for mode, label in enumerate(("day", "dusk", "night", "rain"), 1):
            name = f"preview-{label}"
            image = shot({"SceneMode": mode, "WeatherEnabled": 0})
            path = ROOT / f"media/{platform}-{name}.png"
            image.save(path)
            evidence.append({"case": name, "image": path.name, "size": image.size})
            print(platform, name, flush=True)
        assert shot({"SceneMode": 0, "WeatherEnabled": 1}).tobytes() == previous["expired"].tobytes()
        (OUT / f"{platform}-verification.json").write_text(json.dumps(evidence, indent=2) + "\n")
    finally:
        command(["pebble", "kill"])


if __name__ == "__main__":
    main()
