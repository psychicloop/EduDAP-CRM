
# edudap-office/run.py
from app import create_app

# Gunicorn entrypoint will import "app" from this module: run:app
app = create_app()

if __name__ == "__main__":
    # Useful for local runs (Render will use gunicorn):
    app.run(host="0.0.0.0", port=5000, debug=False)
``
