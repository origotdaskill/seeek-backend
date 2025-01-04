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

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
        
def get_portfolio_by_user(user_id):
    mongo = PyMongo(current_app)
    db = mongo.db
    return mongo.db.portfolios.find_one({"user_id": user_id})

# Route to handle skills
@portfolio_bp.route('/portfolio/<user_id>/skills', methods=['GET', 'POST'])
def skills(user_id):
    portfolio = get_portfolio_by_user(user_id)
    mongo = PyMongo(current_app)
    db = mongo.db
    
    if request.method == 'GET':
        return jsonify(portfolio.get('skills', [])) if portfolio else jsonify({"error": "User not found"}), 404
    
    if request.method == 'POST':
        new_skills = request.json.get('skills', [])
        if portfolio:
            mongo.db.portfolios.update_one(
                {"user_id": user_id},
                {"$set": {"skills": new_skills}}
            )
            return jsonify({"message": "Skills updated successfully"}), 200
        else:
            mongo.db.portfolios.insert_one({"user_id": user_id, "skills": new_skills})
            return jsonify({"message": "Portfolio created with skills"}), 201

# Route to handle work experience
@portfolio_bp.route('/portfolio/<user_id>/work_experience', methods=['GET', 'POST'])
def work_experience(user_id):
    portfolio = get_portfolio_by_user(user_id)
    mongo = PyMongo(current_app)
    db = mongo.db
    if request.method == 'GET':
        return jsonify(portfolio.get('work_experience', [])) if portfolio else jsonify({"error": "User not found"}), 404
    
    if request.method == 'POST':
        new_experience = request.json.get('work_experience', [])
        if portfolio:
            mongo.db.portfolios.update_one(
                {"user_id": user_id},
                {"$set": {"work_experience": new_experience}}
            )
            return jsonify({"message": "Work experience updated successfully"}), 200
        else:
            mongo.db.portfolios.insert_one({"user_id": user_id, "work_experience": new_experience})
            return jsonify({"message": "Portfolio created with work experience"}), 201

# Route to handle education details
@portfolio_bp.route('/portfolio/<user_id>/education', methods=['GET', 'POST'])
def education(user_id):
    portfolio = get_portfolio_by_user(user_id)
    mongo = PyMongo(current_app)
    db = mongo.db
    if request.method == 'GET':
        return jsonify(portfolio.get('education', [])) if portfolio else jsonify({"error": "User not found"}), 404
    
    if request.method == 'POST':
        new_education = request.json.get('education', [])
        if portfolio:
            mongo.db.portfolios.update_one(
                {"user_id": user_id},
                {"$set": {"education": new_education}}
            )
            return jsonify({"message": "Education details updated successfully"}), 200
        else:
            mongo.db.portfolios.insert_one({"user_id": user_id, "education": new_education})
            return jsonify({"message": "Portfolio created with education details"}), 201




























