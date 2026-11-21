// frontend/src/features/guests.js
import * as api from "../api.js";
import { $ } from "../utils.js";
import { showMessage, showError } from "../blocks/alert/alert.js";
import { createActionButton } from "../blocks/button/button.js";
import { createCell, createEmptyRow } from "../blocks/table/table.js";

export async function loadGuests() {
  try {
    const guests = await api.listGuests();
    const body = $("guests-body");

    if (guests.length === 0) {
      body.replaceChildren(createEmptyRow(4, "No hay huéspedes"));
    } else {
      body.replaceChildren(...guests.map((g) => {
        const tr = document.createElement("tr");
        tr.append(
          createCell(g.full_name),
          createCell(g.email),
          createCell(g.document),
          createCell(createActionButton({ label: "Eliminar", action: "delete-guest", id: g.id, modifier: "danger" })),
        );
        return tr;
      }));
    }

    $("reservation-guest").replaceChildren(...guests.map((g) => new Option(g.full_name, g.id)));
  } catch (error) {
    showError(error);
  }
}

export function initGuests() {
  $("guest-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form));

    try {
      const guest = await api.createGuest(data);
      form.reset();
      showMessage(`Huésped ${guest.full_name} registrado`);
      loadGuests();
    } catch (error) {
      showError(error);
    }
  });

  $("guests-body").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action='delete-guest']");
    if (!button) return;
    if (!confirm("¿Eliminar el huésped?")) return;

    try {
      await api.deleteGuest(Number(button.dataset.id));
      showMessage("Huésped eliminado");
      loadGuests();
    } catch (error) {
      showError(error);
    }
  });

  loadGuests();
}