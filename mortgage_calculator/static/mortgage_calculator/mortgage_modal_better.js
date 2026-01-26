(function () {
  const overlay = document.querySelector("[data-mc-overlay]");
  const modal = overlay?.querySelector(".mc-modal");
  const closeBtn = overlay?.querySelector("[data-mc-close]");
  const calcBtn = overlay?.querySelector("[data-mc-calc]");
  const endpointHolder = overlay?.querySelector("[data-mc-endpoint]");

  if (!overlay || !modal || !closeBtn || !calcBtn || !endpointHolder) return;

  const principalInput = overlay.querySelector(".mc-principal");
  const rateInput = overlay.querySelector(".mc-rate");
  const yearsInput = overlay.querySelector(".mc-years");
  const paymentEl = overlay.querySelector(".mc-payment");
  const errorEl = overlay.querySelector(".mc-error");

  const endpoint = endpointHolder.dataset.mcEndpoint || endpointHolder.getAttribute("data-mc-endpoint");

  function openModal({ principal } = {}) {
    errorEl.textContent = "";
    if (principal) principalInput.value = principal;

    overlay.classList.add("is-open");
    overlay.setAttribute("aria-hidden", "false");

    // small focus help
    setTimeout(() => principalInput.focus(), 50);
  }

  function closeModal() {
    overlay.classList.remove("is-open");
    overlay.setAttribute("aria-hidden", "true");
  }

  // Open from ANY trigger button on page
  document.addEventListener("click", (e) => {
    const trigger = e.target.closest(".mc-trigger");
    if (!trigger) return;

    const principal = trigger.getAttribute("data-mc-principal");
    openModal({ principal });
  });

  closeBtn.addEventListener("click", closeModal);

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (overlay.classList.contains("is-open") && e.key === "Escape") closeModal();
  });

  // Calculate
  calcBtn.addEventListener("click", async () => {
    errorEl.textContent = "";

    const fd = new FormData();
    fd.append("principal", principalInput.value);
    fd.append("rate", rateInput.value);
    fd.append("years", yearsInput.value);

    const resp = await fetch(endpoint, {
      method: "POST",
      body: fd,
      headers: { "X-CSRFToken": window.MC_CSRF_TOKEN || "" }
    });

    const data = await resp.json();
    if (!resp.ok) {
      errorEl.textContent = data.error || "Error calculating mortgage";
      return;
    }
    paymentEl.textContent = data.monthly_payment;
  });
})();
mortgage_modal_better