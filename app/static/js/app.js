/* ===================================================================
   Terminal Palette — homepage behaviour
   Theme data comes from the #theme-data JSON block rendered by
   app/themes.py. No hex values are declared in this file.
   =================================================================== */
(function () {
  'use strict';


  var FAV_KEY = 'tp:favorites';
  var SELECTED_KEY = 'tp:selected';
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
    suits:      document.getElementById('detail-suits'),
    suitsRow:   document.getElementById('detail-suits-row'),
    download:   document.getElementById('detail-download'),
    detailFav:  document.getElementById('detail-fav'),
    favLabel:   document.getElementById('detail-fav-label'),
    favCount:   document.getElementById('favorite-count'),
    headerFav:  document.getElementById('header-favorites'),
    live:       document.getElementById('live-region'),
    empty:      document.getElementById('grid-empty'),
    emptyTitle: document.getElementById('grid-empty-title'),
    emptyHint:  document.getElementById('grid-empty-hint'),
    gridTitle:  document.getElementById('themes-title'),
    appLabel:   document.getElementById('appearance-label'),
    appHint:    document.getElementById('appearance-hint'),
    appHeader:  document.getElementById('appearance-header'),
    search:     document.getElementById('theme-search'),
    clear:      document.getElementById('search-clear'),
    count:      document.getElementById('result-count'),
    pagination: document.getElementById('pagination'),
    pageStatus: document.getElementById('page-status'),
    pagePrev:   document.getElementById('page-prev'),
    pageNext:   document.getElementById('page-next')
  };

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

  // Wired before the theme-data guard: the guide and about pages carry the
  // same header toggle but no theme data, and the toggle has to work there
  // too. Everything below the guard is grid-and-details behaviour.
  document.addEventListener('click', function (e) {
    if (e.target.closest('.appearance-btn')) { toggleAppearance(); }
  });
  renderAppearance();

  var dataEl = document.getElementById('theme-data');
  if (!dataEl) { return; }

  var THEMES = JSON.parse(dataEl.textContent);
  var BY_ID = {};
  THEMES.forEach(function (t) { BY_ID[t.id] = t; });

  var CARDS = el.grid
    ? Array.prototype.slice.call(el.grid.querySelectorAll('.theme-card'))
    : [];

  /* ------------------------------------------------ shuffle ----- */

  // Unbiased Fisher-Yates. Mutates the array it is handed, which is always a
  // throwaway copy — never THEMES itself.
  function shuffle(list) {
    for (var i = list.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var swap = list[i];
      list[i] = list[j];
      list[j] = swap;
    }
    return list;
  }

  // The browsing order for this page load, decided once. Every filter, search
  // and pagination operation reads it; nothing reshuffles afterwards, so a new
  // order appears only on a fresh page load. `display_order` in themes.py is
  // untouched and remains the deterministic editorial order.
  var ORDER = shuffle(THEMES.map(function (t) { return t.id; }));

  // Move the server-rendered cards into the shuffled order. The markup is
  // reused as-is — no card is re-rendered or duplicated in JavaScript.
  function applyOrder() {
    if (!el.grid || !CARDS.length) { return; }

    var byId = {};
    CARDS.forEach(function (card) { byId[card.getAttribute('data-id')] = card; });

    var frag = document.createDocumentFragment();
    ORDER.forEach(function (id) {
      if (byId[id]) { frag.appendChild(byId[id]); }
    });
    el.grid.appendChild(frag);

    // CARDS drives filtering and pagination, so it has to agree with the DOM.
    CARDS = ORDER.map(function (id) { return byId[id]; }).filter(Boolean);
  }

  /* ------------------------------------------------ deep link --- */

  // The hash names a theme, e.g. /#oxblood. Only ids in the active set are
  // honoured; anything else is ignored without comment.
  function hashId() {
    var raw = window.location.hash.replace(/^#/, '');
    if (!raw) { return null; }
    var id;
    try { id = decodeURIComponent(raw); } catch (e) { id = raw; }
    return BY_ID[id] ? id : null;
  }

  // replaceState keeps the address bar in step without stacking history
  // entries, and without the scroll jump that assigning location.hash causes.
  function syncHash(id) {
    if (!HAS_GRID || !window.history || !window.history.replaceState) { return; }
    try {
      window.history.replaceState(window.history.state, '',
        window.location.pathname + window.location.search + '#' + id);
    } catch (e) {
      /* Some sandboxed contexts refuse replaceState; selection still works. */
    }
  }

  // The page holding the selected card. A linked theme moves pagination to
  // its card; the shuffled order itself never moves.
  function pageForSelected() {
    var i = matching.indexOf(selected);
    return i === -1 ? page : Math.floor(i / pageSize()) + 1;
  }

  // The theme grid only exists on the homepage. Everything gated on this is
  // grid behaviour: the shuffle, filters, pagination and hash linking.
  var HAS_GRID = !!el.grid;

  // The last selection, carried to the article pages. Never consulted on the
  // homepage, where the shuffle and the hash decide.
  function storedSelection() {
    try {
      var id = window.localStorage.getItem(SELECTED_KEY);
      return id && BY_ID[id] ? id : null;
    } catch (e) {
      return null;
    }
  }

  function rememberSelection(id) {
    try {
      window.localStorage.setItem(SELECTED_KEY, id);
    } catch (e) {
      /* Storage unavailable; the selection still applies for this page view. */
    }
  }

  // Homepage: a hash naming an active theme wins over the shuffle, and the
  // shuffle decides otherwise. Article pages: the stored selection, falling
  // back to the first theme in display_order. They never shuffle.
  var selected = HAS_GRID
    ? (hashId() || (ORDER.length ? ORDER[0] : null))
    : (storedSelection() || (THEMES.length ? THEMES[0].id : null));
  var mood = 'all';
  var query = '';
  // Never persisted: a reload always returns to All Themes.
  var favoritesView = false;
  var matching = [];
  var page = 1;
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
    // In Favorites view an unfavourited card leaves the result set at once.
    // render() re-clamps the page, refreshes the count, and reselects when the
    // selected card is no longer on screen.
    if (favoritesView) {
      computeMatches();
      render();
    }
    announce(BY_ID[id].name + (isFavorite(id) ? ' added to favorites' : ' removed from favorites'));
  }

  function renderFavorites() {
    if (el.favCount) { el.favCount.textContent = String(favorites.length); }
    // aria-pressed reports the view, not whether any favourites exist; the
    // existing .icon-btn[aria-pressed="true"] rule supplies the active state.
    if (el.headerFav && el.headerFav.tagName === 'BUTTON') {
      el.headerFav.setAttribute('aria-pressed', favoritesView ? 'true' : 'false');
      el.headerFav.setAttribute('aria-label',
        favoritesView ? 'Show all themes' : 'View favorites');
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

  // `silent` suppresses the live-region announcement for the selection made
  // during initialisation, which the user did not ask for.
  function selectTheme(id, silent) {
    var theme = BY_ID[id];
    if (!theme) { return; }
    selected = id;
    // Persisted on every change, load-time included: the article pages open
    // on whatever the homepage last showed.
    rememberSelection(id);

    // Card state, homepage only.
    if (el.grid) {
      Array.prototype.forEach.call(el.grid.querySelectorAll('.theme-card'), function (card) {
        var on = card.getAttribute('data-id') === id;
        card.classList.toggle('is-selected', on);
        var btn = card.querySelector('[data-select]');
        if (btn) { btn.setAttribute('aria-pressed', on ? 'true' : 'false'); }
      });
    }

    // Details panel text
    if (el.name) { el.name.textContent = theme.name; }
    if (el.desc) { el.desc.textContent = theme.description; }
    if (el.category) { el.category.textContent = theme.category; }
    if (el.created) { el.created.textContent = theme.created; }
    if (el.inspired) { el.inspired.textContent = theme.inspired_by; }
    if (el.version) { el.version.textContent = theme.version; }

    renderEnvironments(theme);
    renderColors(theme);
    renderDownload(theme);

    // Terminals
    applyTerminal(el.terminal, theme, '--term-bg', '--term-fg', '--term-green');
    applyTerminal(el.mini, theme, '--mini-bg', '--mini-fg', '--mini-accent');

    renderFavorites();
    // `silent` also marks the load-time selection, which must not rewrite the
    // address bar: a bare URL stays bare, so a reload still gets a fresh
    // shuffle rather than pinning whatever was shown last.
    if (!silent) {
      syncHash(id);
      announce(theme.name + ' selected');
    }
  }

  /* ------------------------------------------------ suits ------- */

  // uat and dr are initialisms; everything else is sentence case. index.html
  // applies the same rule for the server-rendered row.
  var ENV_UPPER = { uat: true, dr: true };

  function environmentLabel(env) {
    return ENV_UPPER[env]
      ? env.toUpperCase()
      : env.charAt(0).toUpperCase() + env.slice(1);
  }

  // A theme with no environments loses the row entirely rather than showing a
  // placeholder; `hidden` leaves no reserved space.
  function renderEnvironments(theme) {
    var envs = theme.environments || [];
    if (el.suits) { el.suits.textContent = envs.map(environmentLabel).join(', '); }
    if (el.suitsRow) { el.suitsRow.hidden = envs.length === 0; }
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

  /* ------------------------------------------------ download ---- */

  // The URL shape comes from the template's url_for, so the route lives in
  // routes.py alone and is never spelled out in JavaScript.
  var DOWNLOAD_TEMPLATE = el.download
    ? el.download.getAttribute('data-url-template')
    : null;

  function renderDownload(theme) {
    if (!el.download || !DOWNLOAD_TEMPLATE) { return; }
    el.download.href = DOWNLOAD_TEMPLATE.replace('__ID__', encodeURIComponent(theme.id));
    el.download.setAttribute('aria-label', 'Download .reg file for ' + theme.name);
  }

  function applyTerminal(node, theme, bgVar, fgVar, accentVar) {
    if (!node) { return; }
    node.style.setProperty(bgVar, theme.background.hex);
    node.style.setProperty(fgVar, theme.foreground.hex);
    node.style.setProperty(accentVar, theme.cursor.hex);
  }

  /* ------------------------------------------------ moods ------- */

  // Searchable text per theme, built once. `environments` is included so the
  // hidden metadata is findable, but it is never rendered anywhere.
  var HAYSTACK = {};
  THEMES.forEach(function (t) {
    HAYSTACK[t.id] = [t.name, t.description, t.category]
      .concat(t.moods, t.environments || [])
      .join(' ')
      .toLowerCase()
      // "late-night" should also answer to "late night".
      .replace(/-/g, ' ') + ' ' + t.moods.join(' ').toLowerCase();
  });

  // Favorites, mood and search resolve through this one predicate; a theme
  // must pass all three. Favorites view is a filter, not a separate mode, so
  // pagination, counting and rendering below are untouched by it.
  function matchesFilters(theme) {
    if (favoritesView && !isFavorite(theme.id)) { return false; }
    if (mood !== 'all' && theme.moods.indexOf(mood) === -1) { return false; }
    if (!query) { return true; }
    return HAYSTACK[theme.id].indexOf(query) !== -1;
  }

  /* ------------------------------------------------ pagination -- */

  // Page size = columns x rows. Boundaries mirror the grid breakpoints in
  // styles.css. Page counts are always derived from these, never hardcoded.
  var MQ_WIDE = window.matchMedia('(min-width: 1241px)');   // 4 columns
  var MQ_MED = window.matchMedia('(min-width: 1041px)');    // 3 columns
  var MQ_TABLET = window.matchMedia('(min-width: 561px)');  // 2 columns

  var PAGE_WIDE = 16;    // 4 x 4
  var PAGE_MED = 9;      // 3 x 3
  var PAGE_TABLET = 6;   // 2 x 3
  var PAGE_MOBILE = 3;   // 1 x 3

  function pageSize() {
    if (MQ_WIDE.matches) { return PAGE_WIDE; }
    if (MQ_MED.matches) { return PAGE_MED; }
    if (MQ_TABLET.matches) { return PAGE_TABLET; }
    return PAGE_MOBILE;
  }

  function totalPages() {
    return Math.max(1, Math.ceil(matching.length / pageSize()));
  }

  function goToPage(n) {
    page = n;
    render();
  }

  /* ------------------------------------------------ rendering --- */

  // Filters resolve first, producing the matching set; pagination then
  // applies to that set.
  function computeMatches() {
    matching = CARDS
      .filter(function (card) { return matchesFilters(BY_ID[card.getAttribute('data-id')]); })
      .map(function (card) { return card.getAttribute('data-id'); });
  }

  function render() {
    var pages = totalPages();
    page = Math.min(Math.max(page, 1), pages);

    var start = (page - 1) * pageSize();
    var onPage = matching.slice(start, start + pageSize());

    CARDS.forEach(function (card) {
      // `hidden` removes the card from the tab order as well as the layout.
      card.hidden = onPage.indexOf(card.getAttribute('data-id')) === -1;
    });

    Array.prototype.forEach.call(document.querySelectorAll('[data-mood]'), function (btn) {
      var on = btn.getAttribute('data-mood') === mood;
      btn.classList.toggle('is-selected', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });

    if (el.empty) {
      el.empty.hidden = matching.length > 0;
      if (el.emptyTitle) {
        el.emptyTitle.textContent = favoritesView
          ? 'No favorite themes yet.'
          : 'No themes in this mood.';
      }
      // The hint only makes sense against an empty Favorites view.
      if (el.emptyHint) { el.emptyHint.hidden = !favoritesView; }
    }
    if (el.clear) { el.clear.hidden = !query; }
    // The count always reports total matches, never the current page.
    if (el.count) {
      el.count.textContent = matching.length + (matching.length === 1 ? ' theme' : ' themes');
    }

    if (el.pagination) {
      el.pagination.hidden = pages <= 1;
      if (el.pageStatus) { el.pageStatus.textContent = 'Page ' + page + ' of ' + pages; }
      if (el.pagePrev) { el.pagePrev.disabled = page <= 1; }
      if (el.pageNext) { el.pageNext.disabled = page >= pages; }
    }

    // Keep the details panel on a card the user can actually see.
    if (onPage.length && onPage.indexOf(selected) === -1) {
      selectTheme(onPage[0]);
    }
  }

  function applyFilters() {
    page = 1;
    computeMatches();
    render();
  }

  // Entering or leaving resets mood and search to a known state, so the view
  // is always deterministic. applyFilters() then resets to page 1.
  function setFavoritesView(on) {
    favoritesView = !!on;
    mood = 'all';
    query = '';
    // Set directly rather than via clearSearch(), which would steal focus.
    if (el.search) { el.search.value = ''; }
    if (el.gridTitle) { el.gridTitle.textContent = favoritesView ? 'Favorites' : 'Themes'; }
    renderFavorites();
    applyFilters();
    announce(favoritesView ? 'Showing favorites' : 'Showing all themes');
  }

  function setMood(key) {
    mood = key;
    applyFilters();
  }

  function setQuery(value) {
    query = value.trim().toLowerCase();
    applyFilters();
  }

  function clearSearch() {
    if (!el.search) { return; }
    el.search.value = '';
    setQuery('');
    el.search.focus();
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


    if (el.detailFav && e.target.closest('#detail-fav')) {
      toggleFavorite(selected);
      return;
    }

    if (el.clear && e.target.closest('#search-clear')) { clearSearch(); return; }

    // Only the homepage's button toggles; the article pages render an anchor,
    // which is left to navigate.
    if (HAS_GRID && e.target.closest('#header-favorites')) {
      setFavoritesView(!favoritesView);
      return;
    }

    if (e.target.closest('#page-prev')) { goToPage(page - 1); return; }
    if (e.target.closest('#page-next')) { goToPage(page + 1); return; }

    var moodBtn = e.target.closest('[data-mood]');
    if (moodBtn) { setMood(moodBtn.getAttribute('data-mood')); return; }

    // Placeholder controls must not navigate or act.
    var placeholder = e.target.closest('[data-placeholder]');
    if (placeholder) { e.preventDefault(); }
  });

  /* ------------------------------------------------ init --------- */
  // Both previews, the RGB values and the details panel reflect the first
  // theme in the shuffled order, so each page load opens on a different one.
  if (el.search) {
    el.search.addEventListener('input', function (e) { setQuery(e.target.value); });
    el.search.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && el.search.value) {
        e.preventDefault();
        clearSearch();
      }
    });
  }

  // A breakpoint change alters the page size; recount pages and clamp.
  [MQ_WIDE, MQ_MED, MQ_TABLET].forEach(function (mq) {
    var onChange = function () { render(); };
    if (mq.addEventListener) { mq.addEventListener('change', onChange); }
    else if (mq.addListener) { mq.addListener(onChange); }
  });

  // Editing the hash, or arriving at a different one, selects that theme in
  // place. Filters and search are left exactly as they are.
  if (HAS_GRID) { window.addEventListener('hashchange', function () {
    var id = hashId();
    if (!id || id === selected) { return; }
    selectTheme(id);
    // Only move pagination when the card is actually in the current result
    // set; if a filter hides it, the panel updates and the grid stays put.
    if (matching.indexOf(id) !== -1) {
      page = pageForSelected();
      render();
    }
  }); }

  applyOrder();
  if (selected) { selectTheme(selected, true); }

  // ?view=favorites arrives from the header link on the article pages. A theme
  // hash still wins, exactly as it does today. The parameter is stripped once
  // applied so a reload returns to All Themes — the view is never persisted.
  function openFavoritesFromQuery() {
    if (!HAS_GRID) { return false; }
    if (window.location.search.indexOf('view=favorites') === -1) { return false; }
    if (window.history && window.history.replaceState) {
      try {
        window.history.replaceState(window.history.state, '',
          window.location.pathname + window.location.hash);
      } catch (e) {
        /* Sandboxed context; the parameter simply stays in the address bar. */
      }
    }
    return !hashId();
  }
  var openFavorites = openFavoritesFromQuery();
  renderFavorites();
  if (HAS_GRID && openFavorites) {
    setFavoritesView(true);
  } else if (HAS_GRID) {
    // Not applyFilters(): that resets to page 1, which would strand a linked
    // theme on a later page. Same work, then pagination opens on its card.
    computeMatches();
    page = pageForSelected();
    render();
  }
})();
