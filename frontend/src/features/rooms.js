// frontend/src/features/rooms.js
import * as api from "../api.js";
import { $ } from "../utils.js";
import { showMessage, showError } from "../blocks/alert/alert.js";
import { createBadge } from "../blocks/badge/badge.js";
import { createActionButton } from "../blocks/button/button.js";
import { createCell, createEmptyRow } from "../blocks/table/table.js";

const ROOM_TYPES = { single: "Simple", double: "Doble", family: "Familiar", suite: "Suite" };
const STATUS_LABELS = { available: "Disponible", maintenance: "Mantenimiento" };

export async function loadRooms() {
  try {
    const rooms = await api.listRooms();
    const body = $("rooms-body");

    if (rooms.length === 0) {
      body.replaceChildren(createEmptyRow(6, "No hay habitaciones"));
    } else {
      body.replaceChildren(...rooms.map((r) => {
        const tr = document.createElement("tr");
        const actions = document.createDocumentFragment();
        actions.append(
          createActionButton({
            label: r.status === "maintenance" ? "Habilitar" : "Mantenimiento",
            action: "toggle-maintenance",
            id: r.id,
            modifier: "neutral",
            mix: "table__action--toggle",
            data: { status: r.status },
            }),
          createActionButton({ label: "Eliminar", action: "delete-room", id: r.id, modifier: "danger" }),
        );
        tr.append(
          createCell(r.number),
          createCell(ROOM_TYPES[r.type] || r.type),
          createCell(`Bs ${r.price_per_night}`),
          createCell(r.capacity),
          createCell(createBadge(r.status, STATUS_LABELS)),
          createCell(actions),
        );
        return tr;
      }));
    }

    // también llena el select del formulario de reservas
    $("reservation-room").replaceChildren(...rooms.map((r) =>
      new Option(`${r.number} · ${ROOM_TYPES[r.type] ?? r.type} · Bs ${r.price_per_night}`, r.id)));
  } catch (error) {
    showError(error);
  }
}

export function initRooms() {
  $("room-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = Object.fromEntries(new FormData(form));
    data.price_per_night = Number(data.price_per_night);
    data.capacity = Number(data.capacity);

    try {
      const room = await api.createRoom(data);
      form.reset();
      showMessage(`Habitación ${room.number} creada`);
      loadRooms();
    } catch (error) {
      showError(error);
    }
  });

  $("rooms-body").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-action]");
    if (!button) return;
    const id = Number(button.dataset.id);

    try {
      if (button.dataset.action === "toggle-maintenance") {
        const next = button.dataset.status === "maintenance" ? "available" : "maintenance";
        await api.updateRoom(id, { status: next });
        loadRooms();
      } else if (button.dataset.action === "delete-room") {
        if (!confirm("¿Eliminar la habitación?")) return;
        await api.deleteRoom(id);
        showMessage("Habitación eliminada");
        loadRooms();
      }
    } catch (error) {
      showError(error);
    }
  });

  loadRooms();
}