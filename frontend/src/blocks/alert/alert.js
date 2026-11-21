// frontend/src/blocks/alert/alert.js
import { $ } from "../../utils.js";
import { ApiError } from "../../api.js";

export function showMessage(text, isError = false) {
  const msg = $("message");
  msg.textContent = text;
  msg.className = `alert page__alert alert--${isError ? "error" : "success"}`;
  msg.hidden = false;
  clearTimeout(showMessage.timer);
  showMessage.timer = setTimeout(() => { msg.hidden = true; }, 4000);
}

export function showError(error) {
  if (error instanceof ApiError) {
    showMessage(error.message, true);
  } else {
    showMessage("No se pudo conectar con el servidor", true);
  }
}