from flask import Blueprint, current_app, jsonify, request

from ..errors import ValidationError
from ..services.dto import GuestCreateInput
from ..views.guest_view import guest_to_dict, guests_to_list

guest_bp = Blueprint("guests", __name__, url_prefix="/api/guests")


def _service():
    return current_app.extensions["guest_service"]


@guest_bp.get("")
def list_guests():
    guests = _service().list_guests()
    return jsonify(guests_to_list(guests))


@guest_bp.get("/<int:guest_id>")
def get_guest(guest_id):
    guest = _service().get_guest(guest_id)
    return jsonify(guest_to_dict(guest))


@guest_bp.post("")
def create_guest():
    data = request.get_json(silent=True) or {}

    missing = [f for f in ("full_name", "email", "document") if not str(data.get(f, "")).strip()]
    if missing:
        raise ValidationError(f"Faltan campos: {', '.join(missing)}")

    dto = GuestCreateInput(
        full_name=str(data["full_name"]),
        email=str(data["email"]),
        document=str(data["document"]),
    )
    guest = _service().create_guest(dto)
    return jsonify(guest_to_dict(guest)), 201


@guest_bp.delete("/<int:guest_id>")
def delete_guest(guest_id):
    _service().delete_guest(guest_id)
    return "", 204