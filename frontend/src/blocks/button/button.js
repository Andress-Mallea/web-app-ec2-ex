// frontend/src/blocks/button/button.js
import { el } from "../../utils.js";

export function createActionButton({ label, action, id, modifier, data = {} }) {
  const classes = ["button", "button--small"];
  if (modifier) classes.push(`button--${modifier}`);
  classes.push("table__action");

  const button = el("button", classes.join(" "), label);
  button.type = "button";
  button.dataset.action = action;
  button.dataset.id = id;
  for (const [key, value] of Object.entries(data)) button.dataset[key] = value;
  return button;
}