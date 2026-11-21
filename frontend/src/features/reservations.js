// frontend/src/features/reservations.js
import * as api from "../api.js";
import { $, formatMoney } from "../utils.js";
import { showMessage, showError } from "../blocks/alert/alert.js";
import { createBadge } from "../blocks/badge/badge.js";
import { createActionButton } from "../blocks/button/button.js";
import { createCell, createEmptyRow } from "../blocks/table/table.js";

const STATUS_LABELS = {
  confirmed: "Confirmada", checked_in: "Hospedado", checked_out: "Finalizada", cancelled: "Cancelada",
};

const RESERVATION_ACTIONS = {
  "check-in": api.checkInReservation,
  "check-out": api.checkOutReservation,
  "cancel": api.cancelReservation,
};

export async function loadReservations() {
  try {
    const reservations = await api.listReservations($("reservation-filter").value);
    const body = $("reservations-body");

    if (reservations.length === 0) {
      body.replaceChildren(createEmptyRow(10, "No hay reservas"));
      return;
    }

    body.replaceChildren(...reservations.map((r) => {
      const tr = document.createElement("tr");
      const actions = document.createDocumentFragment();
      actions.append(
        createActionButton({ label: "Check-in", action: "check-in", id: r.id, modifier: "success" }),
        createActionButton({ label: "Check-out", action: "check-out", id: r.id }),
        createActionButton({ label: "Cancelar", action: "cancel", id: r.id, modifier: "danger" }),
      );
      tr.append(
        createCell(r.id),
        createCell(r.room_number),
        createCell(r.guest_name),
        createCell(r.check_in),
        createCell(r.check_out),
        createCell(r.nights),
        createCell(r.guests_count),
        createCell(formatMoney(r.total_price)), // total tal cual lo calcula la API (descuento / penalidad)
        createCell(createBadge(r.status, STATUS_LABELS)),
        createCell(actions),
      );
      return tr;
    }));
  } catch (error) {
    showError(error);
  }
}

export function initReservations() {
  $("reservation-filter").addEventListener("change", loadReservations);

  $("reservation-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form));
    data.room_id = Number(data.room_id);
    data.guest_id = Number(data.guest_id);
    data.guests_count = Number(data.guests_count);

    try {
      const reservation = await api.createReservation(data);
      form.reset();
      showMessage(`Reserva #${reservation.id} creada · total Bs ${formatMoney(reservation.total_price)}`);
      loadReservations();
    } catch (error) {
      showError(error); // aquí aparece el 422 de las reglas de negocio
    }
  });

  $("reservations-body").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const run = RESERVATION_ACTIONS[button.dataset.action];
    if (!run) return;
    const id = Number(button.dataset.id);

    try {
      const reservation = await run(id);
      let text = `Reserva #${id}: ${STATUS_LABELS[reservation.status] ?? reservation.status}`;
      if (reservation.total_price !== undefined && reservation.total_price !== null) {
        text += ` · total Bs ${formatMoney(reservation.total_price)}`;
      }
      showMessage(text);
      loadReservations();
    } catch (error) {
      showError(error);
    }
  });

  loadReservations();
}