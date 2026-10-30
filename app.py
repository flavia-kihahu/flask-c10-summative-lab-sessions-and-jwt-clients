from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from config import api, app, db, jwt
from models import Note, User, note_schema, notes_schema, signup_schema, user_schema

MAX_PER_PAGE = 50
def flatten_errors(messages):
    return [f"{field}: {msg}" for field, msgs in messages.items() for msg in msgs]
def current_user_id():
    return int(get_jwt_identity())
def own_note_or_404(note_id):
    return Note.query.filter_by(id=note_id, user_id=current_user_id()).first()
@jwt.unauthorized_loader
def missing_token(reason):
    return {"errors": ["Missing or malformed Authorization header."]}, 401
@jwt.invalid_token_loader
def invalid_token(reason):
    return {"errors": ["Invalid token."]}, 401
@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return {"errors": ["Token has expired."]}, 401
class Signup(Resource):
    def post(self):
        body = request.get_json() or {}
        try:
            data = signup_schema.load({k: body.get(k) for k in ("username", "password") if k in body})
        except ValidationError as err:
            return {"errors": flatten_errors(err.messages)}, 422
        if data["password"] != body.get("password_confirmation"):
            return {"errors": ["Password confirmation does not match."]}, 422
        if User.query.filter_by(username=data["username"]).first():
            return {"errors": ["Username already taken."]}, 422
        user = User(username=data["username"])
        user.password_hash = data["password"]
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))
        return {"token": token, "user": user_schema.dump(user)}, 201
class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        user = User.query.filter_by(username=data.get("username")).first()
        if user and user.authenticate(data.get("password") or ""):
            token = create_access_token(identity=str(user.id))
            return {"token": token, "user": user_schema.dump(user)}, 200
        return {"errors": ["Invalid username or password."]}, 401
class Me(Resource):
    method_decorators = [jwt_required()]
    def get(self):
        user = db.session.get(User, current_user_id())
        if not user:
            return {"errors": ["User not found."]}, 401
        return user_schema.dump(user), 200
class NoteIndex(Resource):
    method_decorators = [jwt_required()]
    def get(self):
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            return {"errors": ["page and per_page must be integers."]}, 400
        if page < 1 or per_page < 1:
            return {"errors": ["page and per_page must be positive."]}, 400
        per_page = min(per_page, MAX_PER_PAGE)
        pagination = (
            Note.query.filter_by(user_id=current_user_id())
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
            "notes": notes_schema.dump(pagination.items),
        }, 200
    def post(self):
        try:
            data = note_schema.load(request.get_json() or {})
        except ValidationError as err:
            return {"errors": flatten_errors(err.messages)}, 422
        note = Note(title=data["title"], content=data["content"], user_id=current_user_id())
        db.session.add(note)
        db.session.commit()
        return note_schema.dump(note), 201
class NoteDetail(Resource):
    method_decorators = [jwt_required()]
    def get(self, note_id):
        note = own_note_or_404(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        return note_schema.dump(note), 200
    def patch(self, note_id):
        note = own_note_or_404(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        try:
            data = note_schema.load(request.get_json() or {}, partial=True)
        except ValidationError as err:
            return {"errors": flatten_errors(err.messages)}, 422
        for field, value in data.items():
            setattr(note, field, value)
        db.session.commit()
        return note_schema.dump(note), 200
    def delete(self, note_id):
        note = own_note_or_404(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        db.session.delete(note)
        db.session.commit()
        return {}, 204
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Me, "/me")
api.add_resource(NoteIndex, "/notes")
api.add_resource(NoteDetail, "/notes/<int:note_id>")
if __name__ == "__main__":
    app.run(port=5555, debug=True)