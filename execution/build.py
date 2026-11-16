"""Test Window Seat and isolate fixture builds from the production bundle."""
import argparse
import os
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WATCHFACE = ROOT / "watchface"


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--host-only", action="store_true")
    args = parser.parse_args()
    work = ROOT / ".tmp"
    work.mkdir(exist_ok=True)
    binary = work / "test_model"
    code = WATCHFACE / "src/c"
    run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(code),
         str(ROOT / "tests/host/test_model.c"), str(code / "model.c"), "-o", str(binary)])
    run([str(binary)])
    run(["node", str(ROOT / "tests/host/test_weather.js")])
    run(["python3", str(ROOT / "execution/prepare_art.py")])
    run(["python3", str(ROOT / "execution/prepare_routes.py")])
    run(["node", str(ROOT / "tests/host/test_settings.js")])
    run(["node", "--check", str(WATCHFACE / "src/pkjs/index.js")])
    if args.host_only:
        return
    env = {key: value for key, value in os.environ.items() if key != "WS_FIXTURE"}
    if args.fixture:
        env["WS_FIXTURE"] = "1"
    for command in ("clean", "build"):
        run(["pebble", command], cwd=WATCHFACE, env=env)
    output = work / "native" if args.fixture else ROOT / "dist"
    output.mkdir(parents=True, exist_ok=True)
    version = json.loads((WATCHFACE / "package.json").read_text())["version"]
    name = "fixture.pbw" if args.fixture else f"Window-Seat-{version}.pbw"
    shutil.copy2(WATCHFACE / "build/watchface.pbw", output / name)
    if args.fixture:
        shutil.copy2(WATCHFACE / "build/js/message_keys.json", output / "message_keys.json")
    print(output / name)


if __name__ == "__main__":
    main()
