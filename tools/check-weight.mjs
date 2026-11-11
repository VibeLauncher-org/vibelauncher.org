// Counts the bytes that the landing page transfers and checks that every
// local link and every asset of the pages exists.
//
//   node website/tools/check-weight.mjs [base-url]

import { readdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const BASE = process.argv[2] ?? 'http://127.0.0.1:8931';
const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));

const PAGES = ['index.html', 'download.html', 'privacy.html', '404.html'];

async function sizeOf(path) {
  const response = await fetch(`${BASE}/${path}`);
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  const body = await response.arrayBuffer();
  return body.byteLength;
}

function localAssets(html) {
  const found = new Set();
  const pattern = /(?:href|src)="([^"]+)"/g;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    const value = match[1];
    if (value.startsWith('http') || value.startsWith('mailto:') || value.startsWith('#')) {
      continue;
    }
    found.add(value.split('#')[0]);
  }
  return [...found];
}

for (const page of PAGES) {
  const response = await fetch(`${BASE}/${page}`);
  const html = await response.text();
  let total = Buffer.byteLength(html);

  const missing = [];
  for (const asset of localAssets(html)) {
    try {
      total += await sizeOf(asset);
    } catch (error) {
      missing.push(asset);
    }
  }

  console.log(
    `${page}: ${(total / 1024).toFixed(1)} KB transferred` +
      (missing.length > 0 ? `, MISSING: ${missing.join(', ')}` : ', all assets found')
  );
}

// The anchors of the landing page must exist on it.
const index = await (await fetch(`${BASE}/index.html`)).text();
const ids = new Set([...index.matchAll(/id="([^"]+)"/g)].map((m) => m[1]));
const anchors = [...index.matchAll(/href="#([^"]+)"/g)].map((m) => m[1]);
const broken = anchors.filter((anchor) => !ids.has(anchor));
console.log(
  `anchors: ${anchors.length} on the landing page` +
    (broken.length > 0 ? `, BROKEN: ${broken.join(', ')}` : ', all of them exist')
);

function countFiles(folder) {
  let count = 0;
  for (const entry of readdirSync(folder)) {
    const path = join(folder, entry);
    if (statSync(path).isDirectory()) count += countFiles(path);
    else count += 1;
  }
  return count;
}

console.log(`files in the site: ${countFiles(ROOT)}`);
