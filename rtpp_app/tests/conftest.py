import pytest
from rtpp_app import create_app, db
from rtpp_app.models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    user = User(
        firstName='Test',
        lastName='User',
        email='test@example.com',
        password=generate_password_hash('password123'),
        role='employee'
    )
    db.session.add(user)
    db.session.commit()
    return user
