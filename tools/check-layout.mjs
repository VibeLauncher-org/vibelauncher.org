// Checks the site at the widths of the acceptance criteria with the Chrome
// DevTools Protocol: the real layout width is set, the page is measured and a
// screenshot is taken.
//
//   node website/tools/check-layout.mjs [url]
//
// It reports the horizontal overflow, the width of the page and the errors of
// the console.

import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const URL_UNDER_TEST = process.argv[2] ?? 'http://127.0.0.1:8931/index.html';
const WIDTHS = [320, 768, 1440];
const PORT = 9333;

const profile = mkdtempSync(join(tmpdir(), 'vl-layout-'));

const chrome = spawn(CHROME, [
  '--headless=new',
  '--disable-gpu',
  '--hide-scrollbars',
  '--no-first-run',
  '--no-default-browser-check',
  '--remote-allow-origins=*',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`,
  'about:blank',
]);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function targets() {
  const response = await fetch(`http://127.0.0.1:${PORT}/json/list`);
  return response.json();
}

let socket;
let nextId = 1;
const pending = new Map();

function send(method, params = {}) {
  const id = nextId++;
  socket.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    pending.set(id, resolve);
    setTimeout(() => {
      if (pending.has(id)) {
        pending.delete(id);
        reject(new Error(`no answer for ${method}`));
      }
    }, 15000).unref();
  });
}

async function evaluate(expression) {
  const result = await send('Runtime.evaluate', {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  return result?.result?.result?.value;
}

async function main() {
  const consoleErrors = [];
  let list = [];
  for (let attempt = 0; attempt < 40; attempt++) {
    try {
      list = await targets();
      if (list.length > 0) break;
    } catch (error) {
      // The browser is not listening yet.
    }
    await sleep(250);
  }

  const page = list.find((t) => t.type === 'page');
  if (!page) throw new Error('no page target');

  socket = new WebSocket(page.webSocketDebuggerUrl);

  await new Promise((resolve, reject) => {
    socket.onopen = resolve;
    socket.onerror = reject;
  });

  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.method === 'Log.entryAdded' && message.params.entry.level === 'error') {
      consoleErrors.push(message.params.entry.text);
    }
    if (
      message.method === 'Runtime.exceptionThrown' &&
      message.params.exceptionDetails?.text
    ) {
      consoleErrors.push(message.params.exceptionDetails.text);
    }
    if (message.id !== undefined && pending.has(message.id)) {
      pending.get(message.id)(message);
      pending.delete(message.id);
    }
  };

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Log.enable');

  for (const width of WIDTHS) {
    await send('Emulation.setDeviceMetricsOverride', {
      width,
      height: 900,
      deviceScaleFactor: 1,
      mobile: width < 700,
    });
    await send('Page.navigate', { url: URL_UNDER_TEST });
    await sleep(1200);

    const report = await evaluate(`(() => {
      const doc = document.documentElement;
      const wide = [...document.querySelectorAll('body *')]
        .filter((el) => el.getBoundingClientRect().right > doc.clientWidth + 1)
        .map((el) => el.tagName.toLowerCase() + '.' + (el.className || '') )
        .slice(0, 8);
      return {
        clientWidth: doc.clientWidth,
        scrollWidth: doc.scrollWidth,
        scrollHeight: doc.scrollHeight,
        overflowing: wide,
      };
    })()`);

    const overflow = report.scrollWidth - report.clientWidth;
    console.log(
      `${width}px: page=${report.scrollWidth} viewport=${report.clientWidth} ` +
        `overflow=${overflow > 0 ? 'YES ' + overflow + 'px ' + report.overflowing.join(', ') : 'no'}`
    );
  }

  if (consoleErrors.length > 0) {
    console.log('console errors:');
    for (const error of consoleErrors) console.log(`  ${error}`);
  } else {
    console.log('console errors: none');
  }

  socket.close();
  chrome.kill();
  try {
    rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  } catch (error) {
    // The profile of a browser that has just been killed may still be locked.
  }
}

main().catch((error) => {
  console.error(error);
  chrome.kill();
  process.exit(1);
});
