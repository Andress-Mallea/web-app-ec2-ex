from sqlalchemy import select

from ..models import Guest


class GuestRepository:
    def __init__(self, session):
        self.session = session

    def list_all(self):
        return list(self.session.scalars(select(Guest).order_by(Guest.full_name)))

    def get(self, guest_id):
        return self.session.get(Guest, guest_id)

    def get_by_email(self, email):
        return self.session.scalar(select(Guest).where(Guest.email == email))

    def add(self, guest):
        self.session.add(guest)

    def delete(self, guest):
        self.session.delete(guest)

    def commit(self):
        self.session.commit()