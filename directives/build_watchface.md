---
generated_by: OpenAI Codex
timestamp: "2026-11-08"
---
# Build Window Seat

Run python3 execution/build.py to prepare hardware-palette assets, test the native model and phone weather parser, and produce the clean PBW. Use execution/build.py --fixture for controlled time/weather scenarios, then capture native frames serially with execution/capture_native.py. Preserve the clean production PBW separately. The phone uses a fresh location and Open-Meteo hourly forecast. Cache only complete weather packets on the watch. Weather expiry falls back to time-based scenery.
