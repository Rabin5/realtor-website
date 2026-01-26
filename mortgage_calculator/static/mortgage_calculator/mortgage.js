(function () {
  const openBtn = document.querySelector(".mc-open-btn");
  const backdrop = document.querySelector(".mc-modal-backdrop");
  const closeBtn = document.querySelector(".mc-close-btn");

  if (!openBtn || !backdrop || !closeBtn) return;

  function openModal() {
    backdrop.classList.add("is-open");
    backdrop.setAttribute("aria-hidden", "false");
  }

  function closeModal() {
    backdrop.classList.remove("is-open");
    backdrop.setAttribute("aria-hidden", "true");
  }

  openBtn.addEventListener("click", openModal);
  closeBtn.addEventListener("click", closeModal);

  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) closeModal(); // click outside modal
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
})();
