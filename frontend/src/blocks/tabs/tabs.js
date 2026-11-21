// frontend/src/blocks/tabs/tabs.js
export function initTabs() {
  const tabButtons = document.querySelectorAll("[data-tab]");
  const panels = document.querySelectorAll("[data-panel]");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.toggle("tabs__item--active", b === button));
      panels.forEach((panel) => { panel.hidden = panel.dataset.panel !== button.dataset.tab; });
    });
  });
}