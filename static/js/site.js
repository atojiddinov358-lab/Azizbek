(function () {
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // theme toggle (remembered in this browser only)
  var tb = document.getElementById('themeBtn');
  if (tb) tb.addEventListener('click', function () {
    var next = root.dataset.theme === 'light' ? 'dark' : 'light';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  // mobile menu
  var mb = document.getElementById('menuBtn'), links = document.getElementById('links');
  if (mb) mb.addEventListener('click', function () {
    var open = links.classList.toggle('open');
    mb.setAttribute('aria-expanded', open);
  });

  // reveal on scroll
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    items.forEach(function (el) { io.observe(el); });
  } else items.forEach(function (el) { el.classList.add('in'); });

  // reading / scroll progress
  var bar = document.getElementById('progress');
  if (bar) addEventListener('scroll', function () {
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (h > 0 ? scrollY / h * 100 : 0) + '%';
  }, { passive: true });

  // light star field (no library)
  var c = document.getElementById('stars');
  if (c && !reduce) {
    var x = c.getContext('2d'), stars = [], raf;
    function size() {
      c.width = c.offsetWidth; c.height = c.offsetHeight;
      stars = Array.from({ length: Math.min(120, c.width / 10) }, function () {
        return { x: Math.random() * c.width, y: Math.random() * c.height * 0.8, r: Math.random() * 1.3 + 0.2, p: Math.random() * 6 };
      });
    }
    function draw(t) {
      x.clearRect(0, 0, c.width, c.height);
      stars.forEach(function (s) {
        x.globalAlpha = 0.35 + 0.35 * Math.sin(t / 1200 + s.p);
        x.fillStyle = '#E9EAF0'; x.beginPath(); x.arc(s.x, s.y, s.r, 0, 6.3); x.fill();
      });
      raf = requestAnimationFrame(draw);
    }
    size(); addEventListener('resize', size); raf = requestAnimationFrame(draw);
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) cancelAnimationFrame(raf); else raf = requestAnimationFrame(draw);
    });
  }
})();
