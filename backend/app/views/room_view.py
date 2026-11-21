def room_to_dict(room):
    return {
        "id": room.id,
        "number": room.number,
        "type": room.type,
        "price_per_night": room.price_per_night,
        "capacity": room.capacity,
        "status": room.status,
    }


def rooms_to_list(rooms):
    return [room_to_dict(room) for room in rooms]