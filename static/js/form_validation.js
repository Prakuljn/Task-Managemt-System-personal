(function () {
  function setError(input, message) {
    const field = input.closest(".form-field");
    const err = field ? field.querySelector(".field-error") : null;
    if (err) err.textContent = message || "";
    input.setAttribute("aria-invalid", message ? "true" : "false");
  }

  function clearErrors(form) {
    form
      .querySelectorAll(".field-error")
      .forEach((el) => (el.textContent = ""));
    form
      .querySelectorAll('[aria-invalid="true"]')
      .forEach((el) => el.setAttribute("aria-invalid", "false"));
  }

  function validateMatch(a, b, message) {
    if (!a || !b) return true;
    if (a.value !== b.value) {
      setError(b, message);
      return false;
    }
    return true;
  }

  function attachValidation(form) {
    form.addEventListener("submit", (e) => {
      clearErrors(form);
      let ok = form.checkValidity();

      // Custom rules
      const email = form.querySelector('input[type="email"]');
      if (
        email &&
        email.value &&
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)
      ) {
        setError(email, "Enter a valid email address");
        ok = false;
      }

      const pwd = form.querySelector("#password");
      const confirm = form.querySelector("#confirm");
      if (pwd && confirm) {
        ok = validateMatch(pwd, confirm, "Passwords do not match") && ok;
      }

      const progress = form.querySelector("#progress");
      if (progress) {
        const v = Number(progress.value);
        if (Number.isNaN(v) || v < 0 || v > 100) {
          setError(progress, "Progress must be between 0 and 100");
          ok = false;
        }
      }

      if (!ok) {
        e.preventDefault();
        // set first invalid focus
        const firstInvalid = form.querySelector(
          ':invalid, [aria-invalid="true"]',
        );
        if (firstInvalid) firstInvalid.focus();
      }
    });

    // Live clear
    form.querySelectorAll("input,select,textarea").forEach((el) => {
      el.addEventListener("input", () => setError(el, ""));
      el.addEventListener("change", () => setError(el, ""));
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form[novalidate]").forEach(attachValidation);
  });
})();
