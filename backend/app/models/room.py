from . import db


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)          # single | double | family | suite
    price_per_night = db.Column(db.Float, nullable=False)    # en bolivianos
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="available")  # available | maintenance

    reservations = db.relationship("Reservation", back_populates="room")
