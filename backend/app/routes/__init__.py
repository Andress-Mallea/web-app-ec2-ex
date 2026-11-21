from .guest_routes import guest_bp
from .reservation_routes import reservation_bp
from .room_routes import room_bp

__all__ = ["room_bp", "guest_bp", "reservation_bp"]