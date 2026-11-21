// frontend/src/blocks/badge/badge.js
import { el } from "../../utils.js";

export function createBadge(status, labels) {
  const modifier = String(status).replace(/_/g, "-");
  return el("span", `badge badge--${modifier}`, labels[status] ?? status);
}