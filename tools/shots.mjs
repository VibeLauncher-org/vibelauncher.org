// Takes the screenshots of the site: the landing page in the dark and in the
// light theme, and the other pages.
//
//   node website/tools/shots.mjs [base-url] [out-folder]

import { spawn } from 'node:child_process';
import { mkdirSync, rmSync } from 'node:fs';
import { writeFileSync } from 'node:fs';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const BASE = process.argv[2] ?? 'http://127.0.0.1:8931';
const OUT = process.argv[3] ?? 'D:\\_TEMP\\vl-shots';
const PORT = 9455;

const SHOTS = [
  { name: 'index-dark', page: 'index.html', width: 1440, height: 1600, scheme: 'dark' },
  { name: 'index-light', page: 'index.html', width: 1440, height: 1600, scheme: 'light' },
  { name: 'download', page: 'download.html', width: 1440, height: 1400, scheme: 'dark' },
  { name: 'privacy', page: 'privacy.html', width: 1440, height: 1600, scheme: 'dark' },
  { name: 'index-narrow', page: 'index.html', width: 390, height: 1400, scheme: 'dark' },
  { name: 'index-full', page: 'index.html', width: 1440, height: 900, scheme: 'dark', full: true },
];

mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, [
  '--headless=new',
  '--disable-gpu',
  '--hide-scrollbars',
  '--no-first-run',
  '--remote-allow-origins=*',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}\\profile`,
  'about:blank',
]);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

let nextId = 1;
const pending = new Map();

function send(socket, method, params = {}) {
  const id = nextId++;
  socket.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    pending.set(id, resolve);
    setTimeout(() => {
      if (pending.has(id)) {
        pending.delete(id);
        reject(new Error(`no answer for ${method}`));
      }
    }, 20000).unref();
  });
}

async function main() {
  let list = [];
  for (let attempt = 0; attempt < 40; attempt++) {
    try {
      list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      if (list.length > 0) break;
    } catch (error) {
      // The browser is not listening yet.
    }
    await sleep(250);
  }

  const page = list.find((t) => t.type === 'page');
  const socket = new WebSocket(page.webSocketDebuggerUrl);

  await new Promise((resolve, reject) => {
    socket.onopen = resolve;
    socket.onerror = reject;
  });

  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.id !== undefined && pending.has(message.id)) {
      pending.get(message.id)(message);
      pending.delete(message.id);
    }
  };

  await send(socket, 'Page.enable');

  for (const shot of SHOTS) {
    await send(socket, 'Emulation.setDeviceMetricsOverride', {
      width: shot.width,
      height: shot.height,
      deviceScaleFactor: 1,
      mobile: shot.width < 700,
    });
    await send(socket, 'Emulation.setEmulatedMedia', {
      features: [{ name: 'prefers-color-scheme', value: shot.scheme }],
    });
    await send(socket, 'Page.navigate', { url: `${BASE}/${shot.page}` });
    await sleep(1500);

    const result = await send(socket, 'Page.captureScreenshot', {
      format: 'png',
      captureBeyondViewport: shot.full === true,
    });
    const data = result.result.data;
    writeFileSync(`${OUT}\\${shot.name}.png`, Buffer.from(data, 'base64'));
    console.log(`${shot.name}.png written`);
  }

  socket.close();
  chrome.kill();
  try {
    rmSync(`${OUT}\\profile`, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  } catch (error) {
    // The profile of a browser that has just been killed may still be locked.
  }
}

main().catch((error) => {
  console.error(error);
  chrome.kill();
  process.exit(1);
});
