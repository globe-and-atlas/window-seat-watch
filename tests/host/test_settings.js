'use strict';
const assert = require('node:assert/strict');
const Module = require('node:module');
const path = require('node:path');
const root = path.resolve(__dirname, '../../watchface');
const keys = {};
require(path.join(root, 'package.json')).pebble.messageKeys.forEach((key, index) => {
  keys[key] = 10000 + index;
});
const load = Module._load;
Module._load = function (name) {
  if (name === 'message_keys') return keys;
  if (name === '@rebble/clay') return load.call(this, path.join(root, 'node_modules/@rebble/clay/src/js/index.js'));
  return load.apply(this, arguments);
};
const events = {};
const stored = {};
const sent = [];
const requestLog = [];
global.setInterval = () => 1;
Object.defineProperty(global, 'navigator', {
  configurable: true,
  value: { geolocation: { getCurrentPosition: (success) => success({coords: {latitude: 41.88, longitude: -87.63}}) } }
});
global.localStorage = {
  getItem: key => stored[key] || null,
  setItem: (key, value) => { stored[key] = value; }
};
global.Pebble = {
  addEventListener: (name, handler) => { events[name] = handler; },
  sendAppMessage: (packet) => sent.push(packet),
  openURL: url => assert(url.startsWith('data:text/html')),
  getAccountToken: () => 'test',
  getWatchToken: () => 'test',
  getActiveWatchInfo: () => ({
    platform: 'gabbro', model: 'gabbro', language: 'en_US',
    firmware: {major: 4, minor: 33, patch: 1}
  })
};
global.XMLHttpRequest = class {
  open(method, url) { assert.equal(method, 'GET'); requestLog.push(url); }
  send() {
    const now = Math.floor(Date.now() / 1000);
    const hour = Math.floor(now / 3600) * 3600;
    this.status = 200;
    this.responseText = JSON.stringify({
      current: {time: now, weather_code: 61},
      hourly: {time: [hour, hour+3600, hour+7200, hour+10800], weather_code: [61, 61, 2, 0]}
    });
    this.onload();
  }
};
require(path.join(root, 'src/pkjs/index.js'));
events.ready();
assert.deepEqual(sent[0], {TimeFormat: 0, DateFormat: 0, SceneMode: 0, Route: 0, WeatherEnabled: 1});
assert.equal(sent[1].CurrentKind, 3);
assert.equal(sent[1].Forecast0, 3);
assert.equal(requestLog.length, 1);
events.showConfiguration();
events.webviewclosed({response:'CANCELLED'});
assert.equal(sent.length, 2);
events.webviewclosed({response:encodeURIComponent(JSON.stringify({
  TimeFormat: {value:'2'}, DateFormat:{value:'3'}, SceneMode:{value:'4'}, Route:{value:'16'}, WeatherEnabled:{value:false}
}))});
assert.deepEqual(sent[2], {TimeFormat: 2, DateFormat: 3, SceneMode: 4, Route: 16, WeatherEnabled: 0});
events.appmessage({payload:{WeatherRequest:1}});
assert.equal(requestLog.length, 1);
console.log('Window Seat real Clay Save/Cancel and mocked phone-to-watch weather path passed');
