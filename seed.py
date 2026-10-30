from faker import Faker
from app import app
from config import db
from models import Note, User

fake = Faker()
with app.app_context():
    print("Clearing old data...")
    Note.query.delete()
    User.query.delete()
    print("Seeding users and notes...")
    for username in ["alice", "bob", "carol"]:
        user = User(username=username)
        user.password_hash = "password123"
        db.session.add(user)
        for _ in range(15):
            db.session.add(Note(
                title=fake.sentence(nb_words=4).rstrip("."),
                content=fake.paragraph(nb_sentences=3),
                user=user,
            ))
    db.session.commit()
    print("Done.")