from datetime import datetime
from app import db
from .utils import generate_token


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    osu_id = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f"<osu! user ID: {self.osu_id}>"


class ApiKey(db.Model):
    __tablename__ = "api_keys"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), unique=True, default=generate_token(32))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.key}"
