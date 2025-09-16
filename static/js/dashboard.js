(function () {
  function parseValues(str) {
    return (str || "")
      .split(",")
      .map((s) => Number(s.trim()))
      .filter((n) => !isNaN(n));
  }
  function drawBar(ctx, values, color) {
    const { width, height } = ctx.canvas;
    ctx.clearRect(0, 0, width, height);
    const max = Math.max(1, ...values);
    const pad = 24;
    const w = ((width - pad * 2) / values.length) * 0.7;
    const gap = ((width - pad * 2) / values.length) * 0.3;
    values.forEach((v, i) => {
      const h = (height - pad * 2) * (v / max);
      const x = pad + i * (w + gap);
      const y = height - pad - h;
      const grd = ctx.createLinearGradient(x, y, x, y + h);
      grd.addColorStop(0, color);
      grd.addColorStop(1, "rgba(99,91,255,.35)");
      ctx.fillStyle = grd;
      ctx.fillRect(x, y, w, h);
      ctx.fillStyle = "rgba(230,232,239,.35)";
      ctx.fillRect(x, height - pad, w, 2);
    });
  }
  function drawLine(ctx, values, color) {
    const { width, height } = ctx.canvas;
    ctx.clearRect(0, 0, width, height);
    const max = Math.max(1, ...values);
    const pad = 24;
    const usableW = width - pad * 2;
    const usableH = height - pad * 2;
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = color;
    ctx.beginPath();
    values.forEach((v, i) => {
      const x = pad + usableW * (i / (values.length - 1 || 1));
      const y = height - pad - usableH * (v / max);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    // Glow
    ctx.shadowColor = color;
    ctx.shadowBlur = 14;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  function initCharts() {
    document.querySelectorAll("canvas[data-chart]").forEach((cv) => {
      const ctx = cv.getContext("2d");
      const values = parseValues(cv.getAttribute("data-values"));
      const type = cv.getAttribute("data-chart");
      const color =
        getComputedStyle(document.documentElement)
          .getPropertyValue("--brand-600")
          .trim() || "#635bff";
      // Ensure canvas size matches displayed size for crisp drawing
      const rect = cv.getBoundingClientRect();
      cv.width = Math.floor(rect.width * (window.devicePixelRatio || 1));
      cv.height = Math.floor(240 * (window.devicePixelRatio || 1));
      ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
      if (type === "bar") drawBar(ctx, values, color);
      else drawLine(ctx, values, color);
    });
  }

  // Simple search filter for tables
  function initFilters() {
    const search =
      document.getElementById("searchManagers") ||
      document.getElementById("searchTasks");
    const table =
      document.getElementById("managersTable") ||
      document.getElementById("employeesTasksTable");
    const statusFilter = document.getElementById("statusFilter");
    if (search && table) {
      const rows = Array.from(table.querySelectorAll("tbody tr"));
      const run = () => {
        const q = search.value.toLowerCase();
        const status = statusFilter ? statusFilter.value : "";
        rows.forEach((r) => {
          const text = r.textContent.toLowerCase();
          const statusCell = r.children[4] ? r.children[4].textContent : "";
          const match =
            (!q || text.includes(q)) && (!status || statusCell === status);
          r.style.display = match ? "" : "none";
        });
      };
      search.addEventListener("input", run);
      if (statusFilter) statusFilter.addEventListener("change", run);
    }
  }

  window.addEventListener("resize", () => initCharts());
  document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    initFilters();
  });
})();
