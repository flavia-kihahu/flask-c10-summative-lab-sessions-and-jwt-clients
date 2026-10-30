import os
from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_migrate import Migrate
from flask_restful import Api
from jwt.exceptions import PyJWTError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

class JWTApi(Api):
    def handle_error(self, e):
        if isinstance(e, (JWTExtendedException, PyJWTError)):
            raise e
        return super().handle_error(e)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-jwt")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.json.compact = False
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = JWTApi(app)