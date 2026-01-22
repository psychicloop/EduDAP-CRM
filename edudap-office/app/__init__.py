
import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from dotenv import load_dotenv

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'


def create_app():
    load_dotenv(override=False)
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from .auth import auth_bp
    from .portal import portal_bp
    from .admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(portal_bp, url_prefix='/app')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # create db
    with app.app_context():
        from . import models  # noqa
        db.create_all()

    @app.route('/')
    def index():
        # If logged in, go to dashboard; else go to login
        if current_user.is_authenticated:
            return redirect(url_for('portal.dashboard'))
        return redirect(url_for('auth.login'))

    return app
