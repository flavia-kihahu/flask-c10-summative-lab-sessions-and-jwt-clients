from datetime import datetime
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy.ext.hybrid import hybrid_property
from config import bcrypt, db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    notes = db.relationship("Note", back_populates="user", cascade="all, delete-orphan")
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="notes")
class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
class SignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)
user_schema = UserSchema()
signup_schema = SignupSchema()
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)