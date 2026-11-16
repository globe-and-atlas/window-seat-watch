# Window Seat

A sleeper train window for Pebble Time 2 and Round 2. The carriage view follows local watch time. Fresh rain and thunderstorm conditions bring rain onto the glass. A small label above the window names the lighting phase and current condition. Under the clock, the face shows the next hourly condition and its local time.

Day begins at 06:00, dusk at 17:00, and night at 20:00. In the Pebble app, choose watch default, 12-hour, or 24-hour time. The date is off by default, with ISO, US, and European options. You can turn weather off to leave the clock and scenery. Window view offers Auto and four fixed previews. The forecast continues to show live data in preview mode when enabled.

Choose a Route in settings. Countryside is the default. Alpine Pass, Coastal Route, City Approach, and Snowy Forest join twelve landmark routes: San Francisco, London, Toronto, Sydney, Berlin, Amsterdam, Paris, Barcelona, Queenstown, Stockholm, Rome, and Budapest. Route chooses the scenery. Auto still uses your watch's local time and the weather at your phone's location.

Native previews: [Time 2 route gallery](media/routes-emery.png), [Round 2 route gallery](media/routes-gabbro.png), and [automatic lighting and rain](media/route-scenes.png).

With weather enabled, PebbleKit JS requests approximate phone coordinates for Open-Meteo every 30 minutes while active. It rounds coordinates to two decimal places before the request. The watch retains the latest valid conditions and up to three hourly forecast entries, without coordinates. After 75 minutes, stale data gives way to the time-based view and a WEATHER UNAVAILABLE line.

## Build

Install the Pebble SDK, Node.js and Python with Pillow. Run `npm ci --prefix watchface` and `python3 execution/build.py`. The latter runs host checks and creates `dist/Window-Seat-0.2.0.pbw`. Use `--host-only` to run the checks without the SDK. The approved illustration is in `assets/source/carriage.png`.

Native screenshot cases use `execution/build.py --fixture` and `execution/capture_native.py --platform emery` or `--platform gabbro`. Use `--routes` to capture all six automatic states on each route. Run emulator targets serially. The fixture bundle lives under `.tmp/native`.

Forecast data from [Open-Meteo](https://open-meteo.com/).
