
# edudap-office/app/__init__.py
import os
from flask import Flask

def create_app():
    """
    Flask Application Factory.
    Gunicorn (run:app) will import create_app() via run.py and get the app from here.
    """
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # Basic config
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

    # --- Register Blueprints (import inside the factory!) ---

    # If you have an auth blueprint, register it first so login routes exist.
    # This try/except avoids crashes if auth module is absent.
    try:
        from .auth import auth_bp  # expects app/auth.py with auth_bp = Blueprint(...)
        app.register_blueprint(auth_bp)
    except Exception:
        # No auth blueprint available; continue without it.
        pass

    # Portal blueprint (this one you definitely have)
    from .portal import portal_bp
    app.register_blueprint(portal_bp)

    # Simple health check
    @app.get("/healthz")
    def healthz():
        return {"ok": True}, 200

    return app
