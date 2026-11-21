from datetime import date

from flask import Blueprint, current_app, jsonify, request

from ..errors import ValidationError
from ..services.dto import ReservationCreateInput
from ..views.reservation_view import reservation_to_dict, reservations_to_list

reservation_bp = Blueprint("reservations", __name__, url_prefix="/api/reservations")


def _service():
    return current_app.extensions["reservation_service"]


@reservation_bp.get("")
def list_reservations():
    status = request.args.get("status")
    guest_id = request.args.get("guest_id", type=int)
    reservations = _service().list_reservations(status=status, guest_id=guest_id)
    return jsonify(reservations_to_list(reservations))


@reservation_bp.get("/<int:reservation_id>")
def get_reservation(reservation_id):
    reservation = _service().get_reservation(reservation_id)
    return jsonify(reservation_to_dict(reservation))


@reservation_bp.post("")
def create_reservation():
    data = request.get_json(silent=True) or {}

    missing = [
        f
        for f in ("room_id", "guest_id", "check_in", "check_out", "guests_count")
        if data.get(f) in (None, "")
    ]
    if missing:
        raise ValidationError(f"Faltan campos: {', '.join(missing)}")

    try:
        room_id = int(data["room_id"])
        guest_id = int(data["guest_id"])
        check_in = date.fromisoformat(data["check_in"])
        check_out = date.fromisoformat(data["check_out"])
        guests_count = int(data["guests_count"])
    except (TypeError, ValueError):
        raise ValidationError("Fechas en formato AAAA-MM-DD y room_id, guest_id, guests_count numéricos") from None

    dto = ReservationCreateInput(
        room_id=room_id,
        guest_id=guest_id,
        check_in=check_in,
        check_out=check_out,
        guests_count=guests_count,
    )
    reservation = _service().create_reservation(dto)
    return jsonify(reservation_to_dict(reservation)), 201


@reservation_bp.patch("/<int:reservation_id>/cancel")
def cancel_reservation(reservation_id):
    reservation = _service().cancel_reservation(reservation_id)
    return jsonify(reservation_to_dict(reservation))


@reservation_bp.patch("/<int:reservation_id>/check-in")
def check_in_reservation(reservation_id):
    reservation = _service().check_in_reservation(reservation_id)
    return jsonify(reservation_to_dict(reservation))


@reservation_bp.patch("/<int:reservation_id>/check-out")
def check_out_reservation(reservation_id):
    reservation = _service().check_out_reservation(reservation_id)
    return jsonify(reservation_to_dict(reservation))