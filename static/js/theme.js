// ── THEME — runs BEFORE paint to avoid flash ──────────────────────────────
(function () {
  var saved = localStorage.getItem('lms_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
})();

// ── PUBLIC API ─────────────────────────────────────────────────────────────
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('lms_theme', theme);

  // sync every toggle on the page
  document.querySelectorAll('.theme-checkbox').forEach(function (cb) {
    cb.checked = (theme === 'dark');
  });

  // update emoji icon
  document.querySelectorAll('.theme-icon').forEach(function (el) {
    el.textContent = theme === 'dark' ? '🌙' : '☀️';
  });
}

function toggleTheme() {
  var current = document.documentElement.getAttribute('data-theme') || 'light';
  applyTheme(current === 'light' ? 'dark' : 'light');
}

// ── INIT after DOM ready ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  var saved = localStorage.getItem('lms_theme') || 'light';
  applyTheme(saved);   // syncs checkboxes + icons

  // Mobile sidebar
  var ham     = document.querySelector('.hamburger');
  var overlay = document.querySelector('.sidebar-overlay');
  if (ham)     ham.addEventListener('click', openSidebar);
  if (overlay) overlay.addEventListener('click', closeSidebar);

  // Auto-dismiss alerts after 4 s
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (a) {
      a.style.transition = 'opacity 0.5s, transform 0.5s';
      a.style.opacity    = '0';
      a.style.transform  = 'translateY(-4px)';
      setTimeout(function () { a.remove(); }, 500);
    });
  }, 4000);
});

// ── MOBILE SIDEBAR ─────────────────────────────────────────────────────────
function openSidebar() {
  var s = document.querySelector('.sidebar');
  var o = document.querySelector('.sidebar-overlay');
  if (s) s.classList.add('open');
  if (o) o.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeSidebar() {
  var s = document.querySelector('.sidebar');
  var o = document.querySelector('.sidebar-overlay');
  if (s) s.classList.remove('open');
  if (o) o.classList.remove('open');
  document.body.style.overflow = '';
}
