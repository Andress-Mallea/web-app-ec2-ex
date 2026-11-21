from ..errors import ConflictError, NotFoundError, ValidationError
from ..models import Room
from .dto import RoomCreateInput, RoomUpdateInput

ROOM_TYPES = ("single", "double", "family", "suite")
ROOM_STATUSES = ("available", "maintenance")


class RoomService:
    def __init__(self, room_repo):
        self.room_repo = room_repo

    def list_rooms(self, status=None):
        return self.room_repo.list_all(status=status)

    def get_room(self, room_id: int):
        room = self.room_repo.get(room_id)
        if room is None:
            raise NotFoundError("Habitación no encontrada")
        return room

    def create_room(self, data: RoomCreateInput):
        if data.type not in ROOM_TYPES:
            raise ValidationError(f"Tipo inválido. Usa: {', '.join(ROOM_TYPES)}")
        if data.status not in ROOM_STATUSES:
            raise ValidationError(f"Estado inválido. Usa: {', '.join(ROOM_STATUSES)}")

        number = data.number.strip()
        if self.room_repo.get_by_number(number):
            raise ConflictError("Ya existe una habitación con ese número")

        room = Room(
            number=number,
            type=data.type,
            price_per_night=data.price_per_night,
            capacity=data.capacity,
            status=data.status,
        )
        self.room_repo.add(room)
        self.room_repo.commit()
        return room

    def update_room(self, room_id: int, data: RoomUpdateInput):
        room = self.get_room(room_id)

        if data.type is not None:
            if data.type not in ROOM_TYPES:
                raise ValidationError(f"Tipo inválido. Usa: {', '.join(ROOM_TYPES)}")
            room.type = data.type
        if data.status is not None:
            if data.status not in ROOM_STATUSES:
                raise ValidationError(f"Estado inválido. Usa: {', '.join(ROOM_STATUSES)}")
            room.status = data.status
        if data.price_per_night is not None:
            room.price_per_night = data.price_per_night
        if data.capacity is not None:
            room.capacity = data.capacity

        self.room_repo.commit()
        return room

    def delete_room(self, room_id: int):
        room = self.get_room(room_id)
        if room.reservations:
            raise ConflictError("La habitación tiene reservas registradas")
        self.room_repo.delete(room)
        self.room_repo.commit()