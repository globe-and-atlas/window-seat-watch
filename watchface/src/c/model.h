#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>

typedef enum { CLEAR, CLOUD, FOG, RAIN, SNOW, STORM, CONDITION_COUNT } Condition;
typedef struct {
    int32_t observed_at;
    int32_t forecast_at;
    int32_t current;
    int32_t hourly[3];
} Weather;

bool ws_is_24(int setting, bool watch_24);
int ws_clock_hour(int hour, bool is_24);
int ws_scene(int hour, Condition current, int mode);
bool ws_weather_valid(const Weather *weather, time_t now);
int ws_forecast_index(const Weather *weather, time_t now);
const char *ws_condition_name(Condition kind);
uint8_t ws_route_pixel(uint8_t pixel, int selected, int x, int y);
