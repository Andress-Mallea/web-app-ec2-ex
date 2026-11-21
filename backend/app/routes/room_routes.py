from flask import Blueprint, current_app, jsonify, request

from ..errors import ValidationError
from ..services.dto import RoomCreateInput, RoomUpdateInput
from ..views.room_view import room_to_dict, rooms_to_list

room_bp = Blueprint("rooms", __name__, url_prefix="/api/rooms")


def _service():
    return current_app.extensions["room_service"]


@room_bp.get("")
def list_rooms():
    status = request.args.get("status")
    rooms = _service().list_rooms(status=status)
    return jsonify(rooms_to_list(rooms))


@room_bp.get("/<int:room_id>")
def get_room(room_id):
    room = _service().get_room(room_id)
    return jsonify(room_to_dict(room))


@room_bp.post("")
def create_room():
    data = request.get_json(silent=True) or {}

    missing = [f for f in ("number", "type", "price_per_night", "capacity") if data.get(f) in (None, "")]
    if missing:
        raise ValidationError(f"Faltan campos: {', '.join(missing)}")

    try:
        price = float(data["price_per_night"])
        capacity = int(data["capacity"])
    except (TypeError, ValueError):
        raise ValidationError("price_per_night y capacity deben ser números") from None

    dto = RoomCreateInput(
        number=str(data["number"]),
        type=data["type"],
        price_per_night=price,
        capacity=capacity,
        status=data.get("status", "available"),
    )
    room = _service().create_room(dto)
    return jsonify(room_to_dict(room)), 201


@room_bp.put("/<int:room_id>")
def update_room(room_id):
    data = request.get_json(silent=True) or {}

    try:
        price = float(data["price_per_night"]) if "price_per_night" in data else None
        capacity = int(data["capacity"]) if "capacity" in data else None
    except (TypeError, ValueError):
        raise ValidationError("price_per_night y capacity deben ser números") from None

    dto = RoomUpdateInput(
        type=data.get("type"),
        status=data.get("status"),
        price_per_night=price,
        capacity=capacity,
    )
    room = _service().update_room(room_id, dto)
    return jsonify(room_to_dict(room))


@room_bp.delete("/<int:room_id>")
def delete_room(room_id):
    _service().delete_room(room_id)
    return "", 204