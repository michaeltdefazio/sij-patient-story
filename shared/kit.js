/* Patient sites kit: first-visit hint for the tab bar, folds that open for in-page links and for print. */
(function () {
  'use strict';
  var d = document;
  var folds = [].slice.call(d.querySelectorAll('details.fold'));
  function openFor(el) {
    var p = el && el.closest ? el.closest('details') : null;
    while (p) { p.open = true; p = p.parentElement ? p.parentElement.closest('details') : null; }
  }
  function toHash() {
    if (location.hash.length < 2) return;
    var t = null;
    try { t = d.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (e) {}
    if (t) { openFor(t); setTimeout(function () { try { t.scrollIntoView(); } catch (e) {} }, 40); }
  }
  window.addEventListener('hashchange', toHash);
  toHash();
  d.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var id = a.getAttribute('href').slice(1);
    var t = id ? d.getElementById(id) : null;
    if (t) openFor(t);
  });
  var reopen = [];
  window.addEventListener('beforeprint', function () { reopen = folds.filter(function (f) { return !f.open; }); reopen.forEach(function (f) { f.open = true; }); });
  window.addEventListener('afterprint', function () { reopen.forEach(function (f) { f.open = false; }); reopen = []; });


  /* share button: the phone's share sheet when there is one, otherwise copy the link */
  d.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-kshare]') : null;
    if (!b) return;
    var data = { title: d.title, url: location.href.split('#')[0].split('?')[0] };
    var note = b.querySelector('small'), orig = note ? note.textContent : '';
    function say(t) { if (note) { note.textContent = t; setTimeout(function () { note.textContent = orig; }, 2600); } }
    if (navigator.share) { navigator.share(data).catch(function () {}); return; }
    try { navigator.clipboard.writeText(data.url).then(function () { say('Link copied. Paste it into a message.'); }, function () { say(data.url); }); }
    catch (x) { say(data.url); }
  });

  /* one-time pointer to the tab bar on the home page (once per visit when storage works) */
  var tabs = d.querySelector('.tabs');
  if (!tabs || d.body.getAttribute('data-page') !== 'home') return;
  var seen = false, key = 'kit-coach:' + location.pathname.replace(/[^/]*$/, '');
  try { seen = sessionStorage.getItem(key) === '1'; } catch (e) {}
  if (seen) return;
  var c = d.createElement('button');
  c.type = 'button'; c.className = 'coach no-print'; c.setAttribute('aria-label', 'Hint: the tabs at the bottom of the screen open the other pages of this site. Tap to hide this hint.');
  c.textContent = 'Tap the tabs below to explore';
  d.body.appendChild(c);
  tabs.classList.add('nudge');
  function gone() {
    if (!c.parentNode) return;
    c.parentNode.removeChild(c);
    tabs.classList.remove('nudge');
    try { sessionStorage.setItem(key, '1'); } catch (e) {}
    window.removeEventListener('scroll', onScroll);
  }
  var y0 = window.scrollY, onScroll = function () { if (Math.abs(window.scrollY - y0) > 160) gone(); };
  window.addEventListener('scroll', onScroll, { passive: true });
  c.addEventListener('click', gone);
  tabs.addEventListener('click', gone);
  setTimeout(gone, 12000);
})();
