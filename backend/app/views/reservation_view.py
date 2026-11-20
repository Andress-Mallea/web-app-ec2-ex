def reservation_to_dict(reservation):
    return {
        "id": reservation.id,
        "room_id": reservation.room_id,
        "room_number": reservation.room.number,
        "guest_id": reservation.guest_id,
        "guest_name": reservation.guest.full_name,
        "check_in": reservation.check_in.isoformat(),
        "check_out": reservation.check_out.isoformat(),
        "nights": (reservation.check_out - reservation.check_in).days,
        "guests_count": reservation.guests_count,
        "status": reservation.status,
        "total_price": round(reservation.total_price, 2),
        "created_at": reservation.created_at.isoformat(timespec="seconds"),
    }


def reservations_to_list(reservations):
    return [reservation_to_dict(reservation) for reservation in reservations]
