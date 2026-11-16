#include <assert.h>
#include <stdio.h>
#include "model.h"

int main(void) {
    for (int hour = 0; hour < 24; hour++) {
        int expected = hour < 6 || hour >= 20 ? 2 : hour >= 17 ? 1 : 0;
        assert(ws_scene(hour, CLEAR, 0) == expected);
        assert(ws_scene(hour, RAIN, 0) == expected + 3);
        assert(ws_scene(hour, STORM, 0) == expected + 3);
        assert(ws_scene(hour, SNOW, 0) == expected);
        assert(ws_clock_hour(hour, true) == hour);
        assert(ws_clock_hour(hour, false) == (hour % 12 ? hour % 12 : 12));
    }
    assert(ws_scene(1, RAIN, 1) == 0);
    assert(ws_scene(12, CLEAR, 2) == 1);
    assert(ws_scene(12, RAIN, 3) == 2);
    assert(ws_scene(12, CLEAR, 4) == 4);
    assert(ws_is_24(0, true) && !ws_is_24(0, false));
    assert(ws_is_24(2, false) && !ws_is_24(1, true));
    Weather weather = {100000, 100300, CLEAR, {RAIN, CLOUD, CLEAR}};
    assert(ws_forecast_index(&weather, 100000) == 0);
    assert(ws_forecast_index(&weather, 100299) == 0);
    assert(ws_forecast_index(&weather, 100300) == 1);
    assert(ws_forecast_index(&weather, 103900) == 2);
    assert(ws_forecast_index(&weather, 104501) == -1);
    assert(ws_weather_valid(&weather, 99999));
    assert(!ws_weather_valid(&weather, 99909));
    weather.hourly[1] = 9;
    assert(!ws_weather_valid(&weather, 100000));
    for (int color = 0xc0; color <= 0xff; color++) {
        assert(ws_route_pixel(color, 1, 100, 40) == color);
        for (int mode = 0; mode < 6; mode++) {
            assert((ws_route_pixel(color, mode, 100, 40) & 0xc0) == 0xc0);
        }
    }
    assert(ws_route_pixel(0xf5, 0, 100, 40) != ws_route_pixel(0xf5, 2, 100, 40));
    assert(ws_route_pixel(0xf5, 1, 100, 40) != ws_route_pixel(0xf5, 4, 100, 40));
    puts("Window Seat host model checks passed");
}
