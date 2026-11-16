---
generated_by: OpenAI Codex
timestamp: "2026-11-08"
---
# Window Seat handoff

Goal: build the approved Window Seat for Time 2 and Round 2.
Agent: OpenAI Codex
Handoff-from: none
Handoff-type: new-project
Status: Window Seat 0.2.0 is live for Time 2 and Round 2.

Window Seat 0.1.0 is built for emery and gabbro. Production bundle: dist/Window-Seat-0.1.0.pbw. UUID ecee5b93-e8bf-44dc-9a96-2298009f9eff. SHA-256 830f46d2659e920e12193030b094f3b099f66d4d748736532012854af804744c.

Both native matrices passed seven cases. The preview at media/native-comparison.png shows day, dusk, rain, and rain at night. The C model, weather packet parser, and actual Clay flow with mocked phone services passed. A live Open-Meteo response from a fixed public test location passed the parser. The independently reviewed clean PBW has both binaries and no fixture controls.

## Scene clarity update

The user saw a valid hourly rain forecast while the current view still looked dry. Version 0.1.1 labels the lighting phase and latest current condition above the window. The next hourly forecast remains below the clock. Window view settings offer Auto, Day, Dusk, Night, and Rain previews. Preview artwork is marked separately from live weather.

Bundle: dist/Window-Seat-0.1.1.pbw. SHA-256 c762daa5334510e05f52b4e6450d5526be1683c8bc6c693dda683f3befcdce76. Both device matrices passed eleven cases, including dry and rainy dusk with the same future rain forecast, offline previews, and return to Auto. The prior UUID and message keys are retained.

## Store release

Window Seat 0.1.1 is live at https://apps.repebble.com/aca3bb65eafa438ebb7474e0. Both selected-device galleries begin with the Day, Dusk, Night, Rain animation and contain four lossless native stills. The public download and all ten preview files match the staged release. The original listing icon crop clipped clock strokes. Both sizes now use the dusk carriage art directly and the saved files were checked. Independent public release proof passed. Evidence is under release/.

S.D.G.: Gives Pebble wearers an immediate distinction between what the window shows now and the next forecast.
Feynman gap: The updated build passed emulator and Clay checks. Physical-device weather changes remain unverified for this build.

## Route expansion

The Route setting offers Countryside as the default, the four approved routes, and twelve landmark routes. Auto uses watch-local time and phone-local weather for each. The May 30 community report snapshot was used as a country-level order proxy. The selection is documented in knowledge/domain/route_selection.md.

Production bundle: dist/Window-Seat-0.2.0.pbw. SHA-256 7512f2a7ea64bd45b7f5085bc8129f17a9aad8c85b06d9ee8575a1ac08a893ad. Both original sets of six Countryside resources match 0.1.1 byte-for-byte. Final production packs are 138595 bytes on Emery and 181945 bytes on Gabbro. Production binaries exclude the fixture controls.

Host and Clay checks passed. Native emulators captured 102 automatic route/phase combinations on each display, then repeated the 34 night cases per display after correcting outdoor highlights. Matrix evidence is under .tmp/native. The galleries are media/routes-emery.png and media/routes-gabbro.png. The four-state comparison is media/route-scenes.png. The independent review passed against the exact bundle and final native captures. The release has not been submitted.

S.D.G.: Gives Time 2 and Round 2 wearers a choice of train-window views that track their own local lighting and rain.
Feynman gap: The automatic states were verified with injected time and weather on both emulators. The new routes have not been checked on physical watches.

## Store release 0.2.0

Published the reviewed PBW to the existing listing at https://apps.repebble.com/aca3bb65eafa438ebb7474e0. Each device gallery opens with a 20-frame native GIF covering 17 routes. The first four frames show San Francisco in day, dusk, night, and rain. Each gallery follows with four native stills. Both galleries were checked in the refreshed public browser and the ten public assets match the local files byte-for-byte. The public PBW matches the independently reviewed SHA-256. An independent reviewer matched the public PBW and ten assets byte-for-byte. The receipt and verification are under release/0.2.0/.

S.D.G.: Gives Pebble owners an accurate preview of the route and weather options on their selected display.
Feynman gap: Store download and gallery evidence are exact. This release step did not exercise physical-watch weather.
