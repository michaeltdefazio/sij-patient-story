/* Pre-visit form: one answer per question, builds a one-page summary for the doctor.
   Nothing is saved or sent anywhere. */
(function () {
  'use strict';
  var root = document.getElementById('intake');
  if (!root) return;
  var DOC = root.getAttribute('data-doc') || 'my doctor';
  var SHORT = root.getAttribute('data-short') || 'my doctor';
  var CONTACT = root.getAttribute('data-contact') || '';
  var form = document.getElementById('intake-form');
  var body = document.getElementById('sum-body');
  var actions = document.getElementById('sum-actions');
  var statusEl = document.getElementById('sum-status');
  var bar = document.getElementById('prog-bar');
  var progTxt = document.getElementById('prog-txt');
  var floatBtn = document.getElementById('float-sum');
  var box = document.getElementById('summary');
  var nameEl = document.getElementById('f_name');
  var inView = false, any = false;

  var txt = function (s) { return String(s || '').replace(/\s+/g, ' ').trim(); };
  var all = function (sel, ctx) { return Array.prototype.slice.call((ctx || form).querySelectorAll(sel)); };
  var one = function (key) { var c = form.querySelector('input[name="' + key + '"]:checked'); return c ? c.value : ''; };
  var many = function (key) { return all('input[name="' + key + '"]:checked').map(function (c) { return c.value; }); };
  var field = function (key) { var f = document.getElementById('f_' + key); return f ? txt(f.value) : ''; };

  /* show follow-up questions only when they apply; clear them when they stop applying */
  var conditionals = function () {
    all('[data-show-if]').forEach(function (el) {
      var p = el.getAttribute('data-show-if').split('=');
      var show = p[1].split('|').indexOf(one(p[0])) !== -1;
      if (!show && !el.hidden) {
        all('input', el).forEach(function (i) { i.checked = false; if (i.type === 'text') i.value = ''; });
        all('input[type="text"], textarea', el).forEach(function (i) { i.value = ''; });
      }
      el.hidden = !show;
    });
  };
  var marks = function () {
    all('label.opt').forEach(function (l) { var i = l.querySelector('input'); l.classList.toggle('on', !!(i && i.checked)); });
  };
  /* cap the suggested questions so people choose instead of tapping everything */
  var cap = function () {
    var fsEl = form.querySelector('fieldset[data-cap]');
    if (!fsEl) return;
    var max = parseInt(fsEl.getAttribute('data-cap'), 10) || 3;
    var boxes = all('input', fsEl), n = boxes.filter(function (b) { return b.checked; }).length;
    boxes.forEach(function (b) {
      var off = !b.checked && n >= max;
      b.disabled = off;
      b.parentNode.classList.toggle('dis', off);
    });
    var note = document.getElementById('askcap');
    if (note) note.textContent = n >= max ? 'You picked ' + max + '. Untick one to pick a different question.' : (max - n) + (max - n === 1 ? ' pick left' : ' picks left');
  };
  var progress = function () {
    var sets = all('fieldset[data-count]').filter(function (f) { return !f.closest('[hidden]'); });
    var done = sets.filter(function (f) { return f.querySelector('input:checked'); }).length;
    bar.style.width = Math.round(100 * done / sets.length) + '%';
    progTxt.textContent = done + ' of ' + sets.length + ' questions answered';
  };

  /* ---- the summary ---- */
  var TR = [['tr_pt', 'Physical therapy'], ['tr_chiro', 'Chiropractic care'], ['tr_brace', 'Brace or SI belt'], ['tr_med', 'Pain medicine'],
            ['tr_inj', 'Spine or other injections'], ['tr_sij', 'SI joint injection'], ['tr_rfa', 'Radiofrequency ablation (RFA)']];
  var model = function () {
    var m = { now: one('now'), worst: one('worst'), pain: [], history: [], tried: [], goal: field('goal'), asks: [] };
    var add = function (list, k, v) { if (v) list.push([k, v]); };
    add(m.pain, 'Side', one('side'));
    add(m.pain, 'Where', many('where').join(', '));
    add(m.pain, 'One-finger spot', one('finger'));
    add(m.pain, 'Worse with', many('worse').join(', '));
    add(m.pain, 'Limits my day', one('limit'));
    add(m.pain, 'How long', one('dur'));
    var s = one('surg');
    if (s === 'Yes') {
      var parts = ['Yes'], lv = many('surg_lvl'), ty = one('surg_type'), yr = field('surg_year');
      if (lv.length) parts.push(lv.join(', '));
      if (ty) parts.push(ty.toLowerCase());
      if (yr) parts.push(yr);
      s = parts.join(' · ');
    }
    add(m.history, 'Back surgery', s);
    add(m.history, 'Pregnancy', one('preg') === 'Yes' ? 'Pain started during or after a pregnancy' : (one('preg') === 'No' ? 'Pain did not start with a pregnancy' : (one('preg') ? 'Does not apply' : '')));
    add(m.history, 'Fall or injury', one('inj') === 'Yes' ? 'Pain started after a fall or injury' : (one('inj') === 'No' ? 'Pain did not start with a fall or injury' : (one('inj') ? 'Not sure' : '')));
    TR.forEach(function (t) {
      var v = one(t[0]);
      if (!v) return;
      if (t[0] === 'tr_sij' && v === 'Helped') {
        var d = [], r = one('sij_relief'), du = one('sij_dur');
        if (r) d.push(r.toLowerCase() + ' relief');
        if (du) d.push('lasted ' + du.toLowerCase());
        if (d.length) v += ' (' + d.join(', ') + ')';
      }
      m.tried.push([t[1], v]);
    });
    var note = field('tried_note');
    if (note) m.tried.push(['Notes', note]);
    many('ask').forEach(function (q) { m.asks.push(q); });
    if (field('own_q')) m.asks.push(field('own_q'));
    m.any = !!(m.now || m.worst || m.pain.length || m.history.length || m.tried.length || m.goal || m.asks.length);
    return m;
  };
  var today = function () { try { return new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }); } catch (e) { return ''; } };
  var el = function (tag, cls, t) { var n = document.createElement(tag); if (cls) n.className = cls; if (t != null) n.textContent = t; return n; };
  var dl = function (rows) {
    var d = el('dl', 'sd');
    rows.forEach(function (r) { d.appendChild(el('dt', '', r[0])); d.appendChild(el('dd', '', r[1])); });
    return d;
  };
  var render = function () {
    var m = model();
    any = m.any;
    body.textContent = '';
    if (actions) actions.hidden = !any;
    if (floatBtn) floatBtn.hidden = !(any && !inView);
    if (!any) { body.appendChild(el('p', 'sum-empty', 'Answer the questions above and your summary appears here.')); return; }
    var nm = field('name');
    body.appendChild(el('p', 'sum-meta', (nm ? 'Patient: ' + nm + ' · ' : '') + 'Prepared ' + today()));
    if (m.now || m.worst) {
      var sc = el('div', 'sum-scores');
      [['Pain now', m.now], ['Worst this week', m.worst]].forEach(function (x) {
        var c = el('div', 'sum-score'); c.appendChild(el('b', '', x[0]));
        if (x[1]) { c.appendChild(el('span', '', x[1])); c.appendChild(el('small', '', ' / 10')); } else { c.appendChild(el('span', '', '–')); }
        sc.appendChild(c);
      });
      body.appendChild(sc);
    }
    var block = function (title, node) { body.appendChild(el('h3', 'sh', title)); body.appendChild(node); };
    if (m.pain.length) block('Pain', dl(m.pain));
    if (m.history.length) block('History', dl(m.history));
    if (m.tried.length) block('What I have tried', dl(m.tried));
    if (m.goal) block('What I want to do again', dl([['Goal', m.goal]]));
    if (m.asks.length) {
      var ol = el('ol', 'sq'); m.asks.forEach(function (q) { ol.appendChild(el('li', '', q)); });
      block('My questions for ' + SHORT, ol);
    }
    var br = el('p', 'sum-bring'); br.appendChild(el('b', '', 'Bring: ')); br.appendChild(document.createTextNode('your imaging reports or discs, a list of your medicines with doses, and your insurance card.'));
    body.appendChild(br);
    body.appendChild(el('p', 'sum-foot', 'Reported by the patient on a website. This is not a medical record.'));
  };
  var asText = function () {
    var m = model(), nm = field('name'), L = [];
    L.push('Pre-visit summary for ' + DOC);
    if (CONTACT) L.push(CONTACT);
    L.push((nm ? 'Patient: ' + nm + ' · ' : '') + 'Prepared ' + today(), '');
    if (m.now || m.worst) L.push('Pain now: ' + (m.now ? m.now + '/10' : 'not answered') + '. Worst this week: ' + (m.worst ? m.worst + '/10' : 'not answered') + '.', '');
    var sec = function (title, rows) { if (!rows.length) return; L.push(title.toUpperCase()); rows.forEach(function (r) { L.push('- ' + r[0] + ': ' + r[1]); }); L.push(''); };
    sec('Pain', m.pain); sec('History', m.history); sec('What I have tried', m.tried);
    if (m.goal) { L.push('WHAT I WANT TO DO AGAIN'); L.push('- ' + m.goal); L.push(''); }
    if (m.asks.length) { L.push('MY QUESTIONS FOR ' + SHORT.toUpperCase()); m.asks.forEach(function (q, i) { L.push((i + 1) + '. ' + q); }); L.push(''); }
    L.push('Bring: imaging reports or discs, medicine list with doses, insurance card.', 'Reported by the patient. Not a medical record.');
    return L.join('\n');
  };

  var update = function () { conditionals(); marks(); cap(); progress(); render(); };
  form.addEventListener('change', update);
  form.addEventListener('input', render);
  if (nameEl) nameEl.addEventListener('input', render);

  if ('IntersectionObserver' in window && box) {
    new IntersectionObserver(function (es) { inView = es[0].isIntersecting; if (floatBtn) floatBtn.hidden = !(any && !inView); }, { threshold: 0.05 }).observe(box);
  }

  var timer;
  var say = function (t) { statusEl.textContent = t; clearTimeout(timer); timer = setTimeout(function () { statusEl.textContent = ''; }, 3500); };
  document.getElementById('print-sum').addEventListener('click', function () { window.print(); });
  var copyBtn = document.getElementById('copy-sum');
  var okMsg = 'Copied. You can paste it into a message or a note.';
  copyBtn.addEventListener('click', function () {
    var t = asText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () { say(okMsg); }, function () { say('Could not copy. Use Print instead.'); });
    } else {
      var ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', ''); document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); say(okMsg); } catch (e) { say('Could not copy. Use Print instead.'); }
      document.body.removeChild(ta);
    }
  });
  var shareBtn = document.getElementById('share-sum');
  if (navigator.share) {
    shareBtn.hidden = false;
    shareBtn.addEventListener('click', function () { navigator.share({ title: 'Pre-visit summary for ' + DOC, text: asText() }).catch(function () {}); });
  } else {
    copyBtn.classList.remove('ghost'); copyBtn.classList.add('navy');
  }
  document.getElementById('reset-form').addEventListener('click', function () {
    form.reset(); if (nameEl) nameEl.value = '';
    update(); say('Cleared.'); window.scrollTo({ top: 0, behavior: 'auto' });
  });
  update();
})();
