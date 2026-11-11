// The site is static and the script is small: the mobile menu and the colour
// scheme of the page. No tracker, no request, no cookie.

(function () {
  'use strict';

  // The mobile menu: a button that opens and closes the navigation.
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.getAttribute('data-open') === 'true';
      nav.setAttribute('data-open', open ? 'false' : 'true');
      toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
    });

    // The menu closes when the link is chosen: the page scrolls to the
    // section, and the menu must not stay over it.
    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) {
        nav.setAttribute('data-open', 'false');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.getAttribute('data-open') === 'true') {
        nav.setAttribute('data-open', 'false');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  // The theme: the page follows the system, and the button in the footer
  // switches to the other one for this visit.
  var root = document.documentElement;
  var stored = null;

  try {
    stored = window.localStorage.getItem('vibelauncher-theme');
  } catch (error) {
    stored = null;
  }

  if (stored === 'light' || stored === 'dark') {
    root.setAttribute('data-theme', stored);
  }

  var button = document.querySelector('.theme-toggle');

  if (button) {
    button.addEventListener('click', function () {
      var dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var current = root.getAttribute('data-theme');
      var next = current ? (current === 'dark' ? 'light' : 'dark') : (dark ? 'light' : 'dark');

      root.setAttribute('data-theme', next);

      try {
        window.localStorage.setItem('vibelauncher-theme', next);
      } catch (error) {
        // A blocked storage is not a reason to break the page.
      }

      button.setAttribute('aria-pressed', next === 'dark' ? 'true' : 'false');
    });
  }
})();
