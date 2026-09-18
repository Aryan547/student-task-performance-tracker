import os
import click
from flask import Flask, jsonify, render_template, request
from config import config
from database import close_db, init_db
from routes import views_bp, api_bp

def create_app(config_name=None):
    """Application factory for Student Task & Performance Tracker."""
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Register teardown function to close DB connection
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    # Register CLI command for initializing DB
    @app.cli.command("init-db")
    def init_db_cli():
        """Initialize the SQLite database."""
        init_db(app)
        click.echo("Database initialized successfully.")

    # Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Requested resource not found"}), 404
        return render_template("base.html", error_message="404 - Page Not Found"), 404

    @app.errorhandler(400)
    def handle_bad_request(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Bad request"}), 400
        return render_template("base.html", error_message="400 - Bad Request"), 400

    @app.errorhandler(500)
    def handle_server_error(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Internal server error"}), 500
        return render_template("base.html", error_message="500 - Internal Server Error"), 500

    return app

if __name__ == "__main__":
    app = create_app("development")
    db_path = app.config["DATABASE"]
    if not os.path.exists(db_path):
        print(f"Initializing database at {db_path}...")
        init_db(app)
    print("Starting Student Task & Performance Tracker on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
