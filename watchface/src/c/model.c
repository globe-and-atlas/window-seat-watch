#include "model.h"

bool ws_is_24(int setting, bool watch_24) {
    return setting == 2 || (setting == 0 && watch_24);
}

int ws_clock_hour(int hour, bool is_24) {
    return is_24 ? hour : (hour + 11) % 12 + 1;
}

int ws_scene(int hour, Condition current, int mode) {
    if (mode >= 1 && mode <= 3) return mode - 1;
    if (mode == 4) return 4;  // Rain preview uses the approved dusk composition.
    int phase = hour >= 20 || hour < 6 ? 2 : hour >= 17 ? 1 : 0;
    return phase + ((current == RAIN || current == STORM) ? 3 : 0);
}

bool ws_weather_valid(const Weather *weather, time_t now) {
    int64_t age = (int64_t)now - weather->observed_at;
    int64_t lead = (int64_t)weather->forecast_at - weather->observed_at;
    if (weather->observed_at <= 0 || age < -90 || age > 75 * 60 ||
        lead <= 0 || lead > 3600 || weather->current < 0 ||
        weather->current >= CONDITION_COUNT) return false;
    for (size_t index = 0; index < 3; index++) {
        if (weather->hourly[index] < 0 || weather->hourly[index] >= CONDITION_COUNT) return false;
    }
    return true;
}

int ws_forecast_index(const Weather *weather, time_t now) {
    if (!ws_weather_valid(weather, now)) return -1;
    for (int index = 0; index < 3; index++) {
        if ((int64_t)weather->forecast_at + index * 3600 > now) return index;
    }
    return -1;
}

const char *ws_condition_name(Condition kind) {
    static const char *names[] = {"CLEAR", "CLOUDY", "FOG", "RAIN", "SNOW", "STORM"};
    return (unsigned)kind < CONDITION_COUNT ? names[kind] : "";
}

uint8_t ws_route_pixel(uint8_t pixel, int selected, int x, int y) {
    int phase = selected % 3;
    bool rain = selected >= 3;
    if (phase == 1 && !rain) return pixel;

    int red = (pixel >> 4) & 3;
    int green = (pixel >> 2) & 3;
    int blue = pixel & 3;
    if (phase == 0) {
        // Lift midtones and turn the sunset coral into daylight sky tones.
        if (red + green + blue >= 2) {
            if (blue < 3) blue++;
            if (green < 3) green++;
        }
        if (red > green && red > blue) red--;
    } else if (phase == 2) {
        // Cool every outdoor highlight, including the sunset disk.
        red = red / 2;
        green = green / 2;
        blue = blue > 1 ? 2 : 1;
    }
    if (rain) {
        red = red / 2;
        if (green > 1) green--;
        if (blue < 2) blue++;
        // Stagger short diagonal strokes so the rain reads as glass, not a grid.
        int diagonal = x + y / 2;
        int lane = diagonal / 13;
        if (diagonal % 13 == 0 && (y + lane * 17) % 43 < 10) {
            red = phase == 2 ? 0 : 1;
            green = phase == 2 ? 1 : 2;
            blue = 3;
        }
    }
    return 0xc0 | (red << 4) | (green << 2) | blue;
}
