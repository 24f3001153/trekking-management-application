from app import app
from extensions import db
from models import User


with app.app_context():

    db.create_all()


    admin = User.query.filter_by(
        role="Admin"
    ).first()


    if admin is None:

        admin = User(
            name="Admin",
            email="admin@gmail.com",
            password="admin123",
            contact="9999999999",
            role="Admin",
            status="Active"
        )

        db.session.add(admin)

        db.session.commit()


        print("Admin created")

    else:

        print("Admin already exists")