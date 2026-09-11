from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
from functools import wraps


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)

app.secret_key = "customer-feedback-secret-key"

DATABASE = "feedback.db"


# ==========================================
# ADMIN LOGIN DETAILS
# ==========================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ==========================================
# LOGIN REQUIRED DECORATOR
# ==========================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "admin_logged_in" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# CREATE DATABASE TABLE
# ==========================================

def create_table():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            rating INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# SUBMIT CUSTOMER FEEDBACK
# ==========================================

@app.route("/submit", methods=["POST"])
def submit_feedback():

    # Get data from HTML form

    name = request.form.get("name", "").strip()

    email = request.form.get("email", "").strip()

    rating = request.form.get("rating", "").strip()

    feedback = request.form.get("feedback", "").strip()


    # ======================================
    # CHECK EMPTY FIELDS
    # ======================================

    if not name or not email or not rating or not feedback:

        flash(
            "Please fill all fields.",
            "error"
        )

        return redirect(url_for("home"))


    # ======================================
    # CHECK RATING
    # ======================================

    try:

        rating = int(rating)

    except ValueError:

        flash(
            "Please select a valid rating.",
            "error"
        )

        return redirect(url_for("home"))


    # Rating must be between 1 and 5

    if rating < 1 or rating > 5:

        flash(
            "Rating must be between 1 and 5.",
            "error"
        )

        return redirect(url_for("home"))


    # ======================================
    # DECIDE FEEDBACK CATEGORY
    # ======================================

    if rating >= 4:

        category = "Positive"

    elif rating == 3:

        category = "Neutral"

    else:

        category = "Negative"


    # ======================================
    # CURRENT DATE AND TIME
    # ======================================

    created_at = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )


    # ======================================
    # SAVE FEEDBACK INTO DATABASE
    # ======================================

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO feedback
        (
            name,
            email,
            rating,
            feedback,
            category,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        rating,
        feedback,
        category,
        created_at
    ))

    connection.commit()

    connection.close()


    # ======================================
    # SUCCESS MESSAGE
    # ======================================

    flash(
        "Thank you! Your feedback has been submitted successfully.",
        "success"
    )

    return redirect(url_for("home"))


# ==========================================
# ADMIN LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # If admin is already logged in
    # don't show login page again

    if "admin_logged_in" in session:

        return redirect(url_for("admin"))


    # Check login form submission

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # Check username and password

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            # Store login status in session

            session["admin_logged_in"] = True

            flash(
                "Login successful!",
                "success"
            )

            return redirect(url_for("admin"))


        else:

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(url_for("login"))


    return render_template("login.html")


# ==========================================
# ADMIN LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    # Remove admin login session

    session.pop("admin_logged_in", None)

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("login"))


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
@login_required
def admin():

    # Connect database

    connection = get_db_connection()


    # Get all feedback

    feedback_list = connection.execute("""
        SELECT *
        FROM feedback
        ORDER BY id DESC
    """).fetchall()


    # ======================================
    # TOTAL FEEDBACK
    # ======================================

    total_feedback = len(feedback_list)


    # ======================================
    # AVERAGE RATING
    # ======================================

    if total_feedback > 0:

        average_rating = round(
            sum(
                row["rating"]
                for row in feedback_list
            ) / total_feedback,
            1
        )

    else:

        average_rating = 0


    # ======================================
    # POSITIVE FEEDBACK COUNT
    # ======================================

    positive_count = sum(
        1
        for row in feedback_list
        if row["category"] == "Positive"
    )


    # ======================================
    # NEUTRAL FEEDBACK COUNT
    # ======================================

    neutral_count = sum(
        1
        for row in feedback_list
        if row["category"] == "Neutral"
    )


    # ======================================
    # NEGATIVE FEEDBACK COUNT
    # ======================================

    negative_count = sum(
        1
        for row in feedback_list
        if row["category"] == "Negative"
    )


    # ======================================
    # RATING DISTRIBUTION
    # ======================================

    rating_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0
    }


    # Count how many customers selected
    # each rating

    for row in feedback_list:

        rating_counts[row["rating"]] += 1


    # ======================================
    # RATING PERCENTAGES
    # ======================================

    rating_percentages = {}


    for rating in range(1, 6):

        if total_feedback > 0:

            rating_percentages[rating] = round(
                (
                    rating_counts[rating]
                    / total_feedback
                ) * 100
            )

        else:

            rating_percentages[rating] = 0


    # Close database

    connection.close()


    # ======================================
    # SEND DATA TO ADMIN.HTML
    # ======================================

    return render_template(
        "admin.html",

        feedback_list=feedback_list,

        total_feedback=total_feedback,

        average_rating=average_rating,

        positive_count=positive_count,

        neutral_count=neutral_count,

        negative_count=negative_count,

        rating_counts=rating_counts,

        rating_percentages=rating_percentages
    )


# ==========================================
# DELETE FEEDBACK
# ==========================================

@app.route(
    "/delete/<int:feedback_id>",
    methods=["POST"]
)
@login_required
def delete_feedback(feedback_id):

    connection = get_db_connection()


    connection.execute(
        "DELETE FROM feedback WHERE id = ?",
        (feedback_id,)
    )


    connection.commit()

    connection.close()


    flash(
        "Feedback deleted successfully.",
        "success"
    )


    return redirect(url_for("admin"))


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    # Create table if it does not exist

    create_table()


    # Start Flask server

    app.run(debug=True)