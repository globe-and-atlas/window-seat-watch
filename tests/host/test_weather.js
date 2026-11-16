'use strict';
const assert = require('node:assert/strict');
const weather = require('../../watchface/src/pkjs/weather');
const payload = {
  current: { time: 18000, weather_code: 61 },
  hourly: { time: [18000, 21600, 25200, 28800], weather_code: [61, 65, 3, 0] }
};
assert.deepEqual(weather.weatherMessage(payload, 18200), {
  WeatherAt: 18200, CurrentKind: 3, ForecastAt: 21600, Forecast0: 3, Forecast1: 1, Forecast2: 0
});
assert.equal(weather.weatherMessage(payload, 21600), null);
assert.equal(weather.weatherMessage(payload, 14500), null);
assert.equal(weather.weatherMessage({...payload, current: {...payload.current, weather_code: null}}, 18200), null);
assert.equal(weather.weatherMessage({...payload, hourly: {...payload.hourly, time: [18000, 21600, 25300, 28800]}}, 18200), null);
assert.equal(weather.condition(77), 4);
assert.equal(weather.condition(99), 5);
const url = new URL(weather.weatherUrl(41.893491, -87.63557));
assert.equal(url.searchParams.get('latitude'), '41.89');
assert.equal(url.searchParams.get('longitude'), '-87.64');
assert.equal(url.searchParams.get('timeformat'), 'unixtime');
console.log('Window Seat forecast packet checks passed');
