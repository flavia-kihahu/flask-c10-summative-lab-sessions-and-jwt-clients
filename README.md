# Notes API
A secure Flask REST API where users register, log in, and manage their own private notes. Authentication uses JWT bearer tokens, passwords are hashed with Flask-Bcrypt, and every notes route is restricted to the token owner's records.

## Installation
pipenv install
pipenv shell
export FLASK_APP=app.py
flask db init
flask db migrate -m "create users and notes"
flask db upgrade
python seed.py

Optional environment variables: `JWT_SECRET_KEY` (token signing key, set in production), `DATABASE_URI` (default `sqlite:///app.db`).

## Run
python app.py          # http://localhost:5555

Frontend (separate terminal): cd client-with-jwt && npm install && npm start (port 4000, proxies to 5555).

## Endpoints
Errors are returned as `{"errors": ["message", ...]}`.

### Auth
| Method | Path | Description |
| POST | `/signup` | Body: `username` (3-50 chars), `password` (min 6), `password_confirmation`. Returns `{token, user}` with 201, or 422 if invalid, mismatched or duplicate. |
| POST | `/login` | Body: `username`, `password`. Returns `{token, user}` with 200, or 401 if invalid. |
| GET | `/me` | Returns the user the token belongs to. 401 if the token is missing, invalid or expired. |

All notes routes require the header `Authorization: Bearer <token>` (401 otherwise).

| Method | Path | Description |
| GET | `/notes?page=1&per_page=10` | Paginated list of your notes, newest first. `per_page` max 50. Returns `page`, `per_page`, `total`, `total_pages`, `notes`. 400 on bad params. |
| POST | `/notes` | Create a note (`title`, `content`). 201, or 422 on invalid input. |
| GET | `/notes/<id>` | Get one of your notes. |
| PATCH | `/notes/<id>` | Update `title` and/or `content`. 200, or 422 on invalid input. |
| DELETE | `/notes/<id>` | Delete a note. 204. |

A note that doesn't exist or belongs to another user returns **404** in both cases, so other users' records are never revealed.
