from flask import Flask
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

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

@app.route("/admin")
def admin_dashboard():

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    return render_template(
        "admin_dashboard.html"
    )


@app.route("/staff")
def staff_dashboard():

    if session.get("role") != "Staff":
        return redirect(url_for("login"))

    return render_template(
        "staff_dashboard.html"
    )


@app.route("/user")
def user_dashboard():

    if session.get("role") != "Trekker":
        return redirect(url_for("login"))

    return render_template(
        "user_dashboard.html"
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )

if __name__ == "__main__":
    app.run(debug=True)