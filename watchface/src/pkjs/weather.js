'use strict';

function condition(code) {
  if (!Number.isInteger(code)) return null;
  if (code === 0) return 0;
  if (code >= 1 && code <= 3) return 1;
  if (code === 45 || code === 48) return 2;
  if ([51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82].indexOf(code) !== -1) return 3;
  if ([71, 73, 75, 77, 85, 86].indexOf(code) !== -1) return 4;
  if ([95, 96, 99].indexOf(code) !== -1) return 5;
  return null;
}

function weatherMessage(payload, now) {
  var current = payload && payload.current;
  var hourly = payload && payload.hourly;
  if (!current || !hourly || !Array.isArray(hourly.time) ||
      !Array.isArray(hourly.weather_code) || hourly.time.length !== hourly.weather_code.length) return null;
  if (!Number.isInteger(current.time) || Math.abs(now - current.time) > 1800) return null;
  var currentKind = condition(current.weather_code);
  if (currentKind === null) return null;
  var first = hourly.time.findIndex(function (stamp) {
    return Number.isInteger(stamp) && stamp > now;
  });
  if (first < 0 || first + 2 >= hourly.time.length) return null;
  var forecastAt = hourly.time[first];
  if (forecastAt - now > 3600) return null;
  var message = { WeatherAt: now, CurrentKind: currentKind, ForecastAt: forecastAt };
  for (var index = 0; index < 3; index++) {
    if (hourly.time[first + index] !== forecastAt + index * 3600) return null;
    var kind = condition(hourly.weather_code[first + index]);
    if (kind === null) return null;
    message['Forecast' + index] = kind;
  }
  return message;
}

function weatherUrl(latitude, longitude) {
  return 'https://api.open-meteo.com/v1/forecast?latitude=' + latitude.toFixed(2) +
    '&longitude=' + longitude.toFixed(2) +
    '&current=weather_code&hourly=weather_code&forecast_hours=5&timeformat=unixtime';
}

module.exports = { condition: condition, weatherMessage: weatherMessage, weatherUrl: weatherUrl };
