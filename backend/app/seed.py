from datetime import date, timedelta

from .models import Guest, Reservation, Room, db


def seed():
    """Carga datos de ejemplo solo si la base está vacía."""
    if Room.query.first():
        return

    rooms = [
        Room(number="101", type="single", price_per_night=180, capacity=1),
        Room(number="102", type="double", price_per_night=280, capacity=2),
        Room(number="201", type="double", price_per_night=300, capacity=2),
        Room(number="202", type="family", price_per_night=420, capacity=4),
        Room(number="203", type="double", price_per_night=300, capacity=2, status="maintenance"),
        Room(number="301", type="suite", price_per_night=650, capacity=3),
    ]
    guests = [
        Guest(full_name="Ana Rojas", email="ana.rojas@example.com", document="7845123"),
        Guest(full_name="Carlos Pérez", email="carlos.perez@example.com", document="6512398"),
        Guest(full_name="Lucía Vargas", email="lucia.vargas@example.com", document="9021457"),
    ]
    db.session.add_all(rooms + guests)
    db.session.flush()

    today = date.today()
    reservations = [
        (rooms[1], guests[0], today + timedelta(days=3), today + timedelta(days=6), 2),
        (rooms[3], guests[1], today + timedelta(days=10), today + timedelta(days=17), 4),
        (rooms[5], guests[2], today + timedelta(days=1), today + timedelta(days=2), 2),
    ]
    for room, guest, check_in, check_out, count in reservations:
        db.session.add(Reservation(
            room=room, guest=guest, check_in=check_in, check_out=check_out, guests_count=count,
            status="confirmed", total_price=(check_out - check_in).days * room.price_per_night,
        ))
    db.session.commit()
