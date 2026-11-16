'use strict';

var Clay = require('@rebble/clay');
var weather = require('./weather');
var routes = require('./routes');
var refreshPeriod = 30 * 60 * 1000;
var weatherEnabled = true;
var busy = false;
var lastAttempt = 0;

var clay = new Clay([
  {type: 'heading', defaultValue: 'Window Seat'},
  {type: 'text', defaultValue: 'The carriage follows local watch time. Weather uses an approximate phone location and Open-Meteo. The clock and time-based scenery work offline.'},
  {type: 'select', messageKey: 'TimeFormat', label: 'Time format', defaultValue: '0', options: [
    {label: 'Watch default', value: '0'}, {label: '12-hour', value: '1'}, {label: '24-hour', value: '2'}
  ]},
  {type: 'select', messageKey: 'DateFormat', label: 'Date', defaultValue: '0', options: [
    {label: 'Off', value: '0'}, {label: 'YYYY-MM-DD', value: '1'},
    {label: 'MM/DD/YYYY', value: '2'}, {label: 'DD/MM/YYYY', value: '3'}
  ]},
  {type: 'select', messageKey: 'Route', label: 'Route', defaultValue: '0',
    options: routes.map(function (label, index) { return {label: label, value: String(index)}; })},
  {type: 'select', messageKey: 'SceneMode' , label: 'Window view', defaultValue: '0', options: [
    {label: 'Auto (current conditions)', value: '0'},
    {label: 'Day preview', value: '1'}, {label: 'Dusk preview', value: '2'},
    {label: 'Night preview', value: '3'}, {label: 'Rain preview', value: '4'}
  ]},
  {type: 'text', defaultValue: 'In Auto, the window shows current conditions. The line under the clock is a forecast. Preview modes change the artwork.'},
  {type: 'toggle', messageKey: 'WeatherEnabled' , label: 'Local weather', defaultValue: true},
  {type: 'submit', defaultValue: 'Save to watch'}
], null, {autoHandleEvents: false});

function setting(value, maximum) {
  if (typeof value !== 'number' && typeof value !== 'string') return 0;
  var number = Number(value);
  return Number.isInteger(number) && number >= 0 && number <= maximum ? number : 0;
}

function readSettings() {
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem('clay-settings')) || {}; }
  catch (error) { console.log('Window Seat settings were unreadable'); }
  return {
    TimeFormat: setting(saved.TimeFormat, 2),
    DateFormat: setting(saved.DateFormat, 3),
    SceneMode: setting(saved.SceneMode, 4),
    Route: setting(saved.Route, routes.length - 1),
    WeatherEnabled: saved.WeatherEnabled === false || saved.WeatherEnabled === 0 ? 0 : 1
  };
}

function sendSettings() {
  var settings = readSettings();
  weatherEnabled = settings.WeatherEnabled === 1;
  Pebble.sendAppMessage(settings);
}

function fetchWeather(position) {
  if (!weatherEnabled) { busy = false; return; }
  var request = new XMLHttpRequest();
  request.open('GET', weather.weatherUrl(position.coords.latitude, position.coords.longitude), true);
  request.timeout = 12000;
  request.onload = function () {
    busy = false;
    if (!weatherEnabled || request.status !== 200) return;
    try {
      var message = weather.weatherMessage(JSON.parse(request.responseText), Math.floor(Date.now() / 1000));
      if (message) Pebble.sendAppMessage(message);
    } catch (error) { console.log('Window Seat forecast was unreadable'); }
  };
  request.onerror = request.ontimeout = function () { busy = false; };
  request.send();
}

function refresh() {
  if (!weatherEnabled || busy || !navigator.geolocation || Date.now() - lastAttempt < 60000) return;
  busy = true;
  lastAttempt = Date.now();
  navigator.geolocation.getCurrentPosition(fetchWeather, function () { busy = false; },
    {timeout: 12000, maximumAge: refreshPeriod, enableHighAccuracy: false});
}

Pebble.addEventListener('ready', function () {
  sendSettings();
  refresh();
  setInterval(refresh, refreshPeriod);
});
Pebble.addEventListener('appmessage', function (event) {
  if (event.payload && event.payload.WeatherRequest) refresh();
});
Pebble.addEventListener('showConfiguration', function () { Pebble.openURL(clay.generateUrl()); });
Pebble.addEventListener('webviewclosed', function (event) {
  if (!event || !event.response || event.response === 'CANCELLED') return;
  try { clay.getSettings(event.response, false); }
  catch (error) { return; }
  var wasEnabled = weatherEnabled;
  sendSettings();
  if (!wasEnabled && weatherEnabled) lastAttempt = 0;
  refresh();
});
