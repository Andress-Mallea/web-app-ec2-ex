from datetime import date

from ..errors import BusinessRuleError, NotFoundError
from ..models import Reservation
from .dto import ReservationCreateInput
from .pricing import calculate_cancellation_total, select_pricing_strategy

ACTIVE_STATUSES = ("confirmed", "checked_in")
MAX_ACTIVE_RESERVATIONS = 3
ALLOWED_TRANSITIONS = {
    "check-in": ("confirmed", "checked_in"),
    "check-out": ("checked_in", "checked_out"),
    "cancel": ("confirmed", "cancelled"),
}


class ReservationService:
    def __init__(self, reservation_repo, room_repo, guest_repo):
        self.reservation_repo = reservation_repo
        self.room_repo = room_repo
        self.guest_repo = guest_repo

    def list_reservations(self, status=None, guest_id=None):
        return self.reservation_repo.list_all(status=status, guest_id=guest_id)

    def get_reservation(self, reservation_id: int):
        reservation = self.reservation_repo.get(reservation_id)
        if reservation is None:
            raise NotFoundError("Reserva no encontrada")
        return reservation

    def create_reservation(self, data: ReservationCreateInput):
        room = self.room_repo.get(data.room_id)
        if room is None:
            raise NotFoundError("Habitación no encontrada")
        guest = self.guest_repo.get(data.guest_id)
        if guest is None:
            raise NotFoundError("Huésped no encontrado")

        if room.status != "available":
            raise BusinessRuleError("La habitación está en mantenimiento y no puede reservarse")

        if data.check_out <= data.check_in:
            raise BusinessRuleError("La fecha de salida debe ser posterior a la fecha de ingreso")

        if data.check_in < date.today():
            raise BusinessRuleError("La fecha de ingreso no puede ser anterior a hoy")

        if data.guests_count < 1 or data.guests_count > room.capacity:
            raise BusinessRuleError(
                f"La cantidad de huéspedes debe estar entre 1 y la capacidad de la habitación ({room.capacity})"
            )

        if self.reservation_repo.has_overlap(room.id, data.check_in, data.check_out, ACTIVE_STATUSES):
            raise BusinessRuleError("La habitación ya tiene una reserva activa en las fechas seleccionadas")

        if self.reservation_repo.count_active_by_guest(guest.id, ACTIVE_STATUSES) >= MAX_ACTIVE_RESERVATIONS:
            raise BusinessRuleError("El huésped ya alcanzó el límite de 3 reservas activas simultáneas")

      
        nights = (data.check_out - data.check_in).days
        strategy = select_pricing_strategy(nights)
        total_price = strategy.calculate(nights, room.price_per_night)

        reservation = Reservation(
            room=room,
            guest=guest,
            check_in=data.check_in,
            check_out=data.check_out,
            guests_count=data.guests_count,
            status="confirmed",
            total_price=total_price,
        )
        self.reservation_repo.add(reservation)
        self.reservation_repo.commit()
        return reservation

    def cancel_reservation(self, reservation_id: int):
        reservation = self.get_reservation(reservation_id)
        target_status = self._validate_transition(reservation, "cancel")

       
        reservation.total_price = calculate_cancellation_total(
            reservation.check_in, date.today(), reservation.room.price_per_night
        )
        reservation.status = target_status
        self.reservation_repo.commit()
        return reservation

    def check_in_reservation(self, reservation_id: int):
        reservation = self.get_reservation(reservation_id)
        target_status = self._validate_transition(reservation, "check-in")

        if date.today() < reservation.check_in:
            raise BusinessRuleError(
                f"No se puede hacer check-in antes de la fecha de ingreso ({reservation.check_in.isoformat()})"
            )

        reservation.status = target_status
        self.reservation_repo.commit()
        return reservation

    def check_out_reservation(self, reservation_id: int):
        reservation = self.get_reservation(reservation_id)
        target_status = self._validate_transition(reservation, "check-out")
        reservation.status = target_status
        self.reservation_repo.commit()
        return reservation

    @staticmethod
    def _validate_transition(reservation: Reservation, action: str) -> str:
       
        expected_source, target = ALLOWED_TRANSITIONS[action]
        if reservation.status != expected_source:
            raise BusinessRuleError(
                f"No se puede realizar '{action}' en una reserva con estado '{reservation.status}'"
            )
        return target