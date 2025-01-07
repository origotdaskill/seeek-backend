from flask import Blueprint, request, jsonify
from flask_pymongo import PyMongo
from flask import current_app
from models.portfolio import Portfolio
from bson import ObjectId


portfolio_bp = Blueprint("portfolio", __name__)

# Prevent duplicate route registration
_routes_initialized = False


def get_portfolio_by_email(email):
    mongo = PyMongo(current_app)
    db = mongo.db
    return db.portfolios.find_one({"email": email})


# Helper function to update a portfolio field
def update_portfolio_field(email, field, data):
    mongo = PyMongo(current_app)
    db = mongo.db
    return db.portfolios.update_one(
        {"email": email},
        {"$set": {field: data}}
    )


# Route to handle Skills
@portfolio_bp.route('/<email>/skills', methods=['GET', 'POST', 'DELETE'])
def manage_skills(email):
    portfolio = get_portfolio_by_email(email)
    mongo = PyMongo(current_app)
    db = mongo.db

    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    if request.method == 'GET':
        return jsonify(portfolio.get('skills', []))

    if request.method == 'POST':
        new_skills = request.json.get('skills', [])
        update_portfolio_field(email, 'skills', new_skills)
        return jsonify({"message": "Skills updated successfully"}), 200

    if request.method == 'DELETE':
        update_portfolio_field(email, 'skills', [])
        return jsonify({"message": "Skills deleted successfully"}), 200


# Route to handle Work Experience
@portfolio_bp.route('/<email>/work_experience', methods=['GET', 'POST', 'DELETE'])
def manage_work_experience(email):
    portfolio = get_portfolio_by_email(email)
    mongo = PyMongo(current_app)    
    db = mongo.db

    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    if request.method == 'GET':
        return jsonify(portfolio.get('work_experience', []))

    if request.method == 'POST':
        new_experience = request.json.get('work_experience', [])
        update_portfolio_field(email, 'work_experience', new_experience)
        return jsonify({"message": "Work experience updated successfully"}), 200

    if request.method == 'DELETE':
        update_portfolio_field(email, 'work_experience', [])
        return jsonify({"message": "Work experience deleted successfully"}), 200


# Route to handle Education
@portfolio_bp.route('/<email>/education', methods=['GET', 'POST', 'DELETE'])
def manage_education(email):
        portfolio = get_portfolio_by_email(email)
        mongo = PyMongo(current_app)    
        db = mongo.db

        if not portfolio:
            return jsonify({"error": "Portfolio not found"}), 404

        if request.method == 'GET':
            return jsonify(portfolio.get('education', []))

        if request.method == 'POST':
            new_education = request.json.get('education', [])
            update_portfolio_field(email, 'education', new_education)
            return jsonify({"message": "Education details updated successfully"}), 200

        if request.method == 'DELETE':
            update_portfolio_field(email, 'education', [])
            return jsonify({"message": "Education details deleted successfully"}), 200
        

@portfolio_bp.route('/<email>/links', methods=['GET', 'POST', 'DELETE'])
def manage_links(email):
    portfolio = get_portfolio_by_email(email)
    
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404
    
    # Handle GET request: Fetch the links
    if request.method == 'GET':
        return jsonify(portfolio.get('links', [])), 200
    
    # Handle POST request: Add a new link
    elif request.method == 'POST':
        # Get the new link data from the request body
        new_link = request.json.get('link', None)
        link_name = request.json.get('name', None)

        if not new_link or not link_name:
            return jsonify({"error": "Both name and link are required"}), 400

        # Add the new link to the links array
        links = portfolio.get('links', [])
        links.append({'name': link_name, 'link': new_link})

        # Update the portfolio with the new links array
        update_portfolio_field(email, 'links', links)

        return jsonify({"message": "Link added successfully"}), 200
    
    # Handle DELETE request: Delete a link
    elif request.method == 'DELETE':
        # Get the link name to delete from the request body
        link_name = request.json.get('name', None)

        if not link_name:
            return jsonify({"error": "Link name is required"}), 400

        # Find the link in the current list
        links = portfolio.get('links', [])
        
        # Remove the link if it exists
        links = [link for link in links if link['name'] != link_name]

        # Update the portfolio with the modified links array
        update_portfolio_field(email, 'links', links)

        return jsonify({"message": f"Link '{link_name}' deleted successfully"}), 200

