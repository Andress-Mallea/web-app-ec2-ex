from . import db


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)          
    price_per_night = db.Column(db.Float, nullable=False)    
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="available")  

    reservations = db.relationship("Reservation", back_populates="room")