from sqlalchemy import select

from ..models import Room


class RoomRepository:
    def __init__(self, session):
        self.session = session

    def list_all(self, status=None):
        query = select(Room)
        if status:
            query = query.where(Room.status == status)
        return list(self.session.scalars(query.order_by(Room.number)))

    def get(self, room_id):
        return self.session.get(Room, room_id)

    def get_by_number(self, number):
        return self.session.scalar(select(Room).where(Room.number == number))

    def add(self, room):
        self.session.add(room)

    def delete(self, room):
        self.session.delete(room)

    def commit(self):
        self.session.commit()