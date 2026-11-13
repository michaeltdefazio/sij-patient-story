/* Share buttons: uses the phone's share sheet when there is one, otherwise copies the link. */
(function () {
  'use strict';
  Array.prototype.forEach.call(document.querySelectorAll('[data-share]'), function (b) {
    var note = b.parentNode.querySelector('.toast');
    var say = function (m) { if (!note) return; note.textContent = m; setTimeout(function () { note.textContent = ''; }, 4000); };
    b.addEventListener('click', function () {
      var rel = b.getAttribute('data-url');
      var url = rel ? new URL(rel, location.href).href : location.href.split('#')[0];
      var data = { title: b.getAttribute('data-title') || document.title, text: b.getAttribute('data-text') || '', url: url };
      if (navigator.share) { navigator.share(data).catch(function () {}); return; }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () { say('Link copied. Paste it in a text or email.'); }, function () { say(url); });
      } else { say(url); }
    });
  });
})();
