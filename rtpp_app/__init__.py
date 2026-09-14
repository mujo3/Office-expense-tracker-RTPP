from flask import Flask, redirect, url_for
from config import Config, config_by_name
from flask_migrate import Migrate
from rtpp_app.extensions import db, login_manager, mail, csrf
from flask_login import current_user
from rtpp_app.models import invoice, product, category, vendor, user, blacklisttokens, measuringunits, budgets, categorybudgets
from rtpp_app.routes.admin import admin_bp
from rtpp_app.routes.expenses import expenses_bp
from rtpp_app.routes.reports  import reports_bp

login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')

    csrf.init_app(app)

    if config_name and config_name in config_by_name:
        app.config.from_object(config_by_name[config_name])
    else:
        app.config.from_object(Config)

    app.config["WTF_CSRF_ENABLED"] = False

    import rtpp_app.models

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from rtpp_app.routes.auth import auth_bp
    from rtpp_app.routes.main import main_bp
    from rtpp_app.routes.expenses import expenses_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp, url_prefix='/reports')

    @app.route('/')
    def home():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return redirect(url_for('main.dashboard'))

    return app