def init_portfolio_routes(mongo):
    global _routes_initialized
    if _routes_initialized:  # Check if routes are already registered
        return portfolio_bp

    @portfolio_bp.route("/all", methods=["GET"])
    def get_all_portfolio():
        try:
            portfolios = mongo.db.portfolio.find()
            portfolio_list = [
                {**portfolio, "_id": str(portfolio["_id"])} for portfolio in portfolios
            ]
            return jsonify(portfolio_list), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @portfolio_bp.route("/add", methods=["POST"])
    def add_portfolio():
        db = mongo.db
        skills = request.json.get("skills")
        work_experience = request.json.get("work_experience")
        education = request.json.get("education")

        if not skills or not work_experience or not education:
            return jsonify({"error": "Missing fields"}), 400

        user_id = request.json.get("user_id")
        portfolio_item = Portfolio(
            user_id=user_id, skills=skills, work_experience=work_experience, education=education
        )

        db.portfolio.insert_one(portfolio_item.to_dict())
        return jsonify({"message": "Portfolio item added successfully!"}), 201

    @portfolio_bp.route("/update/<user_id>", methods=["PUT"])
    def update_portfolio(user_id):
        # Get the MongoDB instance
        mongo = PyMongo(current_app)
        db = mongo.db
        
        # Get the new data from the request
        data = request.json
        
        # Ensure there are skills, work experience, or education fields to update
        if not any(field in data for field in ['skills', 'work_experience', 'education']):
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Prepare the update query to find the portfolio by user_id
        updated_item = {"$set": data}
        
        # Update the portfolio by user_id (assuming user_id is part of the portfolio document)
        result = db.portfolio.update_one({"user_id": user_id}, updated_item)
        
        if result.matched_count:
            return jsonify({"message": "Portfolio updated successfully!"}), 200
        else:
            return jsonify({"error": "Portfolio for this user not found"}), 404

    @portfolio_bp.route("/delete/<user_id>/<portfolio_id>", methods=["DELETE"])
    def delete_portfolio(user_id, portfolio_id):
        # Get the MongoDB instance
        mongo = PyMongo(current_app)
        db = mongo.db

        # Convert the portfolio_id to ObjectId for MongoDB query
        try:
            portfolio_object_id = ObjectId(portfolio_id)
        except Exception as e:
            return jsonify({"error": f"Invalid portfolio ID: {str(e)}"}), 400

        # Find and delete the portfolio by user_id and portfolio _id
        result = db.portfolio.delete_one({
            "user_id": user_id,
            "_id": portfolio_object_id
        })

        if result.deleted_count:
            return jsonify({"message": "Portfolio item deleted successfully!"}), 200
        else:
            return jsonify({"error": "Portfolio item not found for this user"}), 404
        
    @portfolio_bp.route("/delete_skill/<user_id>", methods=["DELETE"])
    def delete_skill(user_id):
        # Get the MongoDB instance
        mongo = PyMongo(current_app)
        db = mongo.db
        
        # Get the skill to delete from the request body
        skill_to_delete = request.json.get("skill")
        
        if not skill_to_delete:
            return jsonify({"error": "No skill provided to delete"}), 400
        
        # Use the $pull operator to remove the skill from the user's portfolio
        result = db.portfolio.update_one(
            {"user_id": user_id}, 
            {"$pull": {"skills": skill_to_delete}}
        )
        
        if result.modified_count:
            return jsonify({"message": f"Skill '{skill_to_delete}' deleted successfully!"}), 200
        else:
            return jsonify({"error": "Skill not found or not modified"}), 404   

    @portfolio_bp.route("/user/<user_id>", methods=["GET"])
    def get_all_portfolios_by_user(user_id):
        db = mongo.db
        portfolios = db.portfolio.find({"user_id": user_id})  # Find all portfolios with the specific user_id

        # If portfolios are found, convert them into a list of dictionaries
        portfolio_list = []
        for portfolio in portfolios:
            portfolio["_id"] = str(portfolio["_id"])  # Convert ObjectId to string
            portfolio_list.append(portfolio)

        if portfolio_list:
            return jsonify({"portfolios": portfolio_list}), 200
        return jsonify({"error": "No portfolios found for this user"}), 404
    
    @portfolio_bp.route("/delete_attribute/<user_id>", methods=["DELETE"])
    def delete_attribute(user_id):
        # Get the MongoDB instance
        mongo = PyMongo(current_app)
        db = mongo.db

        # Get the field (attribute) to delete and the value from the request body
        field_to_delete = request.json.get("field")  # 'skills', 'work_experience', 'education', etc.
        value_to_delete = request.json.get("value")  # Value within the field to remove (e.g., "Flask", "Company A - 3 years", etc.)

        if not field_to_delete or not value_to_delete:
            return jsonify({"error": "Field or value not provided"}), 400

        # Update the portfolio by pulling (deleting) the value from the specified field
        update_query = {field_to_delete: value_to_delete}
        result = db.portfolio.update_one(
            {"user_id": user_id, field_to_delete: value_to_delete},  # Match by user_id and field value
            {"$pull": update_query}  # Pull (delete) the value from the specified field
        )

        # Check if the update was successful
        if result.matched_count > 0:
            return jsonify({"message": f"{value_to_delete} deleted from {field_to_delete} successfully!"}), 200
        else:
            return jsonify({"error": f"{value_to_delete} not found in {field_to_delete} for this user"}), 404 
    
    @portfolio_bp.route("/update_attribute/<user_id>", methods=["PUT"])
    def update_attribute(user_id):
        # Get the MongoDB instance
        mongo = PyMongo(current_app)
        db = mongo.db

        # Get the field (attribute) to update, the old value, and the new value from the request body
        field_to_update = request.json.get("field")  # 'skills', 'work_experience', 'education', etc.
        old_value = request.json.get("old_value")  # The value to replace
        new_value = request.json.get("new_value")  # The new value to replace the old value with

        if not field_to_update or not old_value or not new_value:
            return jsonify({"error": "Field, old_value, or new_value not provided"}), 400

        # Update the portfolio by replacing the old value with the new value in the specified field
        update_query = {field_to_update: old_value}
        update_data = {"$set": {f"{field_to_update}.$": new_value}}  # Use positional operator to update the array element

        result = db.portfolio.update_one(
            {"user_id": user_id, field_to_update: old_value},  # Match by user_id and field value
            update_data  # Update the array element
        )

        # Check if the update was successful
        if result.matched_count > 0:
            return jsonify({"message": f"{field_to_update} updated successfully!"}), 200
        else:
            return jsonify({"error": f"{old_value} not found in {field_to_update} for this user"}), 404
            
            
            
    _routes_initialized = True
    return portfolio_bp





# Helper function to initialize PyMongo and register routes

