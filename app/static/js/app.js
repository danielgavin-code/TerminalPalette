/* ===================================================================
   Terminal Palette — homepage behaviour
   Theme data comes from the #theme-data JSON block rendered by
   app/themes.py. No hex values are declared in this file.
   =================================================================== */
(function () {
  'use strict';

  var dataEl = document.getElementById('theme-data');
  if (!dataEl) { return; }

  var THEMES = JSON.parse(dataEl.textContent);
  var BY_ID = {};
  THEMES.forEach(function (t) { BY_ID[t.id] = t; });

  var FAV_KEY = 'tp:favorites';
  var APPEARANCE_KEY = 'tp:appearance';

  var el = {
    grid:       document.getElementById('theme-grid'),
    terminal:   document.getElementById('terminal'),
    mini:       document.getElementById('mini-terminal'),
    name:       document.getElementById('detail-name'),
    desc:       document.getElementById('detail-desc'),
    category:   document.getElementById('detail-category'),
    created:    document.getElementById('detail-created'),
    inspired:   document.getElementById('detail-inspired'),
    version:    document.getElementById('detail-version'),
    detailFav:  document.getElementById('detail-fav'),
    favLabel:   document.getElementById('detail-fav-label'),
    favCount:   document.getElementById('favorite-count'),
    headerFav:  document.getElementById('header-favorites'),
    live:       document.getElementById('live-region'),
    empty:      document.getElementById('grid-empty'),
    appLabel:   document.getElementById('appearance-label'),
    appHint:    document.getElementById('appearance-hint'),
    appHeader:  document.getElementById('appearance-header')
  };

  var selected = THEMES.length ? THEMES[0].id : null;
  var mood = 'all';
  var favorites = loadFavorites();

  /* ------------------------------------------------ favorites ---- */

  function loadFavorites() {
    try {
      var raw = window.localStorage.getItem(FAV_KEY);
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list.filter(function (s) { return !!BY_ID[s]; }) : [];
    } catch (e) {
      return [];
    }
  }

  function saveFavorites() {
    try {
      window.localStorage.setItem(FAV_KEY, JSON.stringify(favorites));
    } catch (e) {
      /* Storage unavailable (private mode, blocked). State stays in memory. */
    }
  }

  function isFavorite(id) { return favorites.indexOf(id) !== -1; }

  function toggleFavorite(id) {
    var i = favorites.indexOf(id);
    if (i === -1) { favorites.push(id); } else { favorites.splice(i, 1); }
    saveFavorites();
    renderFavorites();
    announce(BY_ID[id].name + (isFavorite(id) ? ' added to favorites' : ' removed from favorites'));
  }

  function renderFavorites() {
    if (el.favCount) { el.favCount.textContent = String(favorites.length); }
    if (el.headerFav) {
      el.headerFav.setAttribute('aria-pressed', favorites.length > 0 ? 'true' : 'false');
    }

    Array.prototype.forEach.call(document.querySelectorAll('[data-fav]'), function (btn) {
      var id = btn.getAttribute('data-fav');
      var on = isFavorite(id);
      var theme = BY_ID[id];
      if (!theme) { return; }
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.setAttribute('aria-label', (on ? 'Remove ' : 'Add ') + theme.name + (on ? ' from favorites' : ' to favorites'));
    });

    if (el.detailFav) {
      var on = isFavorite(selected);
      el.detailFav.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (el.favLabel) {
        el.favLabel.textContent = on ? 'Remove from favorites' : 'Add to favorites';
      }
    }
  }

  /* ------------------------------------------------ selection ---- */

  function selectTheme(id) {
    var theme = BY_ID[id];
    if (!theme) { return; }
    selected = id;

    // Card state
    Array.prototype.forEach.call(el.grid.querySelectorAll('.theme-card'), function (card) {
      var on = card.getAttribute('data-id') === id;
      card.classList.toggle('is-selected', on);
      var btn = card.querySelector('[data-select]');
      if (btn) { btn.setAttribute('aria-pressed', on ? 'true' : 'false'); }
    });

    // Details panel text
    if (el.name) { el.name.textContent = theme.name; }
    if (el.desc) { el.desc.textContent = theme.description; }
    if (el.category) { el.category.textContent = theme.category; }
    if (el.created) { el.created.textContent = theme.created; }
    if (el.inspired) { el.inspired.textContent = theme.inspired_by; }
    if (el.version) { el.version.textContent = theme.version; }

    renderColors(theme);

    // Terminals
    applyTerminal(el.terminal, theme, '--term-bg', '--term-fg', '--term-green');
    applyTerminal(el.mini, theme, '--mini-bg', '--mini-fg', '--mini-accent');

    renderFavorites();
    announce(theme.name + ' selected');
  }

  /* ------------------------------------------------ colours ----- */

  var CHANNELS = ['r', 'g', 'b'];
  var GROUPS = ['background', 'foreground', 'cursor'];

  // Each functional colour arrives from themes.py as {hex, rgb:[r,g,b]}.
  function rgbFor(key) {
    var rgb = BY_ID[selected][key].rgb;
    return { r: rgb[0], g: rgb[1], b: rgb[2] };
  }

  function renderColors(theme) {
    GROUPS.forEach(function (key) {
      var colour = theme[key];
      var chip = document.querySelector('[data-chip="' + key + '"]');
      if (chip) { chip.style.background = colour.hex; }

      CHANNELS.forEach(function (ch, i) {
        var node = document.querySelector('[data-ch="' + key + '-' + ch + '"]');
        if (node) { node.textContent = String(colour.rgb[i]); }
      });
    });
  }

  function applyTerminal(node, theme, bgVar, fgVar, accentVar) {
    if (!node) { return; }
    node.style.setProperty(bgVar, theme.background.hex);
    node.style.setProperty(fgVar, theme.foreground.hex);
    node.style.setProperty(accentVar, theme.cursor.hex);
  }

  /* ------------------------------------------------ moods ------- */

  function matchesMood(theme, key) {
    return key === 'all' || theme.moods.indexOf(key) !== -1;
  }

  function applyMood(key) {
    mood = key;
    var visible = [];

    Array.prototype.forEach.call(el.grid.querySelectorAll('.theme-card'), function (card) {
      var theme = BY_ID[card.getAttribute('data-id')];
      var show = matchesMood(theme, key);
      // `hidden` removes the card from the tab order as well as the layout.
      card.hidden = !show;
      if (show) { visible.push(theme.id); }
    });

    Array.prototype.forEach.call(document.querySelectorAll('[data-mood]'), function (btn) {
      var on = btn.getAttribute('data-mood') === key;
      btn.classList.toggle('is-selected', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });

    if (el.empty) { el.empty.hidden = visible.length > 0; }

    // Keep the details panel on something the user can actually see.
    if (visible.length && visible.indexOf(selected) === -1) {
      selectTheme(visible[0]);
    }

    announce(visible.length
      ? visible.length + (visible.length === 1 ? ' theme' : ' themes') + ' shown'
      : 'No themes in this mood');
  }

  /* ------------------------------------------------ appearance -- */

  function currentAppearance() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function renderAppearance() {
    var dark = currentAppearance() === 'dark';
    if (el.appLabel) { el.appLabel.textContent = dark ? 'Dark' : 'Light'; }
    if (el.appHint) {
      el.appHint.textContent = dark ? ', switch to light mode' : ', switch to dark mode';
    }
    if (el.appHeader) {
      el.appHeader.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }

  function toggleAppearance() {
    var next = currentAppearance() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try {
      window.localStorage.setItem(APPEARANCE_KEY, next);
    } catch (e) {
      /* Storage unavailable; the choice still applies for this page view. */
    }
    renderAppearance();
    announce(next === 'dark' ? 'Dark mode on' : 'Light mode on');
  }

  /* ------------------------------------------------ clipboard ---- */

  function copyValue(text, btn) {
    function done() {
      btn.classList.add('is-copied');
      window.setTimeout(function () { btn.classList.remove('is-copied'); }, 1400);
      announce(text + ' copied to clipboard');
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
    } else {
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      done();
    } catch (e) {
      announce('Copy failed. The value is ' + text);
    }
    document.body.removeChild(ta);
  }

  function announce(message) {
    if (el.live) { el.live.textContent = message; }
  }

  /* ------------------------------------------------ events ------- */

  if (el.grid) {
    el.grid.addEventListener('click', function (e) {
      var fav = e.target.closest('[data-fav]');
      if (fav) { toggleFavorite(fav.getAttribute('data-fav')); return; }

      var card = e.target.closest('.theme-card');
      if (card) { selectTheme(card.getAttribute('data-id')); }
    });
  }

  document.addEventListener('click', function (e) {
    // Single channel, e.g. "background-r" -> "242"
    var one = e.target.closest('[data-copy-value]');
    if (one) {
      var parts = one.getAttribute('data-copy-value').split('-');
      copyValue(String(rgbFor(parts[0])[parts[1]]), one);
      return;
    }

    // Whole group -> "242, 240, 224"
    var trio = e.target.closest('[data-copy-rgb]');
    if (trio) {
      var rgb = rgbFor(trio.getAttribute('data-copy-rgb'));
      copyValue(CHANNELS.map(function (ch) { return rgb[ch]; }).join(', '), trio);
      return;
    }

    if (el.detailFav && e.target.closest('#detail-fav')) {
      toggleFavorite(selected);
      return;
    }

    var moodBtn = e.target.closest('[data-mood]');
    if (moodBtn) { applyMood(moodBtn.getAttribute('data-mood')); return; }

    if (e.target.closest('.appearance-btn')) { toggleAppearance(); return; }

    // Placeholder controls must not navigate or act.
    var placeholder = e.target.closest('[data-placeholder]');
    if (placeholder) { e.preventDefault(); }
  });

  /* ------------------------------------------------ init --------- */
  // The hero terminal keeps its default charcoal palette until a theme is
  // chosen; the mini preview reflects the selected theme from the start.
  applyTerminal(el.mini, BY_ID[selected], '--mini-bg', '--mini-fg', '--mini-accent');
  renderColors(BY_ID[selected]);
  renderFavorites();
  renderAppearance();
})();
