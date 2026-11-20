from . import db


class Guest(db.Model):
    __tablename__ = "guests"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    document = db.Column(db.String(30), nullable=False)

    reservations = db.relationship("Reservation", back_populates="guest")
