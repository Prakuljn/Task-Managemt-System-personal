(function () {
  const html = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const navToggle = document.getElementById("navToggle");
  const siteNav = document.getElementById("siteNav");
  const yearEl = document.getElementById("year");

  // Year in footer
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Theme management
  const stored = localStorage.getItem("tf-theme");
  const prefersDark =
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches;
  if (!stored) {
    html.setAttribute("data-theme", prefersDark ? "dark" : "light");
  } else {
    html.setAttribute("data-theme", stored);
  }
  function toggleTheme() {
    const current =
      html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", current);
    localStorage.setItem("tf-theme", current);
  }
  if (themeToggle) themeToggle.addEventListener("click", toggleTheme);

  // Mobile nav toggle
  if (navToggle && siteNav) {
    navToggle.addEventListener("click", () => {
      const expanded = navToggle.getAttribute("aria-expanded") === "true";
      navToggle.setAttribute("aria-expanded", String(!expanded));
      siteNav.setAttribute("aria-expanded", String(!expanded));
    });
  }

  // Simple confirm for destructive actions
  document.addEventListener("click", (e) => {
    const t = e.target;
    if (t && t.matches("[data-confirm]")) {
      const msg = t.getAttribute("data-confirm") || "Are you sure?";
      if (!confirm(msg)) {
        e.preventDefault();
      }
    }
  });
})();
