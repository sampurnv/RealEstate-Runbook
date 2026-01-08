from flask import Flask, render_template


def create_app() -> Flask:
    app = Flask(__name__)

    from .routes import bp as api_bp  # noqa: E402
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    return app
