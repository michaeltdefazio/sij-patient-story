/* Questions to bring: tap to build a list. Nothing is saved or sent anywhere. */
(function () {
  'use strict';
  var tool = document.getElementById('visit-tool');
  if (!tool) return;
  var DOC = tool.getAttribute('data-doc') || 'my doctor';
  var SHORT = tool.getAttribute('data-short') || 'my doctor';
  var CONTACT = tool.getAttribute('data-contact') || '';
  var bringBox = Array.prototype.slice.call(tool.querySelectorAll('input[data-kind="bring"]'));
  var askBox = Array.prototype.slice.call(tool.querySelectorAll('input[data-kind="ask"]'));
  var custom = [];
  var out = document.getElementById('mylist-body');
  var count = document.getElementById('list-count');
  var floatBtn = document.getElementById('float-list');
  var listBox = document.getElementById('list');
  var actions = document.getElementById('list-actions');
  var inView = false, total = 0;
  var txt = function (s) { return String(s).replace(/\s+/g, ' ').trim(); };
  var plain = function () {
    var bring = bringBox.filter(function (c) { return c.checked; }).map(function (c) {
      var d = c.getAttribute('data-detail');
      return txt(c.getAttribute('data-label')) + (d ? ' (' + txt(d) + ')' : '');
    });
    var ask = askBox.filter(function (c) { return c.checked; }).map(function (c) { return txt(c.getAttribute('data-label')); }).concat(custom);
    return { bring: bring, ask: ask };
  };
  var syncFloat = function () { if (floatBtn) floatBtn.hidden = !(total && !inView); };
  var render = function () {
    var d = plain(), n = d.bring.length + d.ask.length;
    total = n;
    if (actions) actions.hidden = !n;
    count.textContent = n ? '(' + n + ')' : '';
    if (floatBtn) { floatBtn.textContent = 'My list · ' + n; syncFloat(); }
    out.textContent = '';
    if (!n) { var e = document.createElement('p'); e.className = 'empty'; e.textContent = 'Tap the items above to build your list.'; out.appendChild(e); return; }
    var block = function (title, items, removable) {
      if (!items.length) return;
      var h = document.createElement('h3'); h.textContent = title; out.appendChild(h);
      var ul = document.createElement('ul');
      items.forEach(function (t, i) {
        var li = document.createElement('li'); li.appendChild(document.createTextNode(t));
        if (removable && removable(i)) {
          var b = document.createElement('button'); b.type = 'button'; b.className = 'rm'; b.textContent = 'Remove';
          b.setAttribute('aria-label', 'Remove: ' + t);
          b.addEventListener('click', function () { custom.splice(removable(i) - 1, 1); render(); });
          li.appendChild(b);
        }
        ul.appendChild(li);
      });
      out.appendChild(ul);
    };
    block('Bring', d.bring);
    var selected = askBox.filter(function (c) { return c.checked; }).length;
    block('Ask ' + SHORT, d.ask, function (i) { return i >= selected ? i - selected + 1 : 0; });
  };
  if ('IntersectionObserver' in window && listBox) {
    new IntersectionObserver(function (es) { inView = es[0].isIntersecting; syncFloat(); }, { threshold: 0.05 }).observe(listBox);
  }
  var mark = function () {
    Array.prototype.forEach.call(tool.querySelectorAll('label.pick'), function (l) {
      var i = l.querySelector('input'); l.classList.toggle('on', !!(i && i.checked));
    });
  };
  tool.addEventListener('change', function () { mark(); render(); });
  var input = document.getElementById('own-q');
  var addOwn = function () {
    var v = txt(input.value); if (!v) { input.focus(); return; }
    custom.push(v); input.value = ''; render(); input.focus();
  };
  document.getElementById('add-q').addEventListener('click', addOwn);
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); addOwn(); } });
  var asText = function () {
    var d = plain(), lines = ['My list for my visit with ' + DOC, CONTACT, ''];
    if (d.bring.length) { lines.push('Bring:'); d.bring.forEach(function (t) { lines.push('- ' + t); }); lines.push(''); }
    if (d.ask.length) { lines.push('Ask ' + SHORT + ':'); d.ask.forEach(function (t) { lines.push('- ' + t); }); }
    return lines.join('\n');
  };
  var status = document.getElementById('list-status');
  var timer;
  var say = function (m) { status.textContent = m; clearTimeout(timer); timer = setTimeout(function () { status.textContent = ''; }, 3500); };
  document.getElementById('print-list').addEventListener('click', function () { window.print(); });
  var copyBtn = document.getElementById('copy-list');
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
  var shareBtn = document.getElementById('share-list');
  if (navigator.share) {
    shareBtn.hidden = false;
    shareBtn.addEventListener('click', function () { navigator.share({ title: 'My list for my visit with ' + DOC, text: asText() }).catch(function () {}); });
  } else {
    copyBtn.classList.remove('ghost'); copyBtn.classList.add('navy');
  }
  render();
})();
