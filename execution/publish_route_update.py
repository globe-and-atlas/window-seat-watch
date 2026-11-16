"""Upload the reviewed Window Seat route update once, then verify its public assets."""
from contextlib import ExitStack
import argparse
import json
from pathlib import Path
import sys
import time
from zipfile import ZipFile

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "execution"))
from publish_watchface_updates import API, PublishCommand, account_mapping, fetch, listing, save, sha

VERSION = "0.2.0"
APP_ID = "aca3bb65eafa438ebb7474e0"
UUID = "ecee5b93-e8bf-44dc-9a96-2298009f9eff"
REVIEWED_SHA = "7512f2a7ea64bd45b7f5085bc8129f17a9aad8c85b06d9ee8575a1ac08a893ad"
PBW = ROOT / f"dist/Window-Seat-{VERSION}.pbw"
MEDIA = ROOT / f"media/store/{VERSION}"
STATE = ROOT / f".tmp/store/{VERSION}"
RELEASE = ROOT / f"release/{VERSION}"
PLATFORMS = {"emery": (200, 228), "gabbro": (260, 260)}


def validate():
    assert sha(PBW.read_bytes()) == REVIEWED_SHA
    with ZipFile(PBW) as archive:
        assert archive.testzip() is None
        info = json.loads(archive.read("appinfo.json"))
        assert info["uuid"] == UUID
        assert info["versionLabel"] == VERSION
        assert info["targetPlatforms"] == list(PLATFORMS)
    groups = {}
    for platform, size in PLATFORMS.items():
        paths = sorted(MEDIA.glob(f"{platform}_*.gif"))
        assert len(paths) == 5 and paths[0].name == f"{platform}_01_route-tour.gif"
        for index, path in enumerate(paths):
            with Image.open(path) as image:
                assert image.size == size
                assert image.n_frames == (1 if index else 20)
        groups[platform] = paths
    return groups


def publish():
    groups = validate()
    receipt = RELEASE / "store-release.json"
    guard = STATE / "inflight.json"
    if receipt.exists() or guard.exists():
        raise RuntimeError("Release already attempted. Reconcile public state before another write.")
    before = listing(APP_ID)
    assert any("/0.1.1/" in url for url in before["downloads"])
    assert not any(f"/{VERSION}/" in url for url in before["downloads"])
    save(RELEASE / "prior-listing.json", before)
    token, mapping = account_mapping()
    assert PublishCommand._lookup_app_id_case_insensitive(mapping, UUID) == APP_ID
    data = {
        "version": VERSION,
        "isPublished": "true",
        "replaceScreenshots": "true",
        "releaseNotes": (
            "Choose from 17 train-window routes, including the original Countryside, four new landscapes, "
            "and twelve landmark views. Every route follows local day, dusk, night, and rain on "
            "Pebble Time 2 and Pebble Round 2."
        ),
    }
    save(guard, {"app_id": APP_ID, "version": VERSION, "sha256": REVIEWED_SHA, "started_at": time.time()})
    with ExitStack() as stack:
        files = [("pbwFile", (PBW.name, stack.enter_context(PBW.open("rb")), "application/octet-stream"))]
        for platform, paths in groups.items():
            files.extend((f"screenshots_{platform}", (path.name, stack.enter_context(path.open("rb")), "image/gif"))
                         for path in paths)
        try:
            response = requests.post(f"{API}/api/dashboard/apps/{APP_ID}/releases",
                                     headers={"Authorization": f"Bearer {token}"},
                                     data=data, files=files, timeout=(15, 300))
        except requests.RequestException:
            raise RuntimeError("Release outcome ambiguous. The write guard was retained.") from None
    if not response.ok:
        save(STATE / "upload-error.json", {"status": response.status_code, "body": response.text[:1000]})
        raise RuntimeError(f"Release upload returned HTTP {response.status_code}. The write guard was retained.")
    payload = response.json()
    save(STATE / "response.json", payload)
    results = payload.get("screenshotResults", {})
    save(receipt, {"app_id": APP_ID, "version": VERSION, "sha256": REVIEWED_SHA,
                   "url": before["url"], "public_verified": False, "screenshot_results": results})
    guard.unlink()
    if results.get("failed"):
        raise RuntimeError("Release saved. Screenshot errors require a gallery-only correction.")
    print(f"Release accepted: {before['url']}")


def verify():
    groups = validate()
    # Use the hydrated listing's observed order and download, since HTML may be cached.
    observed = json.loads((STATE / "public-ui.json").read_text())
    pbw_url = observed["download"]
    assert pbw_url.startswith(f"{API}/api/assets/pbw/{APP_ID}/{VERSION}/")
    assert sha(fetch(pbw_url)) == REVIEWED_SHA
    for platform, paths in groups.items():
        urls = observed["galleries"][platform]
        for path, url in zip(paths, urls, strict=True):
            assert f"/{APP_ID}/{platform}/" in url
            assert sha(fetch(url)) == sha(path.read_bytes()), path.name
    save(RELEASE / "public-proof.json", {**observed, "pbw_sha256": REVIEWED_SHA})
    receipt = RELEASE / "store-release.json"
    save(receipt, {**json.loads(receipt.read_text()), "public_verified": True})
    print(f"Public PBW and both galleries verified: {observed['url']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "publish", "verify"))
    action = parser.parse_args().action
    if action == "validate":
        validate()
        print("Reviewed PBW and ten native GIF assets validated.")
    elif action == "publish":
        publish()
    else:
        verify()
