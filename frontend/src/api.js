// frontend/src/api.js

const BASE_URL = `${location.protocol}//${location.hostname}:8000/api`;

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(BASE_URL + path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(res.status, data.error ?? res.statusText);
  }

  if (res.status === 204) return null;
  return res.json().catch(() => null);
}

// ---------- habitaciones ----------
export const listRooms = () => request("/rooms");
export const createRoom = (data) => request("/rooms", { method: "POST", body: data });
export const updateRoom = (id, data) => request(`/rooms/${id}`, { method: "PUT", body: data });
export const deleteRoom = (id) => request(`/rooms/${id}`, { method: "DELETE" });

// ---------- huéspedes ----------
export const listGuests = () => request("/guests");
export const createGuest = (data) => request("/guests", { method: "POST", body: data });
export const deleteGuest = (id) => request(`/guests/${id}`, { method: "DELETE" });

// ---------- reservas ----------
export const listReservations = (status = "") =>
  request("/reservations" + (status ? `?status=${encodeURIComponent(status)}` : ""));
export const createReservation = (data) => request("/reservations", { method: "POST", body: data });
export const checkInReservation = (id) => request(`/reservations/${id}/check-in`, { method: "PATCH" });
export const checkOutReservation = (id) => request(`/reservations/${id}/check-out`, { method: "PATCH" });
export const cancelReservation = (id) => request(`/reservations/${id}/cancel`, { method: "PATCH" });