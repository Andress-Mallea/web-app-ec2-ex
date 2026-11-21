from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .errors import AppError
from .models import db
from .repositories import GuestRepository, ReservationRepository, RoomRepository
from .routes import guest_bp, reservation_bp, room_bp
from .seed import seed
from .services import GuestService, ReservationService, RoomService


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    CORS(app)
    db.init_app(app)

    room_repo = RoomRepository(db.session)
    guest_repo = GuestRepository(db.session)
    reservation_repo = ReservationRepository(db.session)

    app.extensions["room_service"] = RoomService(room_repo)
    app.extensions["guest_service"] = GuestService(guest_repo)
    app.extensions["reservation_service"] = ReservationService(reservation_repo, room_repo, guest_repo)

    app.register_blueprint(room_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(reservation_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Método no permitido"}), 405

    with app.app_context():
        db.create_all()
        if app.config["SEED"]:
            seed()

    return app