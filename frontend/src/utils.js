// frontend/src/utils.js

export const $ = (name) => document.querySelector(`[data-js="${name}"]`);

export function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

export function formatMoney(value) {
  const number = Number(value);
  return Number.isFinite(number) ? String(Math.round(number * 100) / 100) : String(value ?? "");
}