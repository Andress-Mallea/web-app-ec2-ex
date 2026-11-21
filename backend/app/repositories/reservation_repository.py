from sqlalchemy import func, select

from ..models import Reservation


class ReservationRepository:
    def __init__(self, session):
        self.session = session

    def list_all(self, status=None, guest_id=None):
        query = select(Reservation)
        if status:
            query = query.where(Reservation.status == status)
        if guest_id:
            query = query.where(Reservation.guest_id == guest_id)
        return list(self.session.scalars(query.order_by(Reservation.check_in)))

    def get(self, reservation_id):
        return self.session.get(Reservation, reservation_id)

    def has_overlap(self, room_id, check_in, check_out, active_statuses):
        query = select(Reservation.id).where(
            Reservation.room_id == room_id,
            Reservation.status.in_(active_statuses),
            Reservation.check_in < check_out,
            Reservation.check_out > check_in,
        )
        return self.session.scalar(select(query.exists())) or False

    def count_active_by_guest(self, guest_id, active_statuses):
        query = (
            select(func.count())
            .select_from(Reservation)
            .where(
                Reservation.guest_id == guest_id,
                Reservation.status.in_(active_statuses),
            )
        )
        return self.session.scalar(query) or 0

    def add(self, reservation):
        self.session.add(reservation)

    def commit(self):
        self.session.commit()