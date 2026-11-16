#include <pebble.h>
#include "config.h"
#include "model.h"
#include "route_resources.h"

enum { SAVED_TIME = 1, SAVED_DATE, SAVED_WEATHER_ENABLED, SAVED_WEATHER, SAVED_SCENE_MODE, SAVED_ROUTE };
static Window *window;
static Layer *face;
static GBitmap *art;
static int scene = -1;
static int route;
static int loaded_route = -1;
static int time_format;
static int date_format;
static int scene_mode;
static bool weather_enabled = true;
static Weather weather;
static bool inbox_ready;

#if WS_FIXTURE
static time_t fixture_now;
static bool fixture_marker;
#endif

#ifdef PBL_ROUND
static const uint32_t art_ids[] = {
    RESOURCE_ID_GABBRO_DAY, RESOURCE_ID_GABBRO_DUSK, RESOURCE_ID_GABBRO_NIGHT,
    RESOURCE_ID_GABBRO_RAIN_DAY, RESOURCE_ID_GABBRO_RAIN_DUSK, RESOURCE_ID_GABBRO_RAIN_NIGHT
};
#else
static const uint32_t art_ids[] = {
    RESOURCE_ID_EMERY_DAY, RESOURCE_ID_EMERY_DUSK, RESOURCE_ID_EMERY_NIGHT,
    RESOURCE_ID_EMERY_RAIN_DAY, RESOURCE_ID_EMERY_RAIN_DUSK, RESOURCE_ID_EMERY_RAIN_NIGHT
};
#endif

static time_t now_time(void) {
#if WS_FIXTURE
    if (fixture_now > 0) return fixture_now;
#endif
    return time(NULL);
}

static void centered(GContext *ctx, const char *text, GFont font, GColor ink, GRect box) {
    graphics_context_set_text_color(ctx, ink);
    graphics_draw_text(ctx, text, font, box, GTextOverflowModeTrailingEllipsis,
                       GTextAlignmentCenter, NULL);
}

static void forecast_line(char *line, size_t length, time_t now, bool is_24) {
    int index = weather_enabled ? ws_forecast_index(&weather, now) : -1;
    if (index < 0) {
        snprintf(line, length, "%s", weather_enabled ? "WEATHER UNAVAILABLE" : "");
        return;
    }
    time_t forecast_time = (time_t)weather.forecast_at + index * 3600;
    struct tm forecast = *localtime(&forecast_time);
    const char *condition = ws_condition_name(weather.hourly[index]);
    if (is_24) {
        snprintf(line, length, "%s AT %02d:%02d", condition, forecast.tm_hour, forecast.tm_min);
    } else if (forecast.tm_min == 0) {
        snprintf(line, length, "%s AT %d %s", condition, ws_clock_hour(forecast.tm_hour, false),
                 forecast.tm_hour < 12 ? "AM" : "PM");
    } else {
        snprintf(line, length, "%s AT %d:%02d %s", condition, ws_clock_hour(forecast.tm_hour, false),
                 forecast.tm_min, forecast.tm_hour < 12 ? "AM" : "PM");
    }
}

static void load_scene(int selected) {
    if (art) gbitmap_destroy(art);
    art = gbitmap_create_with_resource(route ? route_ids[route - 1] : art_ids[selected]);
    loaded_route = route;
    scene = art ? selected : -1;
    if (!art || !route || gbitmap_get_format(art) != GBitmapFormat8Bit) return;

    uint8_t *data = gbitmap_get_data(art);
    const int stride = gbitmap_get_bytes_per_row(art);
    for (size_t y = 0; y < ARRAY_LENGTH(glass_spans); y++) {
        uint8_t *row = data + y * stride;
        for (int x = glass_spans[y][0]; x < glass_spans[y][1]; x++) {
            row[x] = ws_route_pixel(row[x], selected, x, y);
        }
    }
}

