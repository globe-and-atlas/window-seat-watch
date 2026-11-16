---
generated_by: OpenAI Codex
timestamp: "2026-11-08"
---
# Decisions

Use watch-local hour bands for the three lighting phases. Use the matched wet artwork for rain and thunderstorm conditions. Snow, fog, and cloud remain forecast labels. This keeps the approved artwork recognizable across phases.

Store a validated forecast packet with its timestamp and three consecutive hourly codes. Choose the first future sample on each minute redraw. Expire the packet after 75 minutes and fall back to local-time art. Settings can disable weather entirely.

Prepare platform-specific image resources at build time and keep only one scene bitmap in memory. Separate fixture time injection from the production bundle.

The scene badge names current lighting and conditions. The forecast retains its separate future time. Manual previews are marked PREVIEW and leave forecast data independent of the illustration.

## Route expansion

Route is independent of Window view. Persist an appended setting with Countryside as the default and preserve the earlier AppMessage IDs. Countryside retains the original six bitmap resources. New routes share the carriage frame and store one compressed dusk bitmap per display. The watch applies the phase palette and rain streaks to the glass pixels when the route or weather scene changes. One bitmap remains resident. A generated scanline mask is shared by asset composition and the watch renderer. This fits the SDK resource budget while avoiding duplicate scenery.
