from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from rtpp_app.extensions import db, login_manager
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    must_change_pwd  = db.Column(db.Boolean, default=True, nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reset_password_link = db.Column(db.String, nullable=True)
    role = db.Column(db.Enum('admin', 'employee', name='roles'), nullable=False)

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(int(user_id))
