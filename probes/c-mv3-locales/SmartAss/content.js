(function () {
  'use strict';

  const SORT_KEY = 'dstSorterEnabled';
  const MODE_KEY = 'dstSorterMode';
  const AUTOLOAD_KEY = 'dstSorterAutoLoad';

  // ── Sort mode definitions ───────────────────────────────────────
  // Icon CSS classes: ico-pri = primary (large), ico-sec = secondary (small)
  // AMO Security Fix: badgeIcons als DOM-Builder-Funktionen statt innerHTML-Strings
  // Jedes Icon-Element wird per createElement/textContent erzeugt (kein innerHTML)
  function _mkSpan(cls, color, text) {
    const s = document.createElement('span');
    s.className = cls;
    if (color) s.style.color = color;
    s.textContent = text;
    return s;
  }
  // ── grouped toggle buttons ─────────────────────────────
  // Instead of 5 separate sort badges we now render only 3 sort buttons
  // Each button owns several sub-modes and
  // cycles through them on every click:
  // • Balance : Balance: Top ↔ Balance: Low
  // • Likes : Likes: Top ↔ Likes: Low
  // • Timeline : Timeline: New ↔ Timeline: Old (2-way toggle)
  //
  // MODE_DEFS: label + icon builder for every individual sort mode.
  // The two Balance triangles keep a FIXED position (green ▲ left,
  // red ▼ right). Only their SIZE changes with the selected sub-mode — the
  // active direction's triangle grows (ico-pri = big), the other shrinks
  // (ico-sec = small). Nothing moves, so switching modes is a minimal visual
  // change. Labels use the "Kategorie: Wert" format.
  const MODE_DEFS = {
    'balance-top': {
      label: 'Balance: Top',
      buildIcon: function (p) {
        p.appendChild(_mkSpan('ico-pri', '#2e7d32', '\u25B2'));
        p.appendChild(_mkSpan('ico-sec', '#c62828', '\u25BC'));
      },
    },
    'balance-flop': {
      label: 'Balance: Low',
      buildIcon: function (p) {
        p.appendChild(_mkSpan('ico-sec', '#2e7d32', '\u25B2'));
        p.appendChild(_mkSpan('ico-pri', '#c62828', '\u25BC'));
      },
    },
    'positive-only': {
      label: 'Likes: Top',
      buildIcon: function (p) {
        p.appendChild(_mkSpan('ico-pri', '#2e7d32', '\u25B2'));
      },
    },
    'negative-only': {
      label: 'Likes: Low',
      buildIcon: function (p) {
        p.appendChild(_mkSpan('ico-pri', '#c62828', '\u25BC'));
      },
    },
    // the Timeline badge now shows a single DIRECTION arrow instead of
    // the static clock. New → ⇥ (U+21E5, rightwards arrow to bar = "to the end"),
    // Old → ⇤ (U+21E4, leftwards arrow to bar = "to the beginning"). The arrow
    // uses color=null so it inherits the label's text colour (neutral, no
    // red/green semantics — Timeline is intentionally neutral). On mode switch
    // the single glyph flips direction (like the Likes badge), so arrow+label
    // stay centred as one unit and nothing else in the badge shifts.
    'chronological-new': {
      label: 'Timeline: New',
      buildIcon: function (p) {
        p.appendChild(_mkSpan('ico-pri', null, '\u21E5'));
      },
    },
    'chronological-old': {
      label: 'Timeline: Old',
      buildIcon: function (p) {
        p.appendChild(_mkSpan('ico-pri', null, '\u21E4'));
      },
    },
  };

  // modes that sort "worst first" → the active badge turns RED.
  const LOW_MODES = ['balance-flop', 'negative-only'];

  // BUTTON_GROUPS: one badge per entry; each click advances to the next mode.
  const BUTTON_GROUPS = [
    { id: 'balance', modes: ['balance-top', 'balance-flop'] },
    { id: 'likes', modes: ['positive-only', 'negative-only'] },
    { id: 'timeline', modes: ['chronological-new', 'chronological-old'] },
  ];

  // Build dots indicator to show multi-mode capability.
  // Returns a <span class="dots-indicator"> containing one real CSS circle
  // per sub-mode (filled = active, hollow = inactive). The dots are centered
  // BELOW the button text (see CSS) so they never shift horizontally when the
  // label length changes and stay clear of the thumb-tap zone on mobile.
  function buildDotsIndicator(group, currentMode) {
    const span = document.createElement('span');
    span.className = 'dots-indicator';

    const currentIndex = group.modes.indexOf(currentMode);
    if (currentIndex === -1) return span; // safety fallback

    for (let i = 0; i < group.modes.length; i++) {
      const dot = document.createElement('span');
      dot.className = 'dst-dot' + (i === currentIndex ? ' filled' : '');
      span.appendChild(dot);
    }
    return span;
  }

  const ALL_MODES = Object.keys(MODE_DEFS);

  // Remembers the last-selected sub-mode per button group so a button keeps
  // showing a sensible label/icon even while another button is the active one.
  const groupSelection = {
    balance: 'balance-top',
    likes: 'positive-only',
    timeline: 'chronological-new',
  };

  function getGroupForMode(mode) {
    for (let i = 0; i < BUTTON_GROUPS.length; i++) {
      if (BUTTON_GROUPS[i].modes.indexOf(mode) !== -1) return BUTTON_GROUPS[i];
    }
    return null;
  }

  // Keep groupSelection in sync with the currently active sortMode.
  function syncGroupSelection() {
    const g = getGroupForMode(sortMode);
    if (g) groupSelection[g.id] = sortMode;
  }

  // CSS injected into shadow DOM: icon hierarchy, badge bar, animation, hide old buttons
  const ICON_STYLE_CSS = `
 /* Hide old tab navigation buttons (Alle Postings, Aelteste, Plus, Minus) */
 dst-forum--tabnavigation { display: none !important; }

 /* NOTE: Reply thread sections (SECTION.thread) are now attached as siblings
 of their parent posting groups and move together during sorting.
 This preserves the expand/collapse ("Antworten") functionality.
 We do NOT hide section.thread elements — derstandard.at manages their
 visibility natively via the "collapsed" CSS class. */

 /* Icon size hierarchy. ico-pri = big (active direction),
 ico-sec = small (inactive direction). Spacing between the two Balance
 triangles is handled by gap on .dst-btn-ico so it stays identical
 regardless of which triangle is big/small (order-independent). */
 .ico-pri { font-size:17px; line-height:1; vertical-align:middle; }
 .ico-sec { font-size:11px; line-height:1; vertical-align:middle; }

 /* Dots indicator centered BELOW the button text.
 Real CSS circles (not Unicode glyphs) → crisp on high-density Android
 screens, no pixel-bleeding, no horizontal shift when the label changes. */
 .dots-indicator {
 display: flex;
 justify-content: center;
 align-items: center;
 gap: 4px; /* gap == dot diameter (Gemini "geometric harmony") */
 line-height: 1;
 /* pinned to the bottom via absolute positioning so they are taken
 OUT of the flex flow. This lets the text row occupy the full button
 height and center vertically without being pushed up by the dots. */
 position: absolute;
 left: 0;
 right: 0;
 bottom: 6px;
 }
 .dst-dot {
 width: 4px;
 height: 4px;
 border-radius: 50%;
 box-sizing: border-box;
 background: transparent;
 border: 1px solid currentColor;
 opacity: 0.55; /* hollow (inactive) dot: subtle outline */
 }
 .dst-dot.filled {
 background: currentColor;
 opacity: 0.9; /* filled (active) dot: solid, prominent */
 }

 /* Badge bar container — NO wrap, single row, spans full posting-frame width.
 The 3 sort buttons flex-grow to fill evenly. */
 #dst-badge-bar {
 display: flex;
 flex-wrap: nowrap;
 gap: 6px;
 padding: 10px 0 6px 0;
 align-items: stretch;
 justify-content: center;
 box-sizing: border-box;
 width: 100%;
 }

 /* Individual badge button — vertical layout: text row on top, dots below */
 .dst-badge-btn {
 display: inline-flex;
 flex-direction: column;
 align-items: center;
 justify-content: center;
 gap: 0;
 background: #fff;
 color: #333;
 font-size: 11.5px;
 font-weight: 600;
 padding: 6px 8px 8px 8px; /* 8px bottom keeps dots clear of the border */
 border: 2px solid #ddd;
 cursor: pointer;
 user-select: none;
 white-space: nowrap;
 line-height: 1;
 letter-spacing: .1px;
 transition: all 0.2s ease;
 box-shadow: 0 1px 3px rgba(0,0,0,0.06);
 box-sizing: border-box;
 flex: 1 1 0; /* sort buttons stretch to fill the frame width equally */
 min-width: 0;
 min-height: 42px; /* uniform height across all four buttons */
 border-radius: 22px; /* pill-like rounding (matches old single-line look) */
 position: relative; /* anchor for the absolutely-positioned dots */
 }
 /* Top row: [icon] [label] centred TOGETHER as one unit.
 The icon belongs to the text, so the whole [icon][label] group is
 treated as a single inline unit and centred via justify-content:center.
 No hidden clone/spacer — that only centred the label alone and made the
 icon+text combo look shifted to the left. */
 .dst-btn-toprow {
 display: flex;
 align-items: center;
 justify-content: center; /* centre the [icon][label] group as a unit */
 width: 100%;
 gap: 4px;
 }
 .dst-btn-ico {
 flex: 0 0 auto;
 display: inline-flex;
 align-items: center;
 gap: 1px; /* order-independent gap between the two Balance triangles */
 }
 .dst-btn-label {
 flex: 0 1 auto; /* hug the text; sits right beside its icon */
 text-align: center;
 overflow: hidden;
 text-overflow: ellipsis;
 white-space: nowrap;
 }
 .dst-badge-btn:hover {
 border-color: #aaa;
 background: #f5f5f5;
 box-shadow: 0 2px 6px rgba(0,0,0,0.1);
 }

 /* Active badge: highlighted border, no scale */
 .dst-badge-btn.active {
 border-color: #2e7d32;
 border-width: 2.5px;
 background: #e8f5e9;
 box-shadow: 0 2px 8px rgba(46,125,50,0.25);
 font-weight: 700;
 }
 .dst-badge-btn.active:hover {
 background: #c8e6c9;
 border-color: #1b5e20;
 }

 /* active badge in a "low" sort mode (Balance: Low / Likes: Low)
 turns RED — same red as the down-triangle (#c62828) — with a subtle
 reddish background, mirroring the green active look. This makes the sort
 direction instantly readable from the large border, not just the tiny
 triangle. Timeline stays green for both modes (New/Old is neither
 positive nor negative). */
 .dst-badge-btn.active.dst-low {
 border-color: #c62828;
 background: #fdecea;
 box-shadow: 0 2px 8px rgba(198,40,40,0.25);
 }
 .dst-badge-btn.active.dst-low:hover {
 background: #f9d7d2;
 border-color: #a01818;
 }

 /* Inactive badges visually recede via opacity, making the active
 badge stand out clearly. This is purely visual — no layout changes. */
 .dst-badge-btn:not(.active) {
 opacity: 0.65;
 }

 /* Click animation — styled after the green posting-load bar.
 IMPORTANT: only background-color + box-shadow are animated. These are
 purely visual and do NOT affect layout, so the text/icon/dots arrangement
 inside the badge (the flex top-row + absolutely-positioned dots from
) stays EXACTLY as-is — nothing shifts. No ::before overlay, no
 position/z-index changes on any inner element.
 The badge briefly flashes the loading-bar's light-green (#B7CCA3) with a
 soft green glow ring, then settles back to the active green (#e8f5e9). */
 @keyframes dst-pulse-bounce {
 0% { background-color: #B7CCA3; box-shadow: 0 0 0 5px rgba(143,175,111,0.35), 0 2px 8px rgba(46,125,50,0.25); }
 55% { background-color: #d4e6c6; box-shadow: 0 0 0 3px rgba(143,175,111,0.18), 0 2px 8px rgba(46,125,50,0.20); }
 100% { background-color: #e8f5e9; box-shadow: 0 2px 8px rgba(46,125,50,0.25); }
 }
 .dst-badge-btn.pulse {
 animation: dst-pulse-bounce 0.5s ease-out;
 }
 /* red flash variant for "low" badges so the click animation
 matches the red active state (settles at the reddish #fdecea). */
 @keyframes dst-pulse-bounce-red {
 0% { background-color: #e6a9a3; box-shadow: 0 0 0 5px rgba(198,40,40,0.30), 0 2px 8px rgba(198,40,40,0.25); }
 55% { background-color: #f3cbc6; box-shadow: 0 0 0 3px rgba(198,40,40,0.16), 0 2px 8px rgba(198,40,40,0.20); }
 100% { background-color: #fdecea; box-shadow: 0 2px 8px rgba(198,40,40,0.25); }
 }
 .dst-badge-btn.pulse.dst-low {
 animation: dst-pulse-bounce-red 0.5s ease-out;
 }
 @media (prefers-reduced-motion: reduce) {
 .dst-badge-btn.pulse,
 .dst-badge-btn.pulse.dst-low { animation: none; }
 }


 /* ═══ MOBILE (≤768px): wrap badges into readable rows ═══════════════════
 Desktop layout above is intentionally untouched. These rules live entirely
 inside the media query, so they can ONLY take effect on viewports ≤768px
 (phones / Firefox for Android). On wider screens nothing here applies. */
 @media (max-width: 768px) {
 #dst-badge-bar {
 flex-wrap: wrap; /* allow badges to flow onto multiple rows */
 gap: 8px; /* a touch more breathing room between rows */
 padding: 12px 4px 8px 4px; /* slightly taller bar for comfortable taps */
 }
 #dst-badge-bar .dst-badge-btn {
 flex: 0 1 auto; /* size to label instead of equal-width slices */
 min-width: auto; /* drop the 0 min-width so text is never clipped */
 font-size: 13px; /* larger, legible text on small screens */
 padding: 8px 12px; /* bigger tap target (≥ ~40px tall) */
 white-space: nowrap; /* keep each label on one line; wrap by badge */
 }
 }

 /* ═══ VOTER POPUP ═══════════════════════════════════════════
 Clicking a posting's rating numbers opens this badge-styled popup that
 lists who rated positively / negatively (data from the public ratinglog
 endpoint). Rendered inside the forum shadow DOM so styles stay isolated. */

 /* Make the rating numbers look clickable */
 dst-posting--ratinglog button.u-interactive {
 cursor: pointer !important;
 }
 /* on hover, frame the whole rating area in gold — exactly
 like a warm gold highlight (2px solid #FFD700 + #fff8e1 background) instead
 of underlining the numbers. The default border is transparent so the
 layout never jumps when the gold frame appears. */
 dst-posting--ratinglog.dst-votable button {
 border: 2px solid transparent !important;
 border-radius: 11px !important;
 transition: border-color 0.2s ease, background 0.2s ease !important;
 }
 dst-posting--ratinglog.dst-votable button:hover {
 border: 2px solid #FFD700 !important;
 background: #fff8e1 !important;
 }
 dst-posting--ratinglog.dst-votable button:hover span.pos,
 dst-posting--ratinglog.dst-votable button:hover span.neg {
 text-decoration: none !important;
 }

 /* Full-screen backdrop */
 #dst-voter-overlay {
 position: fixed;
 inset: 0;
 z-index: 2147483647;
 display: flex;
 align-items: center;
 justify-content: center;
 background: rgba(0, 0, 0, 0.45);
 padding: 16px;
 box-sizing: border-box;
 animation: dst-voter-fade 0.15s ease-out;
 }
 @keyframes dst-voter-fade { from { opacity: 0; } to { opacity: 1; } }

 /* The badge-styled card */
 #dst-voter-card {
 position: relative;
 background: #ffffff;
 border-radius: 20px;
 box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
 width: 100%;
 max-width: 540px;
 max-height: 80vh;
 display: flex;
 flex-direction: column;
 overflow: hidden;
 font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
 color: #1a1a1a;
 animation: dst-voter-pop 0.18s cubic-bezier(0.2, 0.8, 0.3, 1.1);
 }
 @keyframes dst-voter-pop { from { transform: scale(0.94); opacity: 0; } to { transform: scale(1); opacity: 1; } }

 /* no more central heading — each column owns its own header (see
 .dst-voter-col-head). the "×" close button was removed; the popup
 closes via a backdrop click or the Escape key. */

 /* Body: two columns */
 #dst-voter-body {
 display: flex;
 gap: 0;
 overflow: hidden;
 flex: 1 1 auto;
 min-height: 120px;
 }
 .dst-voter-col {
 flex: 1 1 50%;
 display: flex;
 flex-direction: column;
 min-width: 0;
 }
 .dst-voter-col + .dst-voter-col { border-left: 1px solid #ececec; }
 .dst-voter-col-head {
 padding: 13px 14px 11px 14px;
 font-size: 13px;
 position: sticky;
 top: 0;
 background: #fff;
 display: flex;
 align-items: center;
 gap: 6px;
 }
 /* Triangle keeps the same size ratio to the text as in the
 badge bar (.ico-pri 17px / .dst-badge-btn 11.5px = 1.478). With 13px text
 that means 13 * 1.478 = 19.2px. */
 .dst-voter-col-head .dst-vch-tri { font-size: 19.2px; line-height: 1; }
 /* Count and label share the same size & weight — no longer
 does the number look bigger/bolder than the text next to it. */
 .dst-voter-col-head .dst-vch-count { font-weight: 600; font-size: 13px; }
 .dst-voter-col-head .dst-vch-label { font-weight: 600; font-size: 13px; }
 .dst-voter-col-head.pos { color: #2e7d32; border-bottom: 2px solid #2e7d32; }
 .dst-voter-col-head.neg { color: #c62828; border-bottom: 2px solid #c62828; }
 .dst-voter-list {
 list-style: none;
 margin: 0;
 padding: 4px 0 8px 0;
 overflow-y: auto;
 flex: 1 1 auto;
 }
 .dst-voter-list li { margin: 0; padding: 0; }
 .dst-voter-list a {
 display: block;
 padding: 7px 14px;
 font-size: 13px;
 color: #1a1a1a;
 text-decoration: none;
 white-space: nowrap;
 overflow: hidden;
 text-overflow: ellipsis;
 border-radius: 8px;
 margin: 1px 6px;
 }
 .dst-voter-list a:hover { background: #f3f6ef; color: #000; }

 /* Footer / pagination */
 #dst-voter-foot {
 flex: 0 0 auto;
 padding: 10px 14px;
 border-top: 1px solid #ececec;
 display: flex;
 align-items: center;
 justify-content: center;
 gap: 10px;
 min-height: 22px;
 }

 /* Loading spinner */
 .dst-voter-loading {
 display: flex;
 flex-direction: column;
 align-items: center;
 justify-content: center;
 gap: 10px;
 padding: 30px;
 width: 100%;
 color: #777;
 font-size: 13px;
 }
 .dst-voter-spinner {
 width: 28px;
 height: 28px;
 border: 3px solid #e0e0e0;
 border-top-color: #2e7d32;
 border-radius: 50%;
 animation: dst-voter-spin 0.8s linear infinite;
 }
 @keyframes dst-voter-spin { to { transform: rotate(360deg); } }

 /* footer progress bar — replicates derStandard's posting-load bar
 (the green "Lade alle Postings …" bar) for a consistent look. */
 .dst-voter-progress {
 width: 100%;
 height: 28px;
 background: #e8e8e8;
 border-radius: 14px;
 position: relative;
 overflow: hidden;
 box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
 }
 .dst-voter-progress-fill {
 position: absolute;
 left: 0;
 top: 0;
 height: 100%;
 width: 0%;
 background: linear-gradient(90deg, #8FAF6F, #B7CCA3);
 border-radius: 14px;
 transition: width 0.4s ease;
 }
 .dst-voter-progress-fill--loading {
 animation: dst-voter-progress-pulse 1.5s ease-in-out infinite;
 }
 .dst-voter-progress--done {
 box-shadow: 0 2px 8px rgba(46,125,50,0.25);
 }
 .dst-voter-progress--done .dst-voter-progress-text {
 color: #fff;
 text-shadow: 0 1px 2px rgba(0,0,0,0.2);
 }
 .dst-voter-progress-text {
 position: absolute;
 left: 0;
 top: 0;
 width: 100%;
 height: 100%;
 display: flex;
 align-items: center;
 justify-content: center;
 color: #2e7d32;
 font-weight: 700;
 font-size: 12px;
 z-index: 1;
 text-shadow: 0 0 3px rgba(255,255,255,0.8);
 }
 @keyframes dst-voter-progress-pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
 .dst-voter-error {
 padding: 24px 20px;
 text-align: center;
 color: #c62828;
 font-size: 13px;
 width: 100%;
 }

 @media (max-width: 768px) {
 #dst-voter-card { max-width: 100%; max-height: 86vh; }
 .dst-voter-list a { padding: 9px 14px; font-size: 14px; }
 }
 `;

  let sortEnabled = true;
  let sortMode = 'balance-top'; // default
  let autoLoadEnabled = true;
  let observer = null;
  let sortTimeout = null;
  let isSorting = false;
  let lastSortSignature = '';
  let autoLoadClicked = false;
  let isLoadingAllPostings = false; // Guard for loadAllPostings
  // Removed ratingChangeDebounce — we no longer observe rating attribute changes
  // This prevents the extension from interfering with derStandard.at's vote processing

  // Reply threads must stay COLLAPSED by default.
  // We collapse each expanded thread exactly ONCE (via the native toggle), and
  // track which postings we've already auto-collapsed so we never fight a user
  // who manually re-expands a thread. WeakSet keyed on the posting element is
  // robust because the CSS-order sort never recreates posting nodes.
  const autoCollapsedPostings = new WeakSet();

  // Track pinned postings we've auto-expanded. When the user turns on
  // the gear's "Antworten ausgeklappt", derStandard expands normal postings but
  // leaves angeheftete (pinned) postings collapsed. We expand those pinned
  // postings once so both posting types honor the setting equally — and the
  // WeakSet makes sure we never fight a user who re-collapses one afterwards.
  const autoExpandedPostings = new WeakSet();

  // ════════════════════════════════════════════════════════════════════════
  // VOTER POPUP
  // Make the rating numbers clickable and show who rated positive/negative.
  // The numeric posting id (needed by the ratinglog endpoint) is supplied by
  // forum-hook.js (MAIN world) which captures it from the GraphQL responses.
  // ════════════════════════════════════════════════════════════════════════

  // Maps encoded posting id (DOM "postingid" attr) -> numeric legacy posting id
  const voterIdMap = Object.create(null);
  let voterListenerAttached = false;
  let voterEscBound = false;

  // Receive id pairs from the MAIN-world hook
  window.addEventListener('dst-voter-idmap', function (ev) {
    try {
      const pairs = JSON.parse(ev.detail);
      for (const k in pairs) voterIdMap[k] = pairs[k];
    } catch (e) {
      /* ignore malformed payloads */
    }
  });

  const RATINGLOG_BASE = 'https://apps.derstandard.at/forum';

  // Resolve the numeric posting id for an encoded id, retrying briefly in case
  // the GraphQL response for that posting hasn't been captured yet.
  function resolveNumericPostingId(encodedId) {
    return new Promise(function (resolve) {
      if (voterIdMap[encodedId]) return resolve(voterIdMap[encodedId]);
      let tries = 0;
      const iv = setInterval(function () {
        tries++;
        if (voterIdMap[encodedId]) {
          clearInterval(iv);
          resolve(voterIdMap[encodedId]);
        } else if (tries >= 20) {
          clearInterval(iv);
          resolve(null);
        } // ~5s
      }, 250);
    });
  }

  // Fetch one ratinglog "page". When `cursor` is null we hit the initial
  // endpoint (returns the wrapper + first entries + next cursor); otherwise we
  // hit the pagination endpoint (returns bare <li> entries).
  async function fetchRatingLogPage(numericId, cursor) {
    let url;
    if (cursor == null) {
      url = RATINGLOG_BASE + '/ratinglog?id=' + encodeURIComponent(numericId) + '&idType=1';
    } else {
      url =
        RATINGLOG_BASE +
        '/RatingLog?id=' +
        encodeURIComponent(numericId) +
        '&idType=Posting&LatestRaterCommunityIdentityId=' +
        encodeURIComponent(cursor);
    }
    const resp = await fetch(url, {
      method: 'GET',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'omit',
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    return await resp.text();
  }

  // Parse a ratinglog HTML fragment into structured data.
  // Returns { totals:{pos,neg}|null, entries:[{name,rate,profile,cid}], nextCursor }
  function parseRatingLog(html) {
    const doc = new DOMParser().parseFromString(html, 'text/html');

    let totals = null;
    const wrapper = doc.querySelector('.js-ratings-log, .ratings-log');
    if (wrapper && wrapper.hasAttribute('data-totalpositive')) {
      totals = {
        pos: parseInt(wrapper.getAttribute('data-totalpositive'), 10) || 0,
        neg: parseInt(wrapper.getAttribute('data-totalnegative'), 10) || 0,
      };
    }

    const entries = [];
    let lastCid = null;
    const items = doc.querySelectorAll('li[data-rate]');
    items.forEach(function (li) {
      const rate = li.getAttribute('data-rate'); // "positive" | "negative"
      const link = li.querySelector('a.ratings-log-communityname, a[href*="/userprofil/"]');
      const nameEl = link ? link.querySelector('span') || link : null;
      const name = nameEl ? (nameEl.textContent || '').trim() : '';
      const profile = link ? link.getAttribute('href') : null;
      let cid = null;
      const followBtn = li.querySelector('[data-communityidentityid]');
      if (followBtn) cid = followBtn.getAttribute('data-communityidentityid');
      else if (profile) {
        const m = profile.match(/\/(\d+)(?:\D*)$/);
        if (m) cid = m[1];
      }
      if (name && (rate === 'positive' || rate === 'negative')) {
        entries.push({ name: name, rate: rate, profile: profile, cid: cid });
      }
      if (cid) lastCid = cid;
    });

    // Pagination cursor: prefer the hidden input from the initial response,
    // otherwise fall back to the last entry's community-identity id.
    let nextCursor = null;
    const hidden = doc.querySelector('input[name="LatestRaterCommunityIdentityId"]');
    if (hidden && hidden.value && /^\d+$/.test(hidden.value)) nextCursor = hidden.value;
    else if (lastCid) nextCursor = lastCid;

    return { totals: totals, entries: entries, nextCursor: nextCursor };
  }

  // ── Popup rendering ───────────────────────────────────────────────────
  function closeVoterPopup(shadowRoot) {
    const ov = shadowRoot.querySelector('#dst-voter-overlay');
    if (ov) ov.remove();
  }

  function buildVoterPopupSkeleton(shadowRoot, posCount, negCount) {
    closeVoterPopup(shadowRoot);

    const overlay = document.createElement('div');
    overlay.id = 'dst-voter-overlay';

    const card = document.createElement('div');
    card.id = 'dst-voter-card';

    // the central "Bewertungen ▲ ▼" heading is gone; each column carries
    // its own header with a coloured triangle, the count, and a descriptive label.
    // the "×" close button was removed entirely — the popup now closes via
    // a backdrop click (outside the card) or the Escape key (see below).

    // Body with two columns
    const body = document.createElement('div');
    body.id = 'dst-voter-body';

    function makeColumn(kind, count, labelText) {
      const col = document.createElement('div');
      col.className = 'dst-voter-col';
      const colHead = document.createElement('div');
      colHead.className = 'dst-voter-col-head ' + kind;
      const tri = document.createElement('span');
      tri.className = 'dst-vch-tri';
      tri.textContent = kind === 'pos' ? '\u25B2' : '\u25BC';
      const cnt = document.createElement('span');
      cnt.className = 'dst-vch-count';
      cnt.textContent = count;
      const t = document.createElement('span');
      t.className = 'dst-vch-label';
      t.textContent = labelText;
      colHead.appendChild(tri);
      colHead.appendChild(cnt);
      colHead.appendChild(t);
      const ul = document.createElement('ul');
      ul.className = 'dst-voter-list';
      ul.setAttribute('data-kind', kind);
      col.appendChild(colHead);
      col.appendChild(ul);
      return { col: col, ul: ul };
    }
    const posCol = makeColumn('pos', posCount, 'Positive Bewertungen');
    const negCol = makeColumn('neg', negCount, 'Negative Bewertungen');
    body.appendChild(posCol.col);
    body.appendChild(negCol.col);

    // Footer
    const foot = document.createElement('div');
    foot.id = 'dst-voter-foot';

    card.appendChild(body);
    card.appendChild(foot);
    overlay.appendChild(card);

    // Close on backdrop click
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeVoterPopup(shadowRoot);
    });

    // Close on Escape (bound once)
    if (!voterEscBound) {
      voterEscBound = true;
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeVoterPopup(shadowRoot);
      });
    }

    shadowRoot.appendChild(overlay);
    return { overlay: overlay, posUl: posCol.ul, negUl: negCol.ul, foot: foot };
  }

  function appendVoterEntries(ul, entries) {
    entries.forEach(function (en) {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.textContent = en.name;
      a.title = en.name;
      if (en.profile) {
        a.href = en.profile;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
      } else {
        a.href = '#';
        a.addEventListener('click', function (e) {
          e.preventDefault();
        });
      }
      a.addEventListener('click', function (e) {
        e.stopPropagation();
      });
      li.appendChild(a);
      ul.appendChild(li);
    });
  }

  async function openVoterPopup(shadowRoot, encodedId, posCount, negCount) {
    const refs = buildVoterPopupSkeleton(shadowRoot, posCount, negCount);

    // Initial loading state inside the body
    const loading = document.createElement('div');
    loading.className = 'dst-voter-loading';
    const spin = document.createElement('div');
    spin.className = 'dst-voter-spinner';
    const ltxt = document.createElement('div');
    ltxt.textContent = 'Bewertungen werden geladen \u2026';
    loading.appendChild(spin);
    loading.appendChild(ltxt);
    const body = refs.overlay.querySelector('#dst-voter-body');
    body.style.display = 'none';
    body.parentElement.insertBefore(loading, body);

    function showError(message) {
      const card = refs.overlay.querySelector('#dst-voter-card');
      if (loading.parentElement) loading.remove();
      body.style.display = 'none';
      let err = card.querySelector('.dst-voter-error');
      if (!err) {
        err = document.createElement('div');
        err.className = 'dst-voter-error';
        card.insertBefore(err, refs.foot);
      }
      err.textContent = message;
    }

    // Resolve numeric id
    const numericId = await resolveNumericPostingId(encodedId);
    if (!numericId) {
      showError(
        'Bewertungsdaten konnten nicht geladen werden (Posting-ID nicht gefunden). Bitte Seite neu laden und erneut versuchen.',
      );
      return;
    }

    // State for pagination
    let cursor = null;
    let done = false;
    let totalPos = parseInt(posCount, 10) || 0;
    let totalNeg = parseInt(negCount, 10) || 0;
    let loadedPos = 0;
    let loadedNeg = 0;
    let bodyShown = false;

    // the ratinglog endpoint returns ALL raters interleaved by recency
    // (positive + negative mixed). Because positive raters usually far outnumber
    // negative ones, the first page is almost all positives and the negative
    // column would stay empty until the user clicked "Mehr laden" several times.
    // We now auto-load EVERY page so both columns fill completely on their own —
    // no "Mehr laden" button anymore.
    const MAX_PAGES = 400; // safety cap against infinite loops
    const PAGE_DELAY_MS = 120; // be polite to the server between requests

    // the footer shows the same green progress bar derStandard's forum
    // uses while loading postings (grey track + green gradient fill + pulse +
    // centred text overlay), instead of the small circular spinner.
    function ensureProgressBar() {
      let bar = refs.foot.querySelector('#dst-voter-progress');
      if (!bar) {
        bar = document.createElement('div');
        bar.id = 'dst-voter-progress';
        bar.className = 'dst-voter-progress';
        const fill = document.createElement('div');
        fill.className = 'dst-voter-progress-fill';
        const txt = document.createElement('span');
        txt.className = 'dst-voter-progress-text';
        bar.appendChild(fill);
        bar.appendChild(txt);
        refs.foot.appendChild(bar);
      }
      return {
        bar: bar,
        fill: bar.querySelector('.dst-voter-progress-fill'),
        txt: bar.querySelector('.dst-voter-progress-text'),
      };
    }

    function updateStatus() {
      const pb = ensureProgressBar();
      const total = totalPos + totalNeg;
      const loaded = loadedPos + loadedNeg;
      if (done) {
        pb.fill.style.width = '100%';
        pb.fill.classList.remove('dst-voter-progress-fill--loading');
        pb.bar.classList.add('dst-voter-progress--done');
        pb.txt.textContent = loaded + ' Bewertungen geladen';
      } else {
        const pct = total > 0 ? Math.min(100, Math.round((loaded / total) * 100)) : 0;
        pb.fill.style.width = pct + '%';
        pb.fill.classList.add('dst-voter-progress-fill--loading');
        pb.txt.textContent = 'L\u00E4dt \u2026 ' + loaded + ' von ' + total + ' geladen';
      }
    }

    function revealBodyOnce() {
      if (bodyShown) return;
      if (loading.parentElement) loading.remove();
      body.style.display = 'flex';
      bodyShown = true;
    }

    // Auto-load every page until there is nothing left to fetch.
    async function loadAllPages() {
      let guard = 0;
      updateStatus(); // show the progress bar immediately (0 %)
      while (!done && guard < MAX_PAGES) {
        guard++;
        let html;
        try {
          html = await fetchRatingLogPage(numericId, cursor);
        } catch (err) {
          if (loadedPos + loadedNeg === 0) {
            showError('Fehler beim Laden der Bewertungsdaten: ' + err.message);
            return;
          }
          // We already have some data — stop gracefully and report partial state.
          done = true;
          const pb = ensureProgressBar();
          pb.fill.style.width = '100%';
          pb.fill.classList.remove('dst-voter-progress-fill--loading');
          pb.bar.classList.add('dst-voter-progress--done');
          pb.txt.textContent =
            loadedPos + loadedNeg + ' geladen \u2013 weitere Daten konnten nicht geladen werden.';
          break;
        }

        const parsed = parseRatingLog(html);
        if (parsed.totals) {
          totalPos = parsed.totals.pos;
          totalNeg = parsed.totals.neg;
        }

        // Reveal the columns as soon as the first page arrives.
        revealBodyOnce();

        const posEntries = parsed.entries.filter(function (e) {
          return e.rate === 'positive';
        });
        const negEntries = parsed.entries.filter(function (e) {
          return e.rate === 'negative';
        });
        appendVoterEntries(refs.posUl, posEntries);
        appendVoterEntries(refs.negUl, negEntries);
        loadedPos += posEntries.length;
        loadedNeg += negEntries.length;

        // Stop when there are no new entries or the cursor stops advancing.
        if (parsed.entries.length === 0 || !parsed.nextCursor || parsed.nextCursor === cursor) {
          done = true;
        } else {
          cursor = parsed.nextCursor;
        }

        updateStatus();

        if (!done) {
          await new Promise(function (r) {
            setTimeout(r, PAGE_DELAY_MS);
          });
        }
      }

      // Reached the safety cap without a natural end.
      if (!done) done = true;

      revealBodyOnce();
      // no "Keine … Bewertungen" placeholder — an empty column simply
      // stays empty.
      updateStatus();
    }

    await loadAllPages();
  }

  // Delegated, capturing click handler — beats derStandard's own paywall
  // handler so clicking the rating numbers opens our popup instead.
  function handleRatingClick(e) {
    if (!sortEnabled) return;
    const path = e.composedPath ? e.composedPath() : [];
    let ratingEl = null;
    for (let i = 0; i < path.length; i++) {
      const node = path[i];
      if (node && node.tagName === 'DST-POSTING--RATINGLOG') {
        ratingEl = node;
        break;
      }
    }
    if (!ratingEl) return;

    e.preventDefault();
    e.stopImmediatePropagation();

    const forum = document.querySelector('dst-forum');
    const shadowRoot = forum && forum.shadowRoot;
    if (!shadowRoot) return;

    const encodedId = ratingEl.getAttribute('postingid');
    const pos = ratingEl.getAttribute('positiveratings') || '0';
    const neg = ratingEl.getAttribute('negativeratings') || '0';
    if (!encodedId) return;

    openVoterPopup(shadowRoot, encodedId, pos, neg);
  }

  function attachVoterListener(shadowRoot) {
    if (voterListenerAttached) return;
    voterListenerAttached = true;
    // Capture on document: fires before any of the page's own click handlers,
    // including the "STANDARD Smart" paywall trigger inside the rating element.
    document.addEventListener('click', handleRatingClick, true);
    // Mark rating elements as votable for the hover style hint.
    try {
      shadowRoot.querySelectorAll('dst-posting--ratinglog').forEach(function (el) {
        el.classList.add('dst-votable');
      });
    } catch (e) {
      /* ignore */
    }
  }

  // ════════════════════════════════════════════════════════════════════════
  // PROFILE PAGE VOTER POPUP
  // Profile pages (derstandard.at/profil/...) render a user's own postings
  // as <dst-posting-external> in plain light DOM — there is no <dst-forum>
  // and no shadow root to work inside.
  //
  // Good news: the profile feed's GraphQL query (UserprofilePostingsPrivate)
  // goes through the same forum-serve-graphql endpoint forum-hook.js already
  // listens to, and forum-hook.js knows how to read its flat `legacyId`
  // field (see forum-hook.js). So voterIdMap fills itself the same way it
  // does on article pages — this code only needs to mark postings as
  // clickable and wire up the click handler. No sorting is applied here —
  // by design, only the "who rated this" popup is wired up.
  // ════════════════════════════════════════════════════════════════════════

  const PROFILE_FEED_SELECTOR = '[class*="PostingFeed_postingfeed__"]';
  let profileVoterListenerAttached = false;
  let profileStyleInjected = false;

  // Mark every rating element we can see as votable (hover hint + click
  // target). The numeric id itself arrives asynchronously via forum-hook.js
  // and voterIdMap — resolveNumericPostingId() already retries for a few
  // seconds, so we don't need to wait for it here.
  function markProfilePostingsVotable(root) {
    root.querySelectorAll('dst-posting--ratinglog').forEach(function (el) {
      el.classList.add('dst-votable');
    });
  }

  // Same idea as ICON_STYLE_CSS injection for the forum's shadow root, but
  // global: the profile page has no shadow root to scope styles into.
  function injectProfileVoterStyle() {
    if (profileStyleInjected) return;
    profileStyleInjected = true;
    if (document.getElementById('dst-icon-style-global')) return;
    const styleEl = document.createElement('style');
    styleEl.id = 'dst-icon-style-global';
    styleEl.textContent = ICON_STYLE_CSS;
    document.head.appendChild(styleEl);
  }

  function handleProfileRatingClick(e) {
    if (!sortEnabled) return;
    const path = e.composedPath ? e.composedPath() : [];
    let ratingEl = null;
    for (let i = 0; i < path.length; i++) {
      const node = path[i];
      if (node && node.tagName === 'DST-POSTING--RATINGLOG') {
        ratingEl = node;
        break;
      }
    }
    if (!ratingEl || !ratingEl.closest('dst-posting-external')) return;

    e.preventDefault();
    e.stopImmediatePropagation();

    const encodedId = ratingEl.getAttribute('postingid');
    const pos = ratingEl.getAttribute('positiveratings') || '0';
    const neg = ratingEl.getAttribute('negativeratings') || '0';
    if (!encodedId) return;

    // document.body stands in for "shadowRoot" here — openVoterPopup only
    // ever calls .appendChild / .querySelector on whatever it's given.
    openVoterPopup(document.body, encodedId, pos, neg);
  }

  function attachProfileVoterListener() {
    if (profileVoterListenerAttached) return;
    profileVoterListenerAttached = true;
    document.addEventListener('click', handleProfileRatingClick, true);
  }

  // ── Entry point for profile pages ───────────────────────────────
  function waitForProfileFeed() {
    const existing = document.querySelector(PROFILE_FEED_SELECTOR);
    if (existing) {
      console.log('[DST Sorter] [Profil] Postings-Feed gefunden, aktiviere Voter-Popup');
      injectProfileVoterStyle();
      markProfilePostingsVotable(existing);
      attachProfileVoterListener();
      // Infinite-scroll / lazy-loaded postings keep appearing — re-mark
      // whenever the feed's subtree changes.
      const feedObserver = new MutationObserver(function () {
        markProfilePostingsVotable(existing);
      });
      feedObserver.observe(existing, { childList: true, subtree: true });
      return;
    }

    // Feed not there yet (SPA navigation) — watch for it to show up.
    const docObserver = new MutationObserver(function () {
      const feed = document.querySelector(PROFILE_FEED_SELECTOR);
      if (feed) {
        docObserver.disconnect();
        waitForProfileFeed();
      }
    });
    docObserver.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true,
    });
  }

  // ── Utility: read ratings from a posting ───────────────────────
  function getPositiveRatings(posting) {
    const ratingEl = posting.querySelector('dst-posting--ratinglog');
    if (!ratingEl) return 0;
    return parseInt(ratingEl.getAttribute('positiveratings'), 10) || 0;
  }

  function getNegativeRatings(posting) {
    const ratingEl = posting.querySelector('dst-posting--ratinglog');
    if (!ratingEl) return 0;
    return parseInt(ratingEl.getAttribute('negativeratings'), 10) || 0;
  }

  function getNetRatings(posting) {
    return getPositiveRatings(posting) - getNegativeRatings(posting);
  }

  // ── Parse relative time strings like "vor 5 Stunden" ──────────
  function parseRelativeTime(text) {
    if (!text) return 0;
    const now = Date.now();
    // Match patterns like "vor 5 Stunden", "vor 2 Tagen", "vor 30 Minuten", "vor 1 Monat"
    const match = text.match(/vor\s+(\d+)\s+(Sekunde|Minute|Stunde|Tag|Woche|Monat|Jahr)n?/i);
    if (!match) return 0;
    const value = parseInt(match[1], 10);
    const unit = match[2].toLowerCase();
    let ms = 0;
    if (unit.startsWith('sekunde')) ms = value * 1000;
    else if (unit.startsWith('minute')) ms = value * 60 * 1000;
    else if (unit.startsWith('stunde')) ms = value * 60 * 60 * 1000;
    else if (unit.startsWith('tag')) ms = value * 24 * 60 * 60 * 1000;
    else if (unit.startsWith('woche')) ms = value * 7 * 24 * 60 * 60 * 1000;
    else if (unit.startsWith('monat')) ms = value * 30 * 24 * 60 * 60 * 1000;
    else if (unit.startsWith('jahr')) ms = value * 365 * 24 * 60 * 60 * 1000;
    return ms > 0 ? now - ms : 0;
  }

  // ── Extract timestamp from a posting for chronological sort ────
  function getPostingTimestamp(posting) {
    // Strategy 1: <time datetime="..."> with a valid ISO date
    let timeEl = posting.querySelector('time[datetime]');
    if (timeEl) {
      const dtAttr = timeEl.getAttribute('datetime');
      if (dtAttr && dtAttr !== 'null' && dtAttr !== 'undefined') {
        const parsed = new Date(dtAttr).getTime();
        if (!isNaN(parsed) && parsed > 0) return parsed;
      }
      // Strategy 1b: Parse relative time from <time> textContent
      const relTime = parseRelativeTime(timeEl.textContent);
      if (relTime > 0) return relTime;
    }

    // Strategy 2: Check shadow DOM of the posting
    if (posting.shadowRoot) {
      timeEl = posting.shadowRoot.querySelector('time[datetime]');
      if (timeEl) {
        const dtAttr = timeEl.getAttribute('datetime');
        if (dtAttr && dtAttr !== 'null' && dtAttr !== 'undefined') {
          const parsed = new Date(dtAttr).getTime();
          if (!isNaN(parsed) && parsed > 0) return parsed;
        }
        const relTime = parseRelativeTime(timeEl.textContent);
        if (relTime > 0) return relTime;
      }
    }

    // Strategy 3: Check sub-elements like dst-posting-head
    const headEl = posting.querySelector('dst-posting-head');
    if (headEl) {
      timeEl = headEl.querySelector('time');
      if (!timeEl && headEl.shadowRoot) {
        timeEl = headEl.shadowRoot.querySelector('time');
      }
      if (timeEl) {
        const dtAttr = timeEl.getAttribute('datetime');
        if (dtAttr && dtAttr !== 'null' && dtAttr !== 'undefined') {
          const parsed = new Date(dtAttr).getTime();
          if (!isNaN(parsed) && parsed > 0) return parsed;
        }
        const relTime = parseRelativeTime(timeEl.textContent);
        if (relTime > 0) return relTime;
      }
    }

    // Strategy 4: Find any <span> with relative time text
    const spans = posting.querySelectorAll('span');
    for (const span of spans) {
      if (span.children.length === 0) {
        const relTime = parseRelativeTime(span.textContent);
        if (relTime > 0) return relTime;
      }
    }

    // Strategy 5: data-created or data-timestamp attribute
    const ts =
      posting.getAttribute('data-created') ||
      posting.getAttribute('data-timestamp') ||
      posting.getAttribute('datetime') ||
      posting.getAttribute('data-date');
    if (ts) {
      const parsed = new Date(ts).getTime();
      if (!isNaN(parsed)) return parsed;
    }

    // Fallback: use DOM position (index) to preserve original order
    return 0;
  }

  // ── Build a signature of current ratings to detect changes ─────
  function buildSortSignature(groups) {
    return groups
      .map((g) => {
        const p = getPositiveRatings(g.posting);
        const n = getNegativeRatings(g.posting);
        return `${p}:${n}`;
      })
      .join(',');
  }

  // ── Detect if a posting is pinned ("angeheftet") ─────────────────
  function isPinnedPosting(posting) {
    if (posting.hasAttribute('pinned')) return true;
    if (posting.hasAttribute('data-pinned')) return true;
    if (posting.getAttribute('ispinned') === 'true') return true;
    if (posting.getAttribute('is-pinned') === 'true') return true;

    const classList = posting.className || '';
    if (
      /\bpinned\b/i.test(classList) ||
      /\bis-pinned\b/i.test(classList) ||
      /\bposting--pinned\b/i.test(classList)
    )
      return true;

    const shadowRoot = posting.shadowRoot;
    if (shadowRoot) {
      const allText = shadowRoot.textContent || ''; // read-only, textContent statt innerHTML
      if (/angeheftet|📌/i.test(allText)) {
        const allElements = shadowRoot.querySelectorAll('*');
        for (const el of allElements) {
          for (const node of el.childNodes) {
            if (node.nodeType === Node.TEXT_NODE) {
              const text = node.textContent?.trim().toLowerCase() || '';
              if (
                text === 'angeheftet' ||
                text === 'pinned' ||
                text === '📌' ||
                text.startsWith('angeheftet') ||
                text.startsWith('📌')
              ) {
                console.log('[DST Sorter] Pinned detected via shadow DOM text: "' + text + '"');
                return true;
              }
            }
          }
        }
      }

      const pinElements = shadowRoot.querySelectorAll(
        '.pinned, .is-pinned, .posting--pinned, .angeheftet, ' +
          '[class~="pinned"], [class~="is-pinned"], [class~="angeheftet"], [class~="sticky"]',
      );
      if (pinElements.length > 0) {
        console.log('[DST Sorter] Pinned detected via shadow DOM class');
        return true;
      }
    }

    const lightPinElements = posting.querySelectorAll(
      '.pinned, .is-pinned, .posting--pinned, .angeheftet, ' +
        '[class~="pinned"], [class~="is-pinned"], [class~="angeheftet"]',
    );
    if (lightPinElements.length > 0) return true;

    for (const child of posting.children) {
      const text = child.textContent?.trim().toLowerCase() || '';
      if (text === 'angeheftet' || text === 'pinned') return true;
    }

    const headerEl = posting.querySelector('dst-posting-head');
    if (headerEl) {
      const headerText = headerEl.textContent || '';
      if (/\bAngeheftet\b/i.test(headerText)) {
        console.log('[DST Sorter] Pinned detected via header text "Angeheftet"');
        return true;
      }
    }

    // Strategy: Check for <strong> or any element with "Angeheftet" text in light DOM
    const strongEls = posting.querySelectorAll('strong, b, span');
    for (const el of strongEls) {
      const text = el.textContent?.trim().toLowerCase() || '';
      if (text.startsWith('angeheftet') || text === '📌') {
        console.log(
          '[DST Sorter] Pinned detected via <' +
            el.tagName +
            '> text: "' +
            el.textContent.trim() +
            '"',
        );
        return true;
      }
    }

    // Strategy: Check full posting textContent for pinned indicators near the top
    const fullText = posting.textContent || '';
    if (/📌\s*Angeheftet|Angeheftet\s*·/i.test(fullText.substring(0, 300))) {
      console.log('[DST Sorter] Pinned detected via posting textContent');
      return true;
    }

    return false;
  }

  // ── Get posting ID for deduplication ───────────────────────────
  function getPostingId(posting) {
    // 1) Direct attributes on the <dst-posting> element (rarely present in 2026 DOM)
    const directId =
      posting.getAttribute('data-posting-id') ||
      posting.getAttribute('data-postingid') ||
      posting.getAttribute('data-id') ||
      posting.getAttribute('id') ||
      posting.getAttribute('postingid') ||
      posting.getAttribute('posting-id') ||
      null;
    if (directId) return directId;

    // 2) STABLE encoded posting ID nested inside the posting.
    // derStandard does NOT put an id on the <dst-posting> element itself, but
    // every posting embeds its encoded id (e.g. "3FO5eHTfBXdAobg1YdEqB6a3jUu")
    // on child elements such as <dst-posting--ratinglog postingid="…"> and the
    // flyout trigger buttons (id="flyout-trigger-identity-…"). This id is
    // IDENTICAL for the pinned ("angeheftet") copy and its in-list twin, so it
    // is the reliable key for de-duplicating pinned postings — even when the
    // two copies momentarily show different (stale) rating counts.
    const stableId = getStablePostingId(posting);
    if (stableId) return stableId;

    // 3) Last-resort fallback: author + rating counts. Unreliable (ratings can be
    // stale between the two copies), kept only for postings that somehow lack
    // the nested encoded id.
    const ariaLabel = posting.getAttribute('aria-label') || '';
    if (ariaLabel) {
      const ratingEl = posting.querySelector('dst-posting--ratinglog');
      const pos = ratingEl ? ratingEl.getAttribute('positiveratings') || '0' : '0';
      const neg = ratingEl ? ratingEl.getAttribute('negativeratings') || '0' : '0';
      return ariaLabel + '|' + pos + ':' + neg;
    }

    return null;
  }

  // ── Extract the stable encoded posting ID from nested child elements ──────
  // Returns a string like "3FO5eHTfBXdAobg1YdEqB6a3jUu" or null. We deliberately
  // read it from the posting's OWN header elements (ratinglog / flyout buttons),
  // which are part of the dst-posting itself — reply postings live in separate
  // sibling <section.thread> nodes, so querySelector here won't pick them up.
  function getStablePostingId(posting) {
    // a) <dst-posting--ratinglog postingid="…"> — most direct source
    const ratingEl = posting.querySelector('dst-posting--ratinglog[postingid]');
    if (ratingEl) {
      const pid = ratingEl.getAttribute('postingid');
      if (pid) return pid;
    }
    // b) ratinglog element with id="ratinglog-<encodedId>"
    const ratingById = posting.querySelector('[id^="ratinglog-"]');
    if (ratingById) {
      const v = ratingById.getAttribute('id').replace(/^ratinglog-/, '');
      if (v) return v;
    }
    // c) flyout trigger buttons: id="flyout-trigger-identity-<encodedId>" etc.
    const flyout = posting.querySelector('[id^="flyout-trigger-"]');
    if (flyout) {
      const v = flyout.getAttribute('id').replace(/^flyout-trigger-[a-z]+-/i, '');
      if (v) return v;
    }
    return null;
  }

  // ── Detect if an element is the posting input form / reply box ────
  function isInputFormElement(el) {
    const tag = el.tagName?.toUpperCase() || '';

    // Check tag name for form-like custom elements
    if (/FORM|EDITOR|COMPOSE|POSTFORM|POSTING-FORM|REPLY-FORM|COMMENT-FORM/.test(tag)) return true;

    // Check if element contains <textarea>, <input type="text">, or contenteditable
    if (
      el.querySelector &&
      (el.querySelector('textarea') ||
        el.querySelector('input[type="text"]') ||
        el.querySelector('[contenteditable="true"]'))
    )
      return true;

    // Check for button with "Posten"/"Absenden"/"Senden" text inside the element
    if (el.querySelector) {
      const buttons = el.querySelectorAll('button');
      for (const btn of buttons) {
        const txt = btn.textContent?.trim().toLowerCase() || '';
        if (txt === 'posten' || txt === 'absenden' || txt === 'senden' || txt === 'antworten')
          return true;
      }
    }

    // Check for specific CSS classes
    const cls = el.className || '';
    if (
      /\bposting-form\b|\bcomment-form\b|\breply-form\b|\bforum--form\b|\bforum--compose\b|\bforum--editor\b/i.test(
        cls,
      )
    )
      return true;

    // Check shadow DOM for form elements
    if (el.shadowRoot) {
      if (
        el.shadowRoot.querySelector('textarea') ||
        el.shadowRoot.querySelector('input[type="text"]') ||
        el.shadowRoot.querySelector('[contenteditable="true"]')
      )
        return true;
      const shadowButtons = el.shadowRoot.querySelectorAll('button');
      for (const btn of shadowButtons) {
        const txt = btn.textContent?.trim().toLowerCase() || '';
        if (txt === 'posten' || txt === 'absenden' || txt === 'senden') return true;
      }
    }

    // Check if element has text "Titel" + "Kommentar" pattern (the derstandard.at input form)
    const text = el.textContent || '';
    if (/Titel/i.test(text) && /Kommentar/i.test(text) && /Posten/i.test(text)) return true;

    return false;
  }

  // ── Determine if a direct child of main is a root posting ────────────
  // On derstandard.at, the DOM inside main.forum--main looks like:
  // DST-POSTING-BOX → comment form
  // SECTION.thread → reply thread container (data-level=1 postings inside)
  // DST-POSTING[level=0] → root posting (SORTABLE)
  // SLOT → ad container between postings
  //
  // The key visual indicator (as described by users):
  // - Reply postings sit inside SECTION.thread elements with a grey left border
  // - Root postings are DST-POSTING[data-level="0"] direct children of main
  // - The "grey triangle" is the SECTION's border-left visual indicator
  function isRootPosting(el) {
    const tag = el.tagName?.toUpperCase();
    if (tag !== 'DST-POSTING') return false;

    // Primary check: data-level attribute
    const level = el.getAttribute('data-level');
    if (level === '0') return true;

    // If no data-level but it's a direct child of main (not inside a section.thread),
    // treat as root posting
    if (level === null || level === undefined) {
      const parent = el.parentElement;
      if (parent && parent.tagName?.toUpperCase() === 'MAIN') {
        console.log(
          '[DST Sorter] DST-POSTING without data-level, direct child of main — treating as root',
        );
        return true;
      }
    }

    return false;
  }

  // ── Determine if a direct child of main is a reply thread section ──
  function isReplyThreadSection(el) {
    const tag = el.tagName?.toUpperCase();
    if (tag !== 'SECTION') return false;

    // Check for thread-related CSS classes
    const cls = (el.className || '').toLowerCase();
    return cls.includes('thread');
  }

  // ── Transfer rating data from one posting to another ──────────────
  // Used to sync ratings from a duplicate (stale pinned copy) to the
  // canonical posting, ensuring sorting uses the most current numbers.
  function transferRatingsIfNewer(fromPosting, toPosting) {
    const fromRating = fromPosting.querySelector('dst-posting--ratinglog');
    const toRating = toPosting.querySelector('dst-posting--ratinglog');

    if (!fromRating || !toRating) return false;

    const fromPos = parseInt(fromRating.getAttribute('positiveratings'), 10) || 0;
    const fromNeg = parseInt(fromRating.getAttribute('negativeratings'), 10) || 0;
    const toPos = parseInt(toRating.getAttribute('positiveratings'), 10) || 0;
    const toNeg = parseInt(toRating.getAttribute('negativeratings'), 10) || 0;

    const fromTotal = fromPos + fromNeg;
    const toTotal = toPos + toNeg;

    // If 'from' has more total ratings, it's likely the newer/fresher copy
    if (fromTotal > toTotal) {
      toRating.setAttribute('positiveratings', String(fromPos));
      toRating.setAttribute('negativeratings', String(fromNeg));
      console.log(
        '[DST Sorter] Transferred fresher ratings: +' +
          fromPos +
          '/-' +
          fromNeg +
          ' (was +' +
          toPos +
          '/-' +
          toNeg +
          ')',
      );
      return true;
    }

    return false;
  }

  // ── Collect posting "groups" for sorting ───────────────────────────
  // ARCHITECTURE (based on live DOM analysis of derstandard.at 2026):
  //
  // main.forum--main children (original order):
  // [0] DST-POSTING-BOX → comment form (keep separate)
  // [1] DST-POSTING[lv=0] → root posting #1 (SORTABLE)
  // [2] SECTION.thread → reply thread for posting #1 (SIBLING)
  // [3] SLOT → ad container (SIBLING)
  // [4] DST-POSTING[lv=0] → root posting #2 (SORTABLE)
  // [5] SLOT → ad container (SIBLING)
  // ...
  //
  // Each posting "group" = the DST-POSTING element + its trailing siblings
  // (SECTION.thread + SLOT). SECTION.thread elements MUST move with their
  // parent posting to preserve the expand/collapse ("Antworten") functionality.
  // Only DST-POSTING[data-level="0"] direct children of main are sortable.
  function collectPostingGroups(main) {
    const groups = [];
    const formElements = [];
    let current = null;
    const seenPostingIds = new Map();
    let skippedSections = 0;
    let skippedSlots = 0;

    for (const child of Array.from(main.children)) {
      const tag = child.tagName?.toUpperCase();

      // ── Case 1: SECTION.thread → Reply thread container ──
      // These sections contain level-1 reply postings (the replies).
      // They MUST move together with their parent root posting during sorting,
      // otherwise the expand/collapse ("Antworten") functionality breaks.
      // We attach them as siblings of the preceding posting group.
      if (isReplyThreadSection(child)) {
        if (current) {
          current.siblings.push(child);
        }
        skippedSections++;
        continue;
      }

      // ── Case 2: DST-POSTING[data-level="0"] → Root posting → NEW sortable group ──
      // IMPORTANT: Check this BEFORE isInputFormElement, because root postings
      // contain "Antworten" buttons that would falsely match the form heuristic.
      if (isRootPosting(child)) {
        const pinned = isPinnedPosting(child);
        const postingId = getPostingId(child);

        let isDuplicate = false;
        if (postingId) {
          if (seenPostingIds.has(postingId)) {
            isDuplicate = true;
            const firstGroup = seenPostingIds.get(postingId);

            // Transfer fresher ratings from duplicate to the canonical posting
            if (firstGroup) {
              transferRatingsIfNewer(child, firstGroup.posting);
            }

            if (firstGroup && firstGroup.pinned) {
              console.log(
                '[DST Sorter] Duplicate of pinned posting detected (ID: ' + postingId + ')',
              );
            } else if (pinned) {
              if (firstGroup) firstGroup.pinned = true;
              console.log(
                '[DST Sorter] Duplicate posting, second is pinned (ID: ' + postingId + ')',
              );
            } else {
              console.log('[DST Sorter] Duplicate posting detected (ID: ' + postingId + ')');
            }
          }
        }

        current = {
          posting: child,
          siblings: [],
          pinned: pinned,
          isDuplicate: isDuplicate,
          postingId: postingId,
          domIndex: groups.length,
        };
        groups.push(current);

        if (postingId && !isDuplicate) {
          seenPostingIds.set(postingId, current);
        }

        if (pinned) {
          console.log('[DST Sorter] Pinned posting (ID: ' + (postingId || '?') + ')');
        }

        continue;
      }

      // ── Case 3: DST-POSTING-BOX or input form → comment form → keep separate ──
      if (tag === 'DST-POSTING-BOX' || isInputFormElement(child)) {
        formElements.push(child);
        continue;
      }

      // ── Case 4: SLOT (ad container) or any other element → attach to current group ──
      if (tag === 'SLOT') skippedSlots++;
      if (current) {
        current.siblings.push(child);
      }
    }

    console.log(
      '[DST Sorter] Collected ' +
        groups.length +
        ' root posting groups' +
        ' (skipped ' +
        skippedSections +
        ' reply thread sections, ' +
        skippedSlots +
        ' ad slots attached)',
    );

    return { groups, formElements };
  }

  // ── Keep reply threads collapsed by default ──
  // The forum's gear menu ("Zahnrad") has an "Antworten ausgeklappt" toggle.
  // When the user explicitly turns it ON, derStandard stores
  // "<userId>_prefers-threads": "expanded"
  // in localStorage["user-settings"]. We HONOR that choice: if the user wants
  // threads expanded we never collapse them — that makes the native gear
  // setting work again instead of being silently overridden by the extension.
  function userPrefersExpandedThreads() {
    try {
      const raw = localStorage.getItem('user-settings');
      if (!raw) return false;
      const settings = JSON.parse(raw);
      for (const key in settings) {
        if (key.indexOf('_prefers-threads') !== -1 && settings[key] === 'expanded') {
          return true;
        }
      }
    } catch (e) {
      /* ignore malformed settings */
    }
    return false;
  }

  // Collapse every reply thread that derStandard rendered as expanded, so that
  // replies are hidden until the user clicks the native "Antworten" toggle.
  // We click the real native control (button.answers) so derStandard's own
  // expand/collapse state stays in sync and the original forum functionality
  // (re-expanding on click) keeps working perfectly.
  function collapseReplyThreads(main) {
    if (!main) return;
    if (userPrefersExpandedThreads()) return; // respect the gear's "Antworten ausgeklappt"

    const expanded = main.querySelectorAll('dst-posting.posting-has-thread-expanded');
    let collapsedCount = 0;

    // treat pinned ("angeheftete") postings exactly like normal
    // ones. derStandard renders a pinned posting TWICE (two DOM nodes that share
    // the same postingId). The collapse/expand state is keyed by postingId, so if
    // we click the native toggle on BOTH copies the two toggles cancel out and the
    // thread snaps back to expanded — which is why the setting previously only
    // worked for normal (non-duplicated) postings. We therefore toggle each
    // logical posting at most ONCE per postingId.
    const processedIds = new Set();

    expanded.forEach((posting) => {
      // Only auto-collapse a given posting ONCE — never re-collapse a thread the
      // user has deliberately re-opened after our initial collapse.
      if (autoCollapsedPostings.has(posting)) return;

      // Second DOM copy of a pinned posting we already collapsed: do NOT click
      // again (that would re-expand it). Just remember the node and move on.
      const pid = getPostingId(posting);
      if (pid) {
        if (processedIds.has(pid)) {
          autoCollapsedPostings.add(posting);
          return;
        }
        processedIds.add(pid);
      }

      const toggle = posting.querySelector('button.answers');
      if (!toggle) return;

      // The native toggle marks the posting "is-active-posting" (focus highlight).
      // Remove that purely-visual side-effect if we added it, so the page doesn't
      // look like dozens of postings are selected after a bulk collapse.
      const hadActive = posting.classList.contains('is-active-posting');
      toggle.click();
      if (!hadActive) posting.classList.remove('is-active-posting');

      autoCollapsedPostings.add(posting);
      collapsedCount++;
    });

    if (collapsedCount > 0) {
      console.log(
        '[DST Sorter] Collapsed ' +
          collapsedCount +
          ' reply thread(s) — pinned & normal treated equally',
      );
    }
  }

  // (expand side): when the user enabled "Antworten ausgeklappt"
  // in the gear, derStandard expands NORMAL postings but leaves angeheftete
  // (pinned) postings collapsed. We expand those pinned postings ourselves so the
  // setting works for BOTH posting types. Normal postings are left untouched —
  // derStandard already expands them, and forcing them would override threads the
  // user collapsed by hand.
  function expandPinnedThreads(main) {
    if (!main) return;
    if (!userPrefersExpandedThreads()) return; // only when the gear wants expanded

    const candidates = main.querySelectorAll('dst-posting.posting-with-thread');
    let expandedCount = 0;
    const processedIds = new Set();

    candidates.forEach((posting) => {
      // already expanded (by derStandard or by us) → nothing to do
      if (posting.classList.contains('posting-has-thread-expanded')) return;
      // only auto-expand once, so the user can re-collapse a pinned thread
      if (autoExpandedPostings.has(posting)) return;
      // only pinned postings — normal ones are already expanded by derStandard
      if (!isPinnedPosting(posting)) return;

      // derStandard renders pinned postings twice (shared postingId); toggle the
      // logical posting only once so the two clicks don't cancel each other out.
      const pid = getPostingId(posting);
      if (pid) {
        if (processedIds.has(pid)) {
          autoExpandedPostings.add(posting);
          return;
        }
        processedIds.add(pid);
      }

      const toggle = posting.querySelector('button.answers');
      if (!toggle) return;

      // The native toggle also marks the posting "is-active-posting" (focus
      // highlight). Remove that purely-visual side-effect if we added it.
      const hadActive = posting.classList.contains('is-active-posting');
      toggle.click(); // expands asynchronously (derStandard fetches the replies)
      if (!hadActive) posting.classList.remove('is-active-posting');

      autoExpandedPostings.add(posting);
      expandedCount++;
    });

    if (expandedCount > 0) {
      console.log(
        '[DST Sorter] Expanded ' +
          expandedCount +
          ' pinned reply thread(s) to honor "Antworten ausgeklappt"',
      );
    }
  }

  // ── Sort comparator based on current mode ──────────────────────
  function sortComparator(a, b) {
    switch (sortMode) {
      case 'balance-top': {
        // Net score descending (best first)
        const aNet = getNetRatings(a.posting);
        const bNet = getNetRatings(b.posting);
        if (bNet !== aNet) return bNet - aNet;
        return getPositiveRatings(b.posting) - getPositiveRatings(a.posting);
      }
      case 'balance-flop': {
        // Net score ascending (worst/most controversial first)
        const aNet = getNetRatings(a.posting);
        const bNet = getNetRatings(b.posting);
        if (aNet !== bNet) return aNet - bNet;
        return getNegativeRatings(b.posting) - getNegativeRatings(a.posting);
      }
      case 'positive-only': {
        // Positive ratings descending
        const aPos = getPositiveRatings(a.posting);
        const bPos = getPositiveRatings(b.posting);
        if (bPos !== aPos) return bPos - aPos;
        return getNetRatings(b.posting) - getNetRatings(a.posting);
      }
      case 'negative-only': {
        // Negative ratings descending (most disliked first)
        const aNeg = getNegativeRatings(a.posting);
        const bNeg = getNegativeRatings(b.posting);
        if (bNeg !== aNeg) return bNeg - aNeg;
        return getNegativeRatings(b.posting) - getNegativeRatings(a.posting);
      }
      case 'chronological-new': {
        // Newest first (descending timestamp)
        const aTime = getPostingTimestamp(a.posting);
        const bTime = getPostingTimestamp(b.posting);
        if (aTime !== bTime) return bTime - aTime;
        // Fallback: preserve DOM order
        return (a.domIndex || 0) - (b.domIndex || 0);
      }
      case 'chronological': // legacy alias → behaves like "Old Timeline"
      case 'chronological-old': {
        // Oldest first (ascending timestamp)
        const aTime = getPostingTimestamp(a.posting);
        const bTime = getPostingTimestamp(b.posting);
        if (aTime !== bTime) return aTime - bTime;
        // Fallback: preserve DOM order
        return (a.domIndex || 0) - (b.domIndex || 0);
      }
      default:
        return 0;
    }
  }

  // ── Check if already in correct sorted order ────────────────────
  function isAlreadySorted(groups) {
    for (let i = 0; i < groups.length - 1; i++) {
      if (sortComparator(groups[i], groups[i + 1]) > 0) return false;
    }
    return true;
  }

  // ── Check if rating data is available ──────────────────────────
  function hasRatingData(main) {
    const postings = main.querySelectorAll('dst-posting[data-level="0"]');
    if (postings.length === 0) return false;
    // For timeline / no-timeline modes we don't need ratings at all
    if (sortMode.indexOf('chronological') === 0 || sortMode === 'no-timeline') return true;
    let withRatings = 0;
    postings.forEach((p) => {
      if (p.querySelector('dst-posting--ratinglog')) withRatings++;
    });
    return withRatings >= Math.min(3, postings.length) || withRatings >= postings.length * 0.5;
  }

  // ── Sort and reorder ─────────────────────────────────────────
  // ── CSS-order sort: no DOM removal/insertion! ──────────
  // Instead of removing elements from the DOM and re-inserting them
  // (which destroys derStandard.at's internal Web Component state,
  // breaking votes, counters, and visual feedback), we use CSS
  // flexbox ordering. The DOM stays completely untouched.
  function sortPostings(shadowRoot) {
    if (isSorting) return;
    isSorting = true;

    if (observer) observer.disconnect();

    try {
      const main = shadowRoot.querySelector('main.forum--main');
      if (!main) return;

      // "Timeline: New" IS derStandard's native post order — there is
      // nothing to reorder. Running the full CSS-order pipeline here (group
      // collection, duplicate scan, flex-order rewrite on every child,
      // collapse/expand pass) was pure wasted work and risked fighting the
      // page's own layout for no visual benefit. In this mode we only need
      // the rating/voter-popup wiring (click-to-see-who-rated), so we call
      // injectSortBadge directly — which attaches attachVoterListener and
      // renders the badge bar — and skip the sorting code entirely.
      if (sortMode === 'chronological-new') {
        // Undo any CSS `order` values a previous mode may have applied so the
        // page falls back to derStandard's native (already newest-first) DOM
        // order. Without this, switching FROM e.g. "Balance: Top" TO
        // "Timeline: New" would keep showing the old sorted order.
        for (const child of main.children) {
          if (child.style.order) child.style.order = '';
        }
        injectSortBadge(shadowRoot);
        return;
      }

      const { groups: allGroups, formElements } = collectPostingGroups(main);
      if (allGroups.length === 0) return;

      // Step 1: Remove duplicate postings from DOM (this is safe — duplicates aren't voted on)
      const duplicateGroups = allGroups.filter((g) => g.isDuplicate);
      if (duplicateGroups.length > 0) {
        console.log(
          '[DST Sorter] Removing ' + duplicateGroups.length + ' duplicate posting(s) from DOM',
        );
        for (const dup of duplicateGroups) {
          dup.posting.remove();
          dup.siblings.forEach((sib) => sib.remove());
        }
      }

      // Step 2: Separate pinned from regular
      const remainingGroups = allGroups.filter((g) => !g.isDuplicate);
      const pinnedGroups = remainingGroups.filter((g) => g.pinned);
      const regularGroups = remainingGroups.filter((g) => !g.pinned);

      const allSortable = remainingGroups;
      console.log(
        '[DST Sorter] CSS-ORDER sorting ' +
          allSortable.length +
          ' ROOT postings (' +
          pinnedGroups.length +
          ' pinned + ' +
          regularGroups.length +
          ' regular, mode: ' +
          sortMode +
          ')',
      );

      if (allSortable.length === 0) {
        injectSortBadge(shadowRoot);
        return;
      }

      const sig = buildSortSignature(allSortable);
      if (sig === lastSortSignature) {
        // Check if order actually needs updating
        const combined = [...pinnedGroups, ...regularGroups];
        combined.sort(sortComparator);
        // Even if signature is same, still apply order (mode may have changed)
      }

      // Sort groups
      pinnedGroups.sort(sortComparator);
      regularGroups.sort(sortComparator);

      // Combined order: pinned first, then form elements, then regular
      // We assign CSS order values to EVERY child of main — no exceptions!
      // Elements without an explicit order default to 0 in flexbox, which
      // causes them to cluster at the top and create visual gaps.

      // Enable flexbox on main (only once, idempotent)
      if (!main.style.display || main.style.display !== 'flex') {
        main.style.display = 'flex';
        main.style.flexDirection = 'column';
      }

      // CRITICAL: Hide SLOT elements (ad containers) inside the flex container.
      // Shadow DOM <slot> elements render light DOM content (ads) through the
      // slot mechanism. When flexbox reorders elements via CSS order, the slotted
      // content doesn't follow the flex layout properly, creating huge visual gaps
      // (4000+ px) between postings. Hiding slots eliminates these gaps.
      // The ads are derstandard.at's own ad containers injected between postings.
      for (const child of main.children) {
        if (child.tagName === 'SLOT') {
          child.style.display = 'none';
        }
      }

      // Build a set of all elements we know about (groups + form elements)
      const handledElements = new Set();
      for (const group of [...pinnedGroups, ...regularGroups]) {
        handledElements.add(group.posting);
        group.siblings.forEach((s) => handledElements.add(s));
      }
      formElements.forEach((f) => handledElements.add(f));

      // Collect unhandled children (headers, tab nav, ad slots not attached
      // to any group, injected elements, etc.) preserving their DOM order.
      // We split them into "before first posting" and "after last posting"
      // so headers stay at the top and trailing elements go to the bottom.
      const preElements = []; // elements before the first known element
      const postElements = []; // elements after (or between) known elements
      let seenFirstHandled = false;
      for (const child of main.children) {
        if (handledElements.has(child)) {
          seenFirstHandled = true;
          continue;
        }
        // Skip the badge bar — it gets its order separately after injection
        if (child.id === 'dst-badge-bar') {
          preElements.push(child);
          continue;
        }
        if (!seenFirstHandled) {
          preElements.push(child);
        } else {
          postElements.push(child);
        }
      }

      let orderIndex = 0;

      // 1. Pre-elements (headers, tab navigation, etc.) — keep at top
      for (const el of preElements) {
        el.style.order = String(orderIndex++);
      }

      // 2. Pinned postings (appear first among postings)
      for (const group of pinnedGroups) {
        group.posting.style.order = String(orderIndex++);
        for (const sib of group.siblings) {
          sib.style.order = String(orderIndex++);
        }
      }

      // 3. Form elements (comment box) come after pinned
      for (const formEl of formElements) {
        formEl.style.order = String(orderIndex++);
      }

      // 4. Regular postings in sorted order
      for (const group of regularGroups) {
        group.posting.style.order = String(orderIndex++);
        for (const sib of group.siblings) {
          sib.style.order = String(orderIndex++);
        }
      }

      // 5. Post-elements (trailing ads, injected elements) — push to end
      for (const el of postElements) {
        el.style.order = String(orderIndex++);
      }

      lastSortSignature = sig;
      injectSortBadge(shadowRoot);

      // Log top 5
      const groups = [...pinnedGroups, ...regularGroups];
      console.log('[DST Sorter] Top 5 after CSS-order sort:');
      for (let i = 0; i < Math.min(5, groups.length); i++) {
        const pos = getPositiveRatings(groups[i].posting);
        const neg = getNegativeRatings(groups[i].posting);
        const net = pos - neg;
        const pid = getPostingId(groups[i].posting) || '?';
        const label = groups[i].pinned ? ' [PINNED]' : '';
        console.log(
          ' ' +
            (i + 1) +
            '. Net=' +
            net +
            ' (Pos=' +
            pos +
            ', Neg=' +
            neg +
            ') [ID: ' +
            pid +
            ']' +
            label,
        );
      }

      console.log(
        '[DST Sorter] CSS-ORDER sorting complete! No DOM elements were removed or moved.',
      );

      // After (re)sorting, keep reply threads collapsed by
      // default. The observer is disconnected here, so the native toggle clicks
      // below cannot trigger a re-sort loop. Each posting is collapsed at most
      // once and the user's "Antworten ausgeklappt" gear choice is respected.
      collapseReplyThreads(main);
      // ...and, when the gear wants threads expanded, make pinned postings match
      // the normal ones (derStandard leaves pinned collapsed). Both helpers guard
      // on the gear setting internally, so exactly one of them does work.
      expandPinnedThreads(main);
    } finally {
      isSorting = false;
      observeForum(shadowRoot);
    }
  }

  // ── Badge bar: 3 grouped toggle badges ───────────────
  async function changeSortMode(newMode, shadowRoot) {
    sortMode = newMode;
    syncGroupSelection();

    if (chrome?.storage?.sync) {
      chrome.storage.sync.set({ [MODE_KEY]: sortMode });
    } else {
      localStorage.setItem(MODE_KEY, sortMode);
    }

    lastSortSignature = '';

    // Load all postings before re-sorting (if not yet loaded)
    if (autoLoadEnabled && findLoadMoreButton(shadowRoot)) {
      await loadAllPostings(shadowRoot);
      lastSortSignature = '';
    }

    sortPostings(shadowRoot);
  }

  function injectSortBadge(shadowRoot) {
    const header = shadowRoot.querySelector('.forum--header');
    if (!header) return;

    // Inject CSS into shadow DOM (once)
    if (!shadowRoot.querySelector('#dst-icon-style')) {
      const styleEl = document.createElement('style');
      styleEl.id = 'dst-icon-style';
      styleEl.textContent = ICON_STYLE_CSS;
      shadowRoot.appendChild(styleEl);
    }

    // Enable the clickable voter popup on the rating numbers.
    attachVoterListener(shadowRoot);
    try {
      shadowRoot
        .querySelectorAll('dst-posting--ratinglog:not(.dst-votable)')
        .forEach(function (el) {
          el.classList.add('dst-votable');
        });
    } catch (e) {
      /* ignore */
    }

    // Remove existing badge bar
    const existingBar = shadowRoot.querySelector('#dst-badge-bar');
    if (existingBar) existingBar.remove();

    // ── Badge bar: lives INSIDE main.forum--main ──────────────────
    // instead of inserting the bar as a sibling of the header (which
    // spans the full <section.forum> width and overflowed the frame), we insert
    // it as the FIRST CHILD of <main.forum--main>. The composer frame + all
    // posting entries live in that same container, so the bar automatically
    // inherits its exact width → both edges line up perfectly, no margin math.
    const bar = document.createElement('div');
    bar.id = 'dst-badge-bar';
    bar.style.width = '100%'; // fill main.forum--main

    // render ONE badge per button group. Each badge shows the
    // label/icon of its currently-selected sub-mode and cycles through its
    // sub-modes on click. Exactly one group is "active" at any time (the one
    // that owns the current sortMode).
    syncGroupSelection();
    BUTTON_GROUPS.forEach((group) => {
      const displayedMode = groupSelection[group.id];
      const m = MODE_DEFS[displayedMode];
      const isActive = group.modes.indexOf(sortMode) !== -1;

      // an active badge in a "low" sort mode turns red via .dst-low.
      const isLow = isActive && LOW_MODES.indexOf(displayedMode) !== -1;
      const btn = document.createElement('div');
      btn.className = 'dst-badge-btn' + (isActive ? ' active' : '') + (isLow ? ' dst-low' : '');
      btn.setAttribute('data-group', group.id);
      btn.setAttribute('data-mode', displayedMode);
      // AMO Security Fix: createElement statt innerHTML
      // Top row: icon + label side by side
      const topRow = document.createElement('span');
      topRow.className = 'dst-btn-toprow';
      // [icon][label] centred TOGETHER as one unit (icon belongs to text).
      const iconWrap = document.createElement('span');
      iconWrap.className = 'dst-btn-ico';
      m.buildIcon(iconWrap);
      const labelSpan = document.createElement('span');
      labelSpan.className = 'dst-btn-label';
      labelSpan.textContent = m.label;
      topRow.appendChild(iconWrap);
      topRow.appendChild(labelSpan);
      btn.appendChild(topRow);

      // Add dots indicator (centered BELOW the text) to show multi-mode capability
      const dotsSpan = buildDotsIndicator(group, displayedMode);
      btn.appendChild(dotsSpan);

      btn.addEventListener('click', (e) => {
        e.stopPropagation();

        let targetMode;
        if (group.modes.indexOf(sortMode) !== -1) {
          // This group is already active → advance to its next sub-mode.
          const idx = group.modes.indexOf(sortMode);
          targetMode = group.modes[(idx + 1) % group.modes.length];
        } else {
          // Switching to a different group → activate its remembered sub-mode.
          targetMode = groupSelection[group.id];
        }
        groupSelection[group.id] = targetMode;

        // Re-sort with the new mode (this re-renders the badge bar too).
        changeSortMode(targetMode, shadowRoot);

        // After re-render, find the new active badge and animate it
        setTimeout(() => {
          const newActive = shadowRoot.querySelector('.dst-badge-btn.active');
          if (newActive) {
            newActive.classList.add('pulse');
            newActive.addEventListener(
              'animationend',
              () => {
                newActive.classList.remove('pulse');
              },
              { once: true },
            );
          }
        }, 50);
      });

      bar.appendChild(btn);
    });

    // Insert the bar as the FIRST CHILD of main.forum--main so it
    // inherits that container's exact width (aligns with the composer frame &
    // posting entries). Fall back to the old sibling-of-header placement only
    // if main.forum--main can't be found.
    const mainEl = shadowRoot.querySelector('main.forum--main');
    if (mainEl) {
      mainEl.insertBefore(bar, mainEl.firstChild);
    } else if (header.nextSibling) {
      header.parentNode.insertBefore(bar, header.nextSibling);
    } else if (header.parentNode) {
      header.parentNode.appendChild(bar);
    } else {
      header.appendChild(bar);
    }
  }

  function removeSortBadge(shadowRoot) {
    const bar = shadowRoot.querySelector('#dst-badge-bar');
    if (bar) bar.remove();
  }

  // ── Debounced sort ────────────────────────────────────────────
  function scheduledSort(shadowRoot) {
    if (sortTimeout) clearTimeout(sortTimeout);
    sortTimeout = setTimeout(() => {
      if (sortEnabled) sortPostings(shadowRoot);
    }, 300);
  }

  // ── Observe mutations inside forum shadow root ────────────────
  // CRITICAL FIX: Do NOT observe rating attribute changes at all.
  //
  // PROBLEM (older versions):
  // When a user clicks +/- (upvote/downvote), derStandard.at updates the
  // positiveratings/negativeratings attributes on dst-posting--ratinglog.
  // Even with a 2-second debounce delay, the subsequent sortPostings() call
  // removes ALL postings from the DOM and re-inserts them in sorted order.
  // This DOM manipulation destroys derStandard.at's internal vote state,
  // causing the vote counter to revert and the vote to not be saved.
  //
  // SOLUTION:
  // - Only observe childList changes (new postings being loaded)
  // - NEVER react to rating attribute changes
  // - Sorting based on updated ratings only happens on:
  // a) Manual badge bar click (user explicitly requests re-sort)
  // b) New postings loaded (childList mutation)
  // c) Page load / tab switch
  // This ensures the extension NEVER interferes with the vote process.
  function observeForum(shadowRoot) {
    if (observer) observer.disconnect();

    const main = shadowRoot.querySelector('main.forum--main');
    if (!main) return;

    observer = new MutationObserver((mutations) => {
      if (isSorting) return;

      let hasNewPosting = false;

      for (const mutation of mutations) {
        // CRITICAL: Only react to childList changes directly on main.
        // Ignore subtree changes (e.g. vote counter text updates inside postings).
        // When derStandard.at updates a vote counter, it changes textContent inside
        // a nested element — that's a childList mutation on a CHILD node, not on main.
        // We only care about new DST-POSTING elements being added to main directly.
        if (mutation.type === 'childList' && mutation.target === main) {
          // Check if any added node is a posting (new comment loaded)
          for (const node of mutation.addedNodes) {
            if (
              node.nodeType === 1 &&
              (node.tagName === 'DST-POSTING' ||
                node.tagName === 'SECTION' ||
                node.tagName === 'SLOT')
            ) {
              hasNewPosting = true;
              break;
            }
          }
          if (hasNewPosting) break;
        }
      }

      if (hasNewPosting) {
        scheduledSort(shadowRoot);
      }
    });

    // Only childList on main's direct children — NO subtree, NO attributes!
    // subtree:false ensures we only see changes to main's direct children,
    // not internal DOM changes within postings (like vote counter updates).
    observer.observe(main, {
      childList: true,
      subtree: false,
    });
  }

  // ── URL check: is this an article page? ─────────────────────────
  function isArticlePage() {
    const path = window.location.pathname;
    return /\/story\//.test(path);
  }

  // ── Auto-load forum by clicking on "X Postings" link ──────────
  function autoLoadForum() {
    if (!isArticlePage()) {
      console.log(
        '[DST Sorter] Auto-load SKIPPED: not an article page (' + window.location.pathname + ')',
      );
      return false;
    }

    if (autoLoadClicked) {
      console.log('[DST Sorter] Auto-load SKIPPED: already clicked on this page');
      return false;
    }

    if (!autoLoadEnabled) {
      console.log('[DST Sorter] Auto-load SKIPPED: disabled in settings');
      return false;
    }

    if (document.querySelector('dst-forum')) {
      console.log('[DST Sorter] Auto-load SKIPPED: forum already present');
      return false;
    }

    const postingsLink = Array.from(document.querySelectorAll('a, button')).find((el) => {
      if (!el.textContent || !/\d+\s*Posting/i.test(el.textContent)) return false;
      if (el.tagName === 'A' && el.href) {
        const linkUrl = new URL(el.href, window.location.origin);
        if (linkUrl.pathname !== window.location.pathname) {
          return false;
        }
      }
      return true;
    });

    if (postingsLink) {
      autoLoadClicked = true;
      console.log('[DST Sorter] Found postings link on article page, clicking automatically...');
      setTimeout(() => {
        postingsLink.click();
      }, 300);
      return true;
    }
    return false;
  }

  // ── Load ALL postings by clicking "Weitere Postings laden" ──
  // The button is a direct child of section.forum in the shadow DOM.
  // Class: "form--button thread--more" (BEM notation with double hyphens!)
  // querySelector doesn't work on it — must iterate section.forum.children.
  // Each click loads ~90 new postings. We keep clicking until the button
  // disappears (all postings loaded) or we hit the safety limit.

  function findLoadMoreButton(shadowRoot) {
    // Strategy 1: Search inside shadow root for section.forum > BUTTON
    const section = shadowRoot.querySelector('section.forum');
    if (section) {
      for (const child of section.children) {
        if (child.tagName === 'BUTTON') {
          const text = (child.textContent || '').trim().toLowerCase();
          if (text.includes('weitere') && text.includes('posting')) {
            return child;
          }
          const cls = child.getAttribute('class') || '';
          if (cls.includes('thread') && cls.includes('more')) {
            return child;
          }
        }
      }
    }
    // Strategy 2: Search in main document (button may be outside shadow DOM)
    const docSection = document.querySelector('section.forum');
    if (docSection) {
      for (const child of docSection.children) {
        if (child.tagName === 'BUTTON') {
          const text = (child.textContent || '').trim().toLowerCase();
          if (text.includes('weitere') && text.includes('posting')) {
            return child;
          }
          const cls = child.getAttribute('class') || '';
          if (cls.includes('thread') && cls.includes('more')) {
            return child;
          }
        }
      }
    }
    // Strategy 3: Search inside dst-forum light DOM (slotted children)
    const dstForum = document.querySelector('dst-forum');
    if (dstForum) {
      for (const child of dstForum.children) {
        if (child.tagName === 'BUTTON') {
          const text = (child.textContent || '').trim().toLowerCase();
          if (text.includes('weitere') && text.includes('posting')) {
            return child;
          }
          const cls = child.getAttribute('class') || '';
          if (cls.includes('thread') && cls.includes('more')) {
            return child;
          }
        }
      }
    }
    return null;
  }

  function getTotalPostingCount(shadowRoot) {
    // read the TOTAL posting count from the dedicated count element
    // derStandard renders (verified live on the forum DOM):
    // • .forum--postingcount (inside dst-forum shadow) → "143 Postings und Antworten"
    // • .js-forum-postingcount (main doc) → "143 Postings"
    // • .article-postingcount (button under the headline) → "143 Postings"
    // We query these SPECIFIC classes in priority order instead of the old
    // greedy `[class*="postingcount"]`, which could accidentally match an
    // unrelated per-thread counter (e.g. a reply count of "1") and thus show
    // "X / 1" during loading. Numbers may carry a German thousands separator
    // ("1.234"), so we strip dots/whitespace before parsing.
    const selectors = ['.forum--postingcount', '.js-forum-postingcount', '.article-postingcount'];
    for (let i = 0; i < selectors.length; i++) {
      const sel = selectors[i];
      const el = (shadowRoot && shadowRoot.querySelector(sel)) || document.querySelector(sel);
      if (el) {
        const m = (el.textContent || '').match(/(\d[\d.\s]*)/);
        if (m) {
          const n = parseInt(m[1].replace(/[.\s]/g, ''), 10);
          if (n > 0) return n;
        }
      }
    }
    return 0;
  }

  // ── Progress bar replaces badge bar during loading ──────
  function showProgressBar(shadowRoot, loaded, total, message) {
    const bar = shadowRoot.querySelector('#dst-badge-bar');
    if (!bar) return;

    // Hide all badge buttons
    for (const child of bar.children) {
      if (child.id !== 'dst-progress-container') {
        child.style.display = 'none';
      }
    }

    let container = bar.querySelector('#dst-progress-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'dst-progress-container';
      container.style.cssText = 'flex:1;display:flex;flex-direction:column;gap:3px;min-width:0;';
      bar.appendChild(container);
    }

    // guard the denominator. A trustworthy total is always ≥ the
    // number already loaded; if detection returned something smaller (or 0),
    // fall back to the loaded count so we never render a bogus "X / 1".
    const validTotal = total && total >= loaded ? total : 0;
    const percentage = validTotal > 0 ? Math.round((loaded / validTotal) * 100) : 0;

    // Build progress bar HTML using DOM methods (AMO safe)
    container.textContent = ''; // clear

    // Outer bar
    const outer = document.createElement('div');
    outer.style.cssText =
      'width:100%;height:28px;background:#e8e8e8;border-radius:14px;position:relative;overflow:hidden;box-shadow:inset 0 1px 3px rgba(0,0,0,0.1);';

    // Inner fill
    const fill = document.createElement('div');
    fill.style.cssText =
      'position:absolute;left:0;top:0;height:100%;width:' +
      percentage +
      '%;background:linear-gradient(90deg,#8FAF6F,#B7CCA3);border-radius:14px;transition:width 0.4s ease;';

    // Pulse animation on fill
    const pulseStyle = document.createElement('style');
    pulseStyle.id = 'dst-pulse-style';
    if (!shadowRoot.querySelector('#dst-pulse-style')) {
      pulseStyle.textContent =
        '@keyframes dst-progress-pulse{0%{opacity:1}50%{opacity:0.7}100%{opacity:1}} #dst-progress-fill{animation:dst-progress-pulse 1.5s ease-in-out infinite}';
      shadowRoot.appendChild(pulseStyle);
    }
    fill.id = 'dst-progress-fill';

    // Text overlay
    const textEl = document.createElement('span');
    textEl.style.cssText =
      'position:absolute;left:0;top:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:#2e7d32;font-weight:700;font-size:12px;z-index:1;text-shadow:0 0 3px rgba(255,255,255,0.8);';
    // show "X / Y" only when we have a trustworthy total; otherwise
    // just show the loaded count (never the bogus "/ 1").
    textEl.textContent =
      message ||
      (validTotal > 0
        ? 'Lade alle Postings... ' + loaded + ' / ' + validTotal
        : 'Lade alle Postings... ' + loaded);

    outer.appendChild(fill);
    outer.appendChild(textEl);
    container.appendChild(outer);
  }

  function hideProgressBar(shadowRoot) {
    const bar = shadowRoot.querySelector('#dst-badge-bar');
    if (!bar) return;

    const container = bar.querySelector('#dst-progress-container');
    if (container) container.remove();

    // Show all badge buttons again
    for (const child of bar.children) {
      child.style.display = '';
    }

    // Remove pulse style
    const pulseStyle = shadowRoot.querySelector('#dst-pulse-style');
    if (pulseStyle) pulseStyle.remove();
  }

  function showProgressComplete(shadowRoot, totalPostings) {
    const bar = shadowRoot.querySelector('#dst-badge-bar');
    if (!bar) return;

    const container = bar.querySelector('#dst-progress-container');
    if (container) {
      container.textContent = '';
      const outer = document.createElement('div');
      outer.style.cssText =
        'width:100%;height:28px;background:linear-gradient(90deg,#8FAF6F,#B7CCA3);border-radius:14px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(46,125,50,0.25);';
      const textEl = document.createElement('span');
      textEl.style.cssText =
        'color:white;font-weight:700;font-size:12px;text-shadow:0 1px 2px rgba(0,0,0,0.2);';
      textEl.textContent = '✓ Alle ' + totalPostings + ' Postings geladen!';
      outer.appendChild(textEl);
      container.appendChild(outer);
    }

    // After 1.5s, hide progress and show badges again
    setTimeout(function () {
      hideProgressBar(shadowRoot);
    }, 1500);
  }

  async function loadAllPostings(shadowRoot) {
    if (isLoadingAllPostings) {
      console.log('[DST Sorter] loadAllPostings already in progress, skipping');
      return false;
    }
    if (!autoLoadEnabled) {
      console.log('[DST Sorter] loadAllPostings SKIPPED: auto-load disabled');
      return false;
    }

    let btn = findLoadMoreButton(shadowRoot);
    if (!btn) {
      console.log(
        '[DST Sorter] No "Weitere Postings laden" button found — all postings already loaded',
      );
      return false;
    }

    isLoadingAllPostings = true;
    const totalExpected = getTotalPostingCount(shadowRoot);
    let loadCount = 0;
    const MAX_LOADS = 50; // Safety limit (50 × ~90 = ~4500 postings max)
    let consecutiveFailures = 0; // Track consecutive failures

    console.log('[DST Sorter] ⏳ Loading ALL postings... (expected: ' + totalExpected + ')');

    // Ensure badge bar exists before showing progress
    injectSortBadge(shadowRoot);
    const currentLoaded = shadowRoot.querySelectorAll('dst-posting').length;
    showProgressBar(shadowRoot, currentLoaded, totalExpected, 'Lade alle Postings...');

    // Disconnect observer during loading to prevent re-sorting on each batch
    if (observer) observer.disconnect();

    while (btn && loadCount < MAX_LOADS) {
      loadCount++;
      const beforeCount = shadowRoot.querySelectorAll('dst-posting').length;

      // Show progress bar
      showProgressBar(shadowRoot, beforeCount, totalExpected);
      console.log(
        '[DST Sorter] Loading batch ' + loadCount + ' (currently: ' + beforeCount + ' postings)',
      );

      // Click the button
      try {
        btn.click();
      } catch (e) {
        console.log('[DST Sorter] Button click failed: ' + e.message);
        break;
      }

      // Wait for new postings to load
      const newPostingsLoaded = await new Promise(function (resolve) {
        let waited = 0;
        const pollInterval = 250;
        const maxWait = 10000; // 10 seconds max per batch
        const poll = setInterval(function () {
          waited += pollInterval;
          const currentCount = shadowRoot.querySelectorAll('dst-posting').length;
          if (currentCount > beforeCount) {
            // New postings loaded!
            clearInterval(poll);
            setTimeout(function () {
              resolve(true);
            }, 400); // Extra delay for DOM to settle
          } else if (waited >= maxWait) {
            // Timeout — button might have disappeared (all loaded)
            clearInterval(poll);
            resolve(false);
          }
        }, pollInterval);
      });

      if (!newPostingsLoaded) {
        consecutiveFailures++;
        console.log(
          '[DST Sorter] Batch ' +
            loadCount +
            ' timeout (consecutive failures: ' +
            consecutiveFailures +
            ')',
        );
        if (consecutiveFailures >= 3) {
          console.log('[DST Sorter] Too many consecutive failures, stopping');
          break;
        }
      } else {
        consecutiveFailures = 0;
      }

      // Re-find button (it gets replaced in the DOM after each batch)
      btn = findLoadMoreButton(shadowRoot);
    }

    const finalCount = shadowRoot.querySelectorAll('dst-posting').length;
    const rootCount = shadowRoot.querySelectorAll('dst-posting[data-level="0"]').length;
    console.log(
      '[DST Sorter] ✅ All postings loaded! ' +
        loadCount +
        ' batches, ' +
        finalCount +
        ' total postings (' +
        rootCount +
        ' root)',
    );

    // Show completion
    showProgressComplete(shadowRoot, finalCount);

    isLoadingAllPostings = false;
    return true;
  }

  // ── Wait for the dst-forum element and its shadow root ────────
  function waitForForum() {
    const forum = document.querySelector('dst-forum');
    if (forum && forum.shadowRoot) {
      console.log('[DST Sorter] Forum already loaded, initializing sort...');
      initSort(forum.shadowRoot);
      return;
    }

    const autoLoaded = autoLoadForum();
    console.log('[DST Sorter] Auto-load forum: ' + (autoLoaded ? 'SUCCESS' : 'NO LINK FOUND'));

    const docObserver = new MutationObserver(() => {
      const f = document.querySelector('dst-forum');
      if (f && f.shadowRoot) {
        console.log('[DST Sorter] Forum element detected via MutationObserver');
        docObserver.disconnect();
        initSort(f.shadowRoot);
      }
    });
    docObserver.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true,
    });

    let attempts = 0;
    const poll = setInterval(() => {
      attempts++;
      const f = document.querySelector('dst-forum');
      if (f && f.shadowRoot) {
        console.log('[DST Sorter] Forum element detected via polling (attempt ' + attempts + ')');
        clearInterval(poll);
        docObserver.disconnect();
        initSort(f.shadowRoot);
      }
      if (attempts > 100) {
        console.log('[DST Sorter] Timeout: Forum element not found after 50 seconds');
        clearInterval(poll);
      }
    }, 500);
  }

  // ── Initialise sorting ────────────────────────────────────────
  function initSort(shadowRoot) {
    const main = shadowRoot.querySelector('main.forum--main');
    if (!main || main.querySelectorAll('dst-posting[data-level="0"]').length === 0) {
      const innerObs = new MutationObserver(() => {
        const posts = main?.querySelectorAll('dst-posting[data-level="0"]');
        if (posts && posts.length > 0) {
          innerObs.disconnect();
          waitForRatingsAndSort(shadowRoot);
        }
      });
      if (main) {
        innerObs.observe(main, { childList: true, subtree: true });
      }
      return;
    }
    waitForRatingsAndSort(shadowRoot);
  }

  // ── Wait for rating data before first sort ────────────────────
  function waitForRatingsAndSort(shadowRoot) {
    const main = shadowRoot.querySelector('main.forum--main');
    if (!main) return;

    if (hasRatingData(main)) {
      // Properly handle async runSort
      runSort(shadowRoot).catch(function (e) {
        console.log('[DST Sorter] runSort error: ' + e.message);
      });
      return;
    }

    let ratingWaitAttempts = 0;
    const maxWaitAttempts = 30;

    const ratingPoll = setInterval(function () {
      ratingWaitAttempts++;
      if (hasRatingData(main)) {
        clearInterval(ratingPoll);
        runSort(shadowRoot).catch(function (e) {
          console.log('[DST Sorter] runSort error: ' + e.message);
        });
      } else if (ratingWaitAttempts >= maxWaitAttempts) {
        clearInterval(ratingPoll);
        runSort(shadowRoot).catch(function (e) {
          console.log('[DST Sorter] runSort error: ' + e.message);
        });
      }
    }, 500);
  }

  async function runSort(shadowRoot) {
    // First do an initial sort with whatever postings are available,
    // then load all remaining postings and re-sort.
    // This gives the user immediate visual feedback while loading continues.

    if (sortEnabled) {
      // Initial sort with available postings
      sortPostings(shadowRoot);
    }

    // Load ALL postings (if auto-load enabled and button exists)
    if (sortEnabled && autoLoadEnabled) {
      // Small delay to let the badge bar render first
      await new Promise(function (r) {
        setTimeout(r, 500);
      });

      const loadMoreExists = findLoadMoreButton(shadowRoot);
      if (loadMoreExists) {
        console.log(
          '[DST Sorter] "Weitere Postings laden" button found — loading all before re-sort',
        );
        const loaded = await loadAllPostings(shadowRoot);
        if (loaded) {
          // Re-sort with all postings now loaded
          lastSortSignature = '';
          sortPostings(shadowRoot);
        }
      }
    }

    observeForum(shadowRoot);

    // Only ONE delayed re-sort (for late-loading ratings)
    setTimeout(function () {
      if (sortEnabled) {
        const main = shadowRoot.querySelector('main.forum--main');
        if (main) {
          const { groups: allGrps } = collectPostingGroups(main);
          const sortableGrps = allGrps.filter(function (g) {
            return !g.isDuplicate;
          });
          const newSig = buildSortSignature(sortableGrps);
          if (newSig !== lastSortSignature) {
            sortPostings(shadowRoot);
          }
        }
      }
    }, 3000);

    // Listen for manual "Weitere Postings laden" clicks
    const moreBtn = findLoadMoreButton(shadowRoot);
    if (moreBtn) {
      moreBtn.addEventListener('click', function () {
        setTimeout(function () {
          scheduledSort(shadowRoot);
        }, 2000);
      });
    }

    const tabs = shadowRoot.querySelectorAll('dst-forum--tabnavigation button.tab');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        lastSortSignature = '';
        setTimeout(function () {
          scheduledSort(shadowRoot);
        }, 1500);
      });
    });
  }

  // ── Storage migration: old format -> new format ────────────────
  function migrateStorage(data) {
    const currentMode = data[MODE_KEY];
    // Already in current format
    if (currentMode && ALL_MODES.indexOf(currentMode) !== -1) {
      return currentMode;
    }
    // "no-timeline" removed (was identical to chronological-new)
    if (currentMode === 'no-timeline') return 'chronological-new';
    // the single "chronological" mode was split into timeline sub-modes.
    // The old behaviour was "oldest first" → map to chronological-old.
    if (currentMode === 'chronological') return 'chronological-old';
    // Migrate old format
    if (currentMode === 'net') return 'balance-top';
    if (currentMode === 'positive') return 'positive-only';
    // Check legacy boolean key (very old versions)
    if (data.sortByPositive === true) return 'positive-only';
    if (data.sortByPositive === false) return 'balance-top';
    // Default
    return 'balance-top';
  }

  // ── Storage: persist enabled state & sort mode ─────────────────
  function loadState(callback) {
    if (chrome?.storage?.sync) {
      chrome.storage.sync.get([SORT_KEY, MODE_KEY, AUTOLOAD_KEY, 'sortByPositive'], (data) => {
        sortEnabled = data[SORT_KEY] !== false;
        sortMode = migrateStorage(data);
        syncGroupSelection();
        autoLoadEnabled = data[AUTOLOAD_KEY] !== false;

        // Persist migrated mode if it changed
        const oldMode = data[MODE_KEY];
        if (oldMode !== sortMode) {
          chrome.storage.sync.set({ [MODE_KEY]: sortMode });
          console.log(
            '[DST Sorter] Migrated sort mode from "' + oldMode + '" to "' + sortMode + '"',
          );
        }

        callback();
      });
    } else {
      sortEnabled = localStorage.getItem(SORT_KEY) !== 'false';
      const rawMode = localStorage.getItem(MODE_KEY);
      sortMode = migrateStorage({ [MODE_KEY]: rawMode });
      syncGroupSelection();
      autoLoadEnabled = localStorage.getItem(AUTOLOAD_KEY) !== 'false';
      if (rawMode !== sortMode) {
        localStorage.setItem(MODE_KEY, sortMode);
      }
      callback();
    }
  }

  // Listen for messages from popup
  if (chrome?.runtime?.onMessage) {
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg.action === 'toggle') {
        sortEnabled = msg.enabled;
        const forum = document.querySelector('dst-forum');
        if (forum && forum.shadowRoot) {
          if (sortEnabled) {
            lastSortSignature = '';
            sortPostings(forum.shadowRoot);
          } else {
            removeSortBadge(forum.shadowRoot);
            location.reload();
          }
        }
      }
      if (msg.action === 'setMode') {
        sortMode = msg.mode;
        syncGroupSelection();
        const forum = document.querySelector('dst-forum');
        if (forum && forum.shadowRoot) {
          if (sortEnabled) {
            lastSortSignature = '';
            sortPostings(forum.shadowRoot);
          }
        }
      }
      if (msg.action === 'setAutoLoad') {
        autoLoadEnabled = msg.enabled;
      }
      if (msg.action === 'getState') {
        return true;
      }
    });
  }

  // ── Entry point ───────────────────────────────────────────────
  loadState(() => {
    if (sortEnabled) {
      waitForForum();
      waitForProfileFeed();
    }
  });
})();
