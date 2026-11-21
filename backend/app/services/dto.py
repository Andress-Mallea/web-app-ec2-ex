from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class RoomCreateInput:
    number: str
    type: str
    price_per_night: float
    capacity: int
    status: str = "available"


@dataclass(frozen=True)
class RoomUpdateInput:
    type: str | None = None
    status: str | None = None
    price_per_night: float | None = None
    capacity: int | None = None


@dataclass(frozen=True)
class GuestCreateInput:
    full_name: str
    email: str
    document: str


@dataclass(frozen=True)
class ReservationCreateInput:
    room_id: int
    guest_id: int
    check_in: date
    check_out: date
    guests_count: int