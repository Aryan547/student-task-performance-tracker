import os
import tempfile
import pytest
from app import create_app
from database import init_db

@pytest.fixture
def app():
    """Create and configure a new app instance with an isolated test database for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    app = create_app("testing")
    app.config.update({
        "DATABASE": db_path,
        "TESTING": True,
    })

    with app.app_context():
        init_db(app)

    yield app

    os.close(db_fd)
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except PermissionError:
            pass

@pytest.fixture
def client(app):
    """Test client for simulating HTTP requests."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner for testing Flask CLI commands."""
    return app.test_cli_runner()
