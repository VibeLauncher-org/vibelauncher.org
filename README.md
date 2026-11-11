# The website of VibeLauncher

The public site of the project: <https://vibelauncher.org>. It is a static
site — plain HTML, CSS and a little vanilla JavaScript. There is no framework,
no bundler and no build step: the files of this folder are the site.

## The pages

| File | What it is |
|---|---|
| `index.html` | The landing page: the features, the modpack formats, Vibefork, the privacy, the downloads and the FAQ |
| `download.html` | The packages for the three systems and what to expect on the first start |
| `privacy.html` | The privacy policy: the summary, the local data, the table of the requests, the telemetry and the contact |
| `404.html` | The page that the server shows for an unknown address |
| `robots.txt` | The rules for the crawlers and the pointer to the sitemap |
| `sitemap.xml` | The addresses of the pages |

## The assets

| Path | What it is |
|---|---|
| `assets/css/base.css` | The tokens, the reset and the typography |
| `assets/css/chrome.css` | The header, the buttons and the footer |
| `assets/css/sections.css` | The sections of the landing page |
| `assets/css/pages.css` | The list of the points and the table of the privacy policy |
| `assets/js/main.js` | The mobile menu and the theme switch |
| `assets/fonts/` | The fonts of the project, cut down to the glyphs of the site and packed into WOFF2, with their OFL licences |
| `assets/icons/` | The mark of the launcher, the wordmark in two colours and the favicon |
| `assets/img/og.png` | The image of the Open Graph: 1200×630 |

The site makes no request to any third party: no tracker, no font from a CDN,
no embedded video. The only link that leaves the page is the one to the releases
on GitHub.

## The tools

The scripts in `tools/` build and check the site. They need Python with
`fonttools`, `brotli`, `Pillow` and `html5lib`, and Node.js for the checks that
drive Chrome over the DevTools Protocol.

```powershell
# the fonts: the glyphs of the site, cut down and packed into WOFF2
python website/tools/build_assets.py

# the Open Graph image and the favicon
python website/tools/build_og.py

# the HTML must have no error
python website/tools/check_html.py

# the contrast of the pairs of colours must be at least 4.5:1
python website/tools/check_contrast.py

# the checks below need the site to be served:
#   cd website; python -m http.server 8931
node website/tools/check-layout.mjs http://127.0.0.1:8931/index.html
node website/tools/check-weight.mjs http://127.0.0.1:8931
node website/tools/shots.mjs http://127.0.0.1:8931
```

`check-layout.mjs` measures the page at 320, 768 and 1440 pixels and reports the
horizontal overflow and the errors of the console. `check-weight.mjs` counts the
bytes that a page transfers and checks that every local asset exists.
`shots.mjs` takes the screenshots of the pages in both themes.

## The screenshot of the launcher

The frame of the launcher in the hero is a placeholder: the real image goes to
`assets/img/launcher-main.webp`, and the frame takes it as soon as the file is
there.
