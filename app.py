from flask import Flask
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)
from extensions import db

app = Flask(__name__)

app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from models import *


@app.route("/")
def home():
    return "Trekking Management Application"


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(
            email=email
        ).first()

        if user is None:
            return render_template(
                "login.html",
                message="Invalid email"
            )

        if user.password != password:
            return render_template(
                "login.html",
                message="Invalid password"
            )

        if user.status == "Blacklisted":
            return render_template(
                "login.html",
                message="Your account has been blacklisted"
            )

        if user.role == "Staff":

            staff = StaffProfile.query.filter_by(
                user_id=user.id
            ).first()

            if staff.approval_status != "Approved":
                return render_template(
                    "login.html",
                    message="Waiting for admin approval"
                )

        session["user_id"] = user.id
        session["role"] = user.role

        if user.role == "Admin":
            return redirect(
                url_for("admin_dashboard")
            )

        elif user.role == "Staff":
            return redirect(
                url_for("staff_dashboard")
            )

        else:
            return redirect(
                url_for("user_dashboard")
            )

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        role = request.form['role']

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return render_template(
                "register.html",
                message="Email already registered"
            )

        new_user = User(
            name=name,
            email=email,
            password=password,
            contact=contact,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        if role == "Staff":

            staff_profile = StaffProfile(
                user_id=new_user.id,
                approval_status="Pending"
            )

            db.session.add(staff_profile)
            db.session.commit()

        return render_template(
            "login.html",
            message="Registration successful. Please login."
        )

    return render_template("register.html")


# ---------- ADMIN DASHBOARD ----------

@app.route("/admin")
def admin_dashboard():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="Trekker").count()
    total_staff = User.query.filter_by(role="Staff").count()
    total_bookings = Booking.query.count()

    return render_template(
        "admin_dashboard.html",
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings
    )


# ---------- TREK MANAGEMENT ----------

@app.route("/admin/treks")
def admin_treks():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    treks = Trek.query.all()

    return render_template("admin_treks.html", treks=treks)


@app.route("/admin/treks/add", methods=['GET', 'POST'])
def admin_add_trek():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    if request.method == 'POST':

        new_trek = Trek(
            trek_name=request.form['trek_name'],
            location=request.form['location'],
            difficulty=request.form['difficulty'],
            duration=request.form['duration'],
            available_slots=request.form['available_slots'],
            status="Pending"
        )

        db.session.add(new_trek)
        db.session.commit()

        return redirect(url_for("admin_treks"))

    return render_template("admin_trek_form.html", trek=None)


