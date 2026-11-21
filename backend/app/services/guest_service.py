from ..errors import ConflictError, NotFoundError, ValidationError
from ..models import Guest
from .dto import GuestCreateInput


class GuestService:
    def __init__(self, guest_repo):
        self.guest_repo = guest_repo

    def list_guests(self):
        return self.guest_repo.list_all()

    def get_guest(self, guest_id: int):
        guest = self.guest_repo.get(guest_id)
        if guest is None:
            raise NotFoundError("Huésped no encontrado")
        return guest

    def create_guest(self, data: GuestCreateInput):
        email = data.email.strip().lower()
        if "@" not in email:
            raise ValidationError("Email inválido")
        if self.guest_repo.get_by_email(email):
            raise ConflictError("Ya existe un huésped con ese email")

        guest = Guest(
            full_name=data.full_name.strip(),
            email=email,
            document=data.document.strip(),
        )
        self.guest_repo.add(guest)
        self.guest_repo.commit()
        return guest

    def delete_guest(self, guest_id: int):
        guest = self.get_guest(guest_id)
        if guest.reservations:
            raise ConflictError("El huésped tiene reservas registradas")
        self.guest_repo.delete(guest)
        self.guest_repo.commit()