static void draw(Layer *layer, GContext *ctx) {
    GRect bounds = layer_get_bounds(layer);
    const int width = bounds.size.w, height = bounds.size.h;
    const int divider = height * 705 / 1000;
    time_t now = now_time();
    struct tm clock = *localtime(&now);
    bool is_24 = ws_is_24(time_format, clock_is_24h_style());
    bool fresh = weather_enabled && ws_weather_valid(&weather, now);
    Condition current = fresh ? weather.current : CLEAR;
    int selected = ws_scene(clock.tm_hour, current, scene_mode);
    if (selected != scene || route != loaded_route) load_scene(selected);

    graphics_context_set_fill_color(ctx, GColorOxfordBlue);
    graphics_fill_rect(ctx, bounds, 0, GCornerNone);
    if (art) {
        graphics_context_set_compositing_mode(ctx, GCompOpSet);
        graphics_draw_bitmap_in_rect(ctx, art, GRect(0, 0, width, divider));
    }
    graphics_context_set_fill_color(ctx, GColorWindsorTan);
    graphics_fill_rect(ctx, GRect(0, divider, width, 2), 0, GCornerNone);

    char digits[12], forecast[32];
    int hour = ws_clock_hour(clock.tm_hour, is_24);
    snprintf(digits, sizeof digits, is_24 ? "%02d:%02d" : "%d:%02d", hour, clock.tm_min);
    GColor cream = GColorPastelYellow;
    centered(ctx, digits, fonts_get_system_font(FONT_KEY_BITHAM_42_BOLD), cream,
             GRect(0, divider - 1, width, 49));
    if (!is_24) {
        centered(ctx, clock.tm_hour < 12 ? "AM" : "PM",
                 fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD), cream,
                 GRect(width / 2 + 56, divider + 18, 26, 19));
    }
    forecast_line(forecast, sizeof forecast, now, is_24);
    centered(ctx, forecast, fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD), GColorCeleste,
             GRect(width / 2 - 82, divider + 44, 164, 18));
    const char *phases[] = {"DAY", "DUSK", "NIGHT"};
    const char *phase = phases[selected % 3];
    char scene_label[30];
    if (scene_mode) {
        snprintf(scene_label, sizeof scene_label, "%s PREVIEW", scene_mode == 4 ? "RAIN" : phase);
    } else if (fresh) {
        snprintf(scene_label, sizeof scene_label, "%s / %s NOW", phase, ws_condition_name(current));
    } else {
        snprintf(scene_label, sizeof scene_label, "%s", phase);
    }
    const int tag_top = height == width ? 22 : 5;
    GFont small = fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD);
    GSize tag_text = graphics_text_layout_get_content_size(scene_label, small,
        GRect(0, 0, 160, 18), GTextOverflowModeTrailingEllipsis, GTextAlignmentCenter);
    const int tag_width = tag_text.w + 12;
    graphics_context_set_fill_color(ctx, GColorOxfordBlue);
    graphics_fill_rect(ctx, GRect((width - tag_width) / 2, tag_top, tag_width, 18), 3, GCornersAll);
    centered(ctx, scene_label, small, cream, GRect(0, tag_top - 1, width, 18));

    if (date_format) {
        char date[16];
        const char *formats[] = {"", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"};
        strftime(date, sizeof date, formats[date_format], &clock);
        const int top = tag_top + 20;
        graphics_context_set_fill_color(ctx, GColorOxfordBlue);
        graphics_fill_rect(ctx, GRect(width / 2 - 38, top, 76, 18), 3, GCornersAll);
        centered(ctx, date, small, cream, GRect(width / 2 - 38, top - 1, 76, 18));
    }
#if WS_FIXTURE
    if (fixture_marker) {
        graphics_context_set_fill_color(ctx, GColorMagenta);
        graphics_fill_rect(ctx, GRect(width / 2 - 4, 18, 2, 2), 0, GCornerNone);
        graphics_context_set_fill_color(ctx, GColorGreen);
        graphics_fill_rect(ctx, GRect(width / 2 + 2, 18, 2, 2), 0, GCornerNone);
    }
#endif
}

static bool read_int(DictionaryIterator *it, uint32_t key, int32_t *value) {
    Tuple *tuple = dict_find(it, key);
    if (!tuple || (tuple->type != TUPLE_INT && tuple->type != TUPLE_UINT)) return false;
    switch (tuple->length) {
        case 1: *value = tuple->type == TUPLE_INT ? (int32_t)tuple->value->int8 : tuple->value->uint8; break;
        case 2: *value = tuple->type == TUPLE_INT ? (int32_t)tuple->value->int16 : tuple->value->uint16; break;
        case 4: *value = tuple->value->int32; break;
        default: return false;
    }
    return true;
}

