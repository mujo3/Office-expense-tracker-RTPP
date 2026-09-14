from flask import Blueprint

main = Blueprint('main', __name__)

from .auth import auth_bp
main.register_blueprint(auth_bp)

from .analytics import analytics_bp
main.register_blueprint(analytics_bp)

def register_routes(app):

    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
