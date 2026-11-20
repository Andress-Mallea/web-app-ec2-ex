def guest_to_dict(guest):
    return {
        "id": guest.id,
        "full_name": guest.full_name,
        "email": guest.email,
        "document": guest.document,
    }


def guests_to_list(guests):
    return [guest_to_dict(guest) for guest in guests]