static void inbox(DictionaryIterator *it, void *context) {
    (void)context;
    int32_t value;
#if WS_FIXTURE
    if (read_int(it, 11002, &value) && value > 0) fixture_now = value;
    if (read_int(it, 11022, &value)) fixture_marker = value != 0;
#endif
    if (read_int(it, MESSAGE_KEY_TimeFormat, &value) && value >= 0 && value <= 2 && value != time_format) {
        time_format = value;
        persist_write_int(SAVED_TIME, value);
    }
    if (read_int(it, MESSAGE_KEY_DateFormat, &value) && value >= 0 && value <= 3 && value != date_format) {
        date_format = value;
        persist_write_int(SAVED_DATE, value);
    }
    if (read_int(it, MESSAGE_KEY_SceneMode, &value) && value >= 0 && value <= 4 && value != scene_mode) {
        scene_mode = value;
        persist_write_int(SAVED_SCENE_MODE, value);
    }
    if (read_int(it, MESSAGE_KEY_Route, &value) && value >= 0 && value < WS_ROUTE_COUNT && value != route) {
        route = value;
        persist_write_int(SAVED_ROUTE, value);
    }
    if (read_int(it, MESSAGE_KEY_WeatherEnabled, &value) && (value == 0 || value == 1) &&
        (bool)value != weather_enabled) {
        weather_enabled = value;
        persist_write_bool(SAVED_WEATHER_ENABLED, weather_enabled);
        if (!weather_enabled) {
            weather = (Weather){0};
            persist_delete(SAVED_WEATHER);
        }
    }
    Weather next;
    if (weather_enabled && read_int(it, MESSAGE_KEY_WeatherAt, &next.observed_at) &&
        read_int(it, MESSAGE_KEY_CurrentKind, &next.current) &&
        read_int(it, MESSAGE_KEY_ForecastAt, &next.forecast_at) &&
        read_int(it, MESSAGE_KEY_Forecast0, &next.hourly[0]) &&
        read_int(it, MESSAGE_KEY_Forecast1, &next.hourly[1]) &&
        read_int(it, MESSAGE_KEY_Forecast2, &next.hourly[2]) &&
        ws_weather_valid(&next, now_time()) &&
        (next.observed_at > weather.observed_at || !ws_weather_valid(&weather, now_time()))) {
        weather = next;
        persist_write_data(SAVED_WEATHER, &weather, sizeof weather);
    }
    layer_mark_dirty(face);
}

static void tick(struct tm *clock, TimeUnits units) {
    (void)clock;
    (void)units;
    layer_mark_dirty(face);
}

static void reconnect(bool connected) {
    if (!connected || !weather_enabled || !inbox_ready) return;
    DictionaryIterator *out;
    if (app_message_outbox_begin(&out) == APP_MSG_OK) {
        dict_write_uint8(out, MESSAGE_KEY_WeatherRequest, 1);
        app_message_outbox_send();
    }
}

static void init(void) {
    if (persist_exists(SAVED_TIME)) time_format = persist_read_int(SAVED_TIME);
    if (persist_exists(SAVED_DATE)) date_format = persist_read_int(SAVED_DATE);
    if (persist_exists(SAVED_WEATHER_ENABLED)) weather_enabled = persist_read_bool(SAVED_WEATHER_ENABLED);
    if (time_format < 0 || time_format > 2) time_format = 0;
    if (date_format < 0 || date_format > 3) date_format = 0;
    if (persist_exists(SAVED_SCENE_MODE)) scene_mode = persist_read_int(SAVED_SCENE_MODE);
    if (scene_mode < 0 || scene_mode > 4) scene_mode = 0;
    if (persist_exists(SAVED_ROUTE)) route = persist_read_int(SAVED_ROUTE);
    if (route < 0 || route >= WS_ROUTE_COUNT) route = 0;
    if (weather_enabled && persist_get_size(SAVED_WEATHER) == sizeof weather)
        persist_read_data(SAVED_WEATHER, &weather, sizeof weather);

    window = window_create();
    Layer *root = window_get_root_layer(window);
    face = layer_create(layer_get_bounds(root));
    layer_set_update_proc(face, draw);
    layer_add_child(root, face);
    window_stack_push(window, false);
    tick_timer_service_subscribe(MINUTE_UNIT, tick);
    app_message_register_inbox_received(inbox);
    inbox_ready = app_message_open(256, 64) == APP_MSG_OK;
    connection_service_subscribe((ConnectionHandlers){.pebble_app_connection_handler = reconnect});
}

static void deinit(void) {
    connection_service_unsubscribe();
    tick_timer_service_unsubscribe();
    app_message_deregister_callbacks();
    if (art) gbitmap_destroy(art);
    layer_destroy(face);
    window_destroy(window);
}

int main(void) {
    init();
    app_event_loop();
    deinit();
}
