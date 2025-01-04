import ast
from datetime import datetime
from flask import Blueprint, render_template, current_app
from flask_pymongo import PyMongo

# Blueprint for web routes
web_bp = Blueprint('web_bp', __name__)

# Create a Blueprint for your routes (user_bp in your case)
@web_bp.route('/profile/<pseudonym>', methods=['GET'])
def render_user_profile(pseudonym):
    mongo = PyMongo(current_app)
    db = mongo.db

    # Find the user by pseudonym
    user = db.users.find_one({"pseudonym": pseudonym})
    if not user:
        return render_template("404.html", error="User profile not found"), 404

    # Safely handle _id (ensure _id is string for rendering)
    user["_id"] = str(user.get("_id", "No ID found"))

    # Extract the user's email from the user document
    user_email = user.get('email', '').strip()

    if not user_email:
        return render_template("404.html", error="User email not found"), 404

    # Debug: print the user's email to check if it was fetched correctly
    print(f"User Email: '{user_email}'")

    # Fetch the portfolio data using the email from the user's document
    portfolio = db.portfolios.find_one({"email": user_email})

    # Debug: print the portfolio document fetched
    print(f"Querying Portfolio with Email: {user_email}")
    if portfolio:
        print(f"Portfolio Found: {portfolio}")
    else:
        print("No portfolio found for this user.")

    if not portfolio:
        portfolio = {
            "skills": [],
            "work_experience": [],
            "education": [],
            "links": []  # Default empty links field if portfolio is empty
        }

    # Safely handle _id in portfolio if exists
    portfolio["_id"] = str(portfolio.get("_id", "No ID found"))

    # Extract the links from the portfolio (if any)
    links = portfolio.get("links", [])  # Default to an empty list if links are missing

    # Process work experience and education fields for date formatting
    for work in portfolio.get("work_experience", []):
        if isinstance(work.get("start_date"), str):
            work["start_date"] = datetime.strptime(work["start_date"], "%Y-%m-%dT%H:%M:%S.%f")
        if isinstance(work.get("end_date"), str):
            work["end_date"] = datetime.strptime(work["end_date"], "%Y-%m-%dT%H:%M:%S.%f")

    for edu in portfolio.get("education", []):
        if isinstance(edu.get("start_date"), str):
            edu["start_date"] = datetime.strptime(edu["start_date"], "%Y-%m-%dT%H:%M:%S.%f")
        if isinstance(edu.get("end_date"), str):
            edu["end_date"] = datetime.strptime(edu["end_date"], "%Y-%m-%dT%H:%M:%S.%f")

    # Pass user, portfolio, and links data to the HTML template
    return render_template("profiles.html", user=user, portfolio=portfolio, links=links)
