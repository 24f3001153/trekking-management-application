from app import db
from datetime import datetime, timezone

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )
    contact = db.Column(
        db.String(15),
        nullable=False
    )
 
    role = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Active"
    )


    bookings = db.relationship(
        "Booking",
        backref="user"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class StaffProfile(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    user = db.relationship(
        "User",
        backref="staff_profile"
    )

    approval_status = db.Column(
        db.String(20),
        default="Pending"
    )



class Trek(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    trek_name = db.Column(
        db.String(100),
        nullable=False
    )


    location = db.Column(
        db.String(100),
        nullable=False
    )


    difficulty = db.Column(
        db.String(20),
        nullable=False
    )


    duration = db.Column(
        db.Integer,
        nullable=False
    )


    available_slots = db.Column(
        db.Integer,
        nullable=False
    )


    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff_profile.id")
    )

    assigned_staff = db.relationship(
        "StaffProfile",
        backref="assigned_treks"
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )


    start_date = db.Column(
        db.Date
    )


    end_date = db.Column(
        db.Date
    )


    bookings = db.relationship(
        "Booking",
        backref="trek"
    )



class Booking(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )


    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("trek.id")
    )


    booking_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


    status = db.Column(
        db.String(20),
        default="Booked"
    )

    payment_status = db.Column(
    db.String(20),
    default="Pending"
    )