@app.route("/admin/treks/edit/<int:trek_id>", methods=['GET', 'POST'])
def admin_edit_trek(trek_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':

        trek.trek_name = request.form['trek_name']
        trek.location = request.form['location']
        trek.difficulty = request.form['difficulty']
        trek.duration = request.form['duration']
        trek.available_slots = request.form['available_slots']
        trek.status = request.form['status']

        db.session.commit()

        return redirect(url_for("admin_treks"))

    return render_template("admin_trek_form.html", trek=trek)


@app.route("/admin/treks/delete/<int:trek_id>")
def admin_delete_trek(trek_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    return redirect(url_for("admin_treks"))


@app.route("/admin/treks/assign/<int:trek_id>", methods=['GET', 'POST'])
def admin_assign_staff(trek_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    trek = Trek.query.get_or_404(trek_id)

    approved_staff = StaffProfile.query.join(User).filter(
        StaffProfile.approval_status == "Approved",
        User.status != "Blacklisted"
    ).all()

    if request.method == 'POST':

        staff_id = request.form['staff_id']
        staff = StaffProfile.query.get(staff_id)

        if staff is None or staff.approval_status != "Approved" or staff.user.status == "Blacklisted":
            return render_template(
                "admin_assign_staff.html",
                trek=trek,
                staff_list=approved_staff,
                error="Cannot assign a blacklisted or unapproved staff member."
            )

        trek.assigned_staff_id = staff_id
        trek.status = "Approved"

        db.session.commit()

        return redirect(url_for("admin_treks"))

    return render_template(
        "admin_assign_staff.html",
        trek=trek,
        staff_list=approved_staff
    )

@app.route("/admin/treks/unassign/<int:trek_id>")
def admin_unassign_staff(trek_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    trek = Trek.query.get_or_404(trek_id)

    trek.assigned_staff_id = None
    trek.status = "Pending"

    db.session.commit()

    return redirect(url_for("admin_treks"))

# ---------- STAFF MANAGEMENT ----------

@app.route("/admin/staff")
def admin_staff():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    staff_profiles = StaffProfile.query.all()

    return render_template(
        "admin_staff.html",
        staff_profiles=staff_profiles,
        error=None
    )


@app.route("/admin/staff/approve/<int:staff_id>")
def admin_approve_staff(staff_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    staff = StaffProfile.query.get_or_404(staff_id)

    staff.approval_status = "Approved"

    db.session.commit()

    return redirect(url_for("admin_staff"))


@app.route("/admin/staff/blacklist/<int:staff_id>")
def admin_blacklist_staff(staff_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    staff = StaffProfile.query.get_or_404(staff_id)
    staff.user.status = "Blacklisted"
    staff.approval_status = "Rejected"

    db.session.commit()

    return redirect(url_for("admin_staff"))


@app.route("/admin/staff/delete/<int:staff_id>")
def admin_delete_staff(staff_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    staff = StaffProfile.query.get_or_404(staff_id)

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=staff.id
    ).count()

    if assigned_treks > 0:
        return render_template(
            "admin_staff.html",
            staff_profiles=StaffProfile.query.all(),
            error="Cannot remove staff with assigned treks. Unassign them first."
        )

    user = staff.user

    db.session.delete(staff)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("admin_staff"))


# ---------- USER MANAGEMENT ----------

@app.route("/admin/users")
def admin_users():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    users = User.query.filter_by(role="Trekker").all()

    return render_template("admin_users.html", users=users)


@app.route("/admin/users/blacklist/<int:user_id>")
def admin_blacklist_user(user_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    user = User.query.get_or_404(user_id)
    user.status = "Blacklisted"

    db.session.commit()

    return redirect(url_for("admin_users"))


@app.route("/admin/users/activate/<int:user_id>")
def admin_activate_user(user_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    user = User.query.get_or_404(user_id)
    user.status = "Active"

    db.session.commit()

    return redirect(url_for("admin_users"))


# ---------- BOOKINGS ----------

@app.route("/admin/bookings")
def admin_bookings():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    filter_user_id = request.args.get('user_id', '').strip()

    if filter_user_id:
        bookings = Booking.query.filter_by(user_id=filter_user_id).all()
    else:
        bookings = Booking.query.all()

    return render_template(
        "admin_bookings.html",
        bookings=bookings,
        filter_user_id=filter_user_id
    )


# ---------- SEARCH ----------

@app.route("/admin/search")
def admin_search():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    query = request.args.get('q', '').strip()
    results_type = request.args.get('type', 'trek')

    results = []

    if query:

        if results_type == "trek":
            results = Trek.query.filter(
                (Trek.trek_name.ilike(f"%{query}%")) |
                (Trek.id == query if query.isdigit() else False)
            ).all()

        elif results_type == "staff":
            staff_profiles = StaffProfile.query.all()
            results = [
                s for s in staff_profiles
                if query.lower() in s.user.name.lower()
                or (query.isdigit() and int(query) == s.id)
            ]

        elif results_type == "user":
            results = User.query.filter(
                (User.role == "Trekker") &
                (
                    (User.name.ilike(f"%{query}%")) |
                    (User.id == query if query.isdigit() else False)
                )
            ).all()

    return render_template(
        "admin_search.html",
        results=results,
        results_type=results_type,
        query=query
    )


# STAFF DASHBOARD

@app.route("/staff")
def staff_dashboard():

    if session.get("role") != "Staff":
        return redirect(url_for("login"))

    staff = StaffProfile.query.filter_by(
        user_id=session["user_id"]
    ).first()

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=staff.id
    ).all()

    trek_data = []

    for trek in assigned_treks:
        registered_count = Booking.query.filter_by(
            trek_id=trek.id,
            status="Booked"
        ).count()

        trek_data.append({
            "trek": trek,
            "registered_count": registered_count
        })

    return render_template(
        "staff_dashboard.html",
        trek_data=trek_data,
        staff=staff
    )


@app.route("/staff/profile", methods=['GET', 'POST'])
def staff_profile():

    if session.get("role") != "Staff":
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if request.method == 'POST':

        user.name = request.form['name']
        user.contact = request.form['contact']

        db.session.commit()

        return render_template(
            "staff_profile.html",
            user=user,
            message="Profile updated successfully"
        )

    return render_template("staff_profile.html", user=user)


@app.route("/staff/treks/<int:trek_id>", methods=['GET', 'POST'])
def staff_manage_trek(trek_id):

    if session.get("role") != "Staff":
        return redirect(url_for("login"))

    staff = StaffProfile.query.filter_by(
        user_id=session["user_id"]
    ).first()

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != staff.id:
        return "You are not assigned to manage this trek", 403

    if request.method == 'POST':

        trek.available_slots = request.form['available_slots']
        trek.status = request.form['status']

        db.session.commit()

        return redirect(url_for("staff_dashboard"))

    bookings = Booking.query.filter_by(
        trek_id=trek.id,
        status="Booked"
    ).all()

    return render_template(
        "staff_trek_manage.html",
        trek=trek,
        bookings=bookings
    )


@app.route("/staff/treks/<int:trek_id>/participants")
def staff_view_participants(trek_id):

    if session.get("role") != "Staff":
        return redirect(url_for("login"))

    staff = StaffProfile.query.filter_by(
        user_id=session["user_id"]
    ).first()

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != staff.id:
        return "You are not assigned to manage this trek", 403

    bookings = Booking.query.filter_by(trek_id=trek.id).all()

    return render_template(
        "staff_participants.html",
        trek=trek,
        bookings=bookings
    )

# USER DASHBOARD 
@app.route("/user")
def user_dashboard():

    if session.get("role") != "Trekker":
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    active_bookings = Booking.query.filter_by(
        user_id=user.id,
        status="Booked"
    ).all()

    return render_template(
        "user_dashboard.html",
        user=user,
        active_bookings=active_bookings
    )

@app.route("/user/profile", methods=['GET', 'POST'])
def user_profile():

    if session.get("role") != "Trekker":
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if request.method == 'POST':

        user.name = request.form['name']
        user.contact = request.form['contact']

        db.session.commit()

        return render_template(
            "user_profile.html",
            user=user,
            message="Profile updated successfully"
        )

    return render_template("user_profile.html", user=user)


@app.route("/user/treks")
def user_browse_treks():

    if session.get("role") != "Trekker":
        return redirect(url_for("login"))

    difficulty = request.args.get('difficulty', '')
    location = request.args.get('location', '')

    query = Trek.query.filter_by(status="Open")

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    treks = query.all()

    return render_template(
        "user_browse_treks.html",
        treks=treks,
        difficulty=difficulty,
        location=location
    )


@app.route("/user/treks/book/<int:trek_id>")
def user_book_trek(trek_id):

    if session.get("role") != "Trekker":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return render_template(
            "user_browse_treks.html",
            treks=Trek.query.filter_by(status="Open").all(),
            difficulty='',
            location='',
            error="This trek is not open for booking."
        )

    if trek.available_slots <= 0:
        return render_template(
            "user_browse_treks.html",
            treks=Trek.query.filter_by(status="Open").all(),
            difficulty='',
            location='',
            error="No slots available for this trek."
        )

    existing_booking = Booking.query.filter_by(
        user_id=user_id,
        trek_id=trek.id,
        status="Booked"
    ).first()

    if existing_booking:
        return render_template(
            "user_browse_treks.html",
            treks=Trek.query.filter_by(status="Open").all(),
            difficulty='',
            location='',
            error="You have already booked this trek."
        )

    new_booking = Booking(
        user_id=user_id,
        trek_id=trek.id,
        status="Booked"
    )

    trek.available_slots -= 1

    db.session.add(new_booking)
    db.session.commit()

    return redirect(url_for("user_bookings"))


@app.route("/user/bookings")
def user_bookings():

    if session.get("role") != "Trekker":
        return redirect(url_for("login"))

    user_id = session["user_id"]

    bookings = Booking.query.filter_by(
        user_id=user_id
    ).order_by(Booking.booking_date.desc()).all()

    return render_template("user_bookings.html", bookings=bookings)


@app.route("/user/bookings/cancel/<int:booking_id>")
def user_cancel_booking(booking_id):

    if session.get("role") != "Trekker":
        return redirect(url_for("login"))

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        return "You cannot cancel this booking", 403

    if booking.status == "Booked":
        booking.status = "Cancelled"
        booking.trek.available_slots += 1
        db.session.commit()

    return redirect(url_for("user_bookings"))


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


if __name__ == "__main__":
    app.run(debug=True)