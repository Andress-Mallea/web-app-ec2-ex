// frontend/src/blocks/table/table.js
import { el } from "../../utils.js";

export function createCell(content, modifier) {
  const td = el("td", modifier ? `table__cell table__cell--${modifier}` : "table__cell");
  if (content instanceof Node) td.append(content);
  else td.textContent = content ?? "";
  return td;
}

export function createEmptyRow(colspan, text) {
  const tr = document.createElement("tr");
  const td = createCell(text, "empty");
  td.colSpan = colspan;
  tr.append(td);
  return tr;
}