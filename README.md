# Trekking Management Application

A web-based Trekking Management System developed as part of the MAD-I project.

## Project Overview

The application allows three types of users to interact with the system:

- **Admin** - Manages treks, trek staff, users and bookings.
- **Trek Staff** - Manages assigned treks, participants and trek status.
- **Trekkers (Users)** - Browse available treks, make bookings and track trekking history.

## Core Features

- Role-based authentication
- Trek creation and management
- Trek staff approval and assignment
- Trek booking and booking history
- Trek status tracking
- Search and filtering of treks
- Dashboard views for Admin, Trek Staff and Users
- Prevents bookings when trek slots are full

## Technology Stack

- Python
- Flask
- SQLite
- Jinja2
- HTML
- CSS
- Bootstrap

## Running Locally

1. Clone the repo:

```
git clone https://github.com/24f3001153/trekking-management-application.git
```

2. Move into the project folder

```
cd trekking-management-application
```
 
3. Install dependencies:

```
   pip install -r requirements.txt
```
 
4. Set up the database and create the default admin account:
```
   python database.py
```
 
5. Start the app:
```
   python app.py
```
 
6. Visit `http://127.0.0.1:5000/login` in your browser.
 
## Notes
 
- The admin account is pre-created programmatically in `database.py` as required by the project specifications, using a hardcoded default credential for local development and grading purposes.
- Bookings does have a Payment Status field, however, it is not implemented as payment handling wasn't part of the core requirements for this project.
- `requirements.txt` reflects the full development environment. A few packages (eg. matplotlib, pandas, plotly) were installed for using in the optional Charts and Visualization milestone, but isn't implemented in this submission.

## Issues Encountered and Resolutions

During the development of this project, I encountered several implementation and debugging issues. The major ones are listed as below.

### 1. SQLAlchemy Instance Error

The application raised the following error:

```
RuntimeError: The current Flask app is not registered with this SQLAlchemy instance.
```

**Resolution**

The issue was caused by multiple SQLAlchemy instances being created due to the project structure. I moved the database object into a separate `extensions.py` file and initialized it using `db.init_app(app)`. This ensured that the entire application shared a single database instance.

---

### 2. Circular Import Issue

Import errors occurred because `app.py` and `models.py` depended on each other.

**Resolution**

The imports were reorganized by separating the database initialization into `extensions.py`, removing the circular dependency.

---


### 3. Jinja Template Errors

While modifying templates, several `TemplateSyntaxError` exceptions occurred due to unmatched `{% if %}` and `{% endif %}` blocks.

**Resolution**

I reviewed all the templates and corrected the unmatched Jinja conditional blocks.

---

### 4. Empty Booking Table Issue

When a user had no bookings, both the "No Bookings" message and an empty bookings table were displayed.

**Resolution**

The template logic was changed to use a single `if-else` block so that only one of them is displayed.

---

### 5. Staff Approval Validation Issue

A blacklisted staff member could still be approved, while remaining in the blacklisted state, resulting in an inconsistent account status.

**Resolution**

A validation check was added to prevent approval of blacklisted staff members, and an **Activate** option was introduced to restore inactive staff when required.

---

### 6. Assign Staff Page Issue

The Assign Staff page displayed an empty assignment form when no approved staff members were available.

**Resolution**

The page now displays the assignment form only when eligible staff members exist; otherwise, an informative message is shown.

---

### 7. Trek Deletion and Booking History Issue

Deleting a trek that already had bookings resulted in incomplete booking history because the associated trek information no longer existed.

**Resolution**

Trek deletion is now blocked whenever bookings exist for that trek. Admin should mark such treks as **Closed** or **Completed** instead.

---

### 8. Assign Staff Button Issue

Initially, the application only displayed an **Assign Staff** button, making it unclear whether a trek already had a staff member assigned.

**Resolution**

The template was updated to use a single dynamic button. It displays **Assign Staff** when no staff member is assigned to a trek and automatically changes to **Reassign Staff** when a staff member has already been assigned.