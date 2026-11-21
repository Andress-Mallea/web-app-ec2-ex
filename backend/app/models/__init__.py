from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .room import Room  
from .guest import Guest  
from .reservation import Reservation 

__all__ = ["db", "Room", "Guest", "Reservation"]
