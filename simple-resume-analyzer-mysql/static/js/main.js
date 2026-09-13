/**
 * ResumeIQ — shared frontend helpers
 * Pure vanilla JS. Easy to explain.
 */

// ---------- Toast notifications ----------
function toast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transition = 'opacity 0.3s';
    setTimeout(() => el.remove(), 300);
  }, 3200);
}

// ---------- HTML escape (prevent XSS) ----------
function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ---------- Date formatting ----------
function formatDate(iso) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

// ---------- Score color class ----------
function scoreClass(score) {
  if (score == null) return '';
  if (score >= 75) return 'success';
  if (score >= 50) return 'warning';
  return 'danger';
}

// ---------- Logout button ----------
document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.href = '/';
    });
  }

  // Show admin link if user is admin
  fetch('/api/auth/me')
    .then(r => r.json())
    .then(data => {
      if (data.user && data.user.is_admin) {
        const link = document.getElementById('admin-link');
        if (link) link.style.display = 'inline';
      }
    })
    .catch(() => {});
});
