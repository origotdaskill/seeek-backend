from datetime import datetime
from flask import Blueprint, app, json, logging, request, jsonify, current_app, render_template, session
from flask_pymongo import PyMongo
from models.portfolio import Portfolio
from models.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from bson.errors import InvalidId
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
from console.helpers import allowed_file
import ast


# Create a Blueprint for user-related routes
user_bp = Blueprint('user_bp', __name__)
ALLOWED_FILE_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip' ,'png', 'jpg', 'jpeg', 'gif' }
UPLOAD_FOLDER = 'static/uploads'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename, allowed_extensions):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Function to add a new user to the database
def add_user_to_db(user_data, password):
    # Use PyMongo to get the database
    mongo = PyMongo(current_app)
    db = mongo.db

    user = User(**user_data)
    user.set_password(password)  # Hash and set the password
    # Insert the user into the "users" collection
    db.users.insert_one(user.to_dict())
    return user



@user_bp.route("/auth/register", methods=["POST"])
def register_new_user():
    """Register a new user and create a default portfolio."""
    try:
        # Parse JSON request
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # Validate input
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Access MongoDB instance
        mongo = PyMongo(current_app)
        db = mongo.db

        # Check if user already exists
        if db.users.find_one({"email": email}):
            return jsonify({"error": "User with this email already exists"}), 409

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user object
        new_user = {
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }

        # Save user to MongoDB
        db.users.insert_one(new_user)

        # Create a default portfolio for the user
        default_portfolio = Portfolio(
            email=email, 
            skills=[], 
            work_experience=[], 
            education=[]
        ).to_dict()

        db.portfolios.insert_one(default_portfolio)

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        # Handle server errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@user_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    required_fields = ["email", "password"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Use PyMongo to get the database
    mongo = PyMongo(current_app)
    db = mongo.db
    
    user = db.users.find_one({"email": data["email"]})
    if user:
        # Convert ObjectId to string
        user['_id'] = str(user['_id'])
        
        # Verify password (assuming you're using check_password_hash)
        if check_password_hash(user["password"], data["password"]):
            session['user_email'] = data["email"]  # Store email in session
            print(f"Session after login: {session}")  # Print session data for debugging
            return jsonify({"message": "Login successful", "user": user}), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

@user_bp.route('/create-profile', methods=['POST'])
def create_profile():
    """Create or update a user profile, including image and file uploads."""
    mongo = PyMongo(current_app)
    db = mongo.db

    # Retrieve form fields
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    job_title = request.form.get('job_title')
    address = request.form.get('address')
    phone_number = request.form.get('phone_number')
    age = request.form.get('age')
    description = request.form.get('description')
    pseudonym = request.form.get('pseudonym')
    profile_image = request.files.get('picture')  # Handle a single image upload
    uploaded_file = request.files.get('files')  # Handle a single regular file upload

    # Validate email
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Check if the user exists
    existing_user = db.users.find_one({"email": email})
    if not existing_user:
        return jsonify({"error": "User not found"}), 404

    # Check for duplicate pseudonym
    if pseudonym:
        duplicate_pseudonym = db.users.find_one({"pseudonym": pseudonym})
        if duplicate_pseudonym:
            return jsonify({"error": "Pseudonym is already taken"}), 400

    # Initialize file paths as None
    db_image_path = None
    db_file_path = None

    # Handle profile image upload
    if profile_image and allowed_file(profile_image.filename, ALLOWED_FILE_EXTENSIONS):
        filename = secure_filename(profile_image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, "pictures", filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Ensure directory exists
        profile_image.save(image_path)
        db_image_path = f"{filename}"  # Save relative path

    # Handle regular file upload
    if uploaded_file and allowed_file(uploaded_file.filename, ALLOWED_FILE_EXTENSIONS):
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, "files", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
        uploaded_file.save(file_path)
        db_file_path = f"{filename}"  # Save relative path

    # Prepare updated data
    updated_data = {
        "first_name": first_name,
        "last_name": last_name,
        "job_title": job_title,
        "address": address,
        "phone_number": phone_number,
        "age": age,
        "description": description,
        "pseudonym": pseudonym,
        "picture": db_image_path,  # Save the image path
        "files": db_file_path,      # Save the file path
        "updated_at": datetime.utcnow(),
    }

    # Remove None values from the update data
    updated_data = {k: v for k, v in updated_data.items() if v is not None}

    # Update the user profile
    db.users.update_one({"email": email}, {"$set": updated_data})
    return jsonify({"message": "Profile updated successfully", "user": updated_data}), 200

@user_bp.route('/auth/profile-status', methods=['GET'])
def check_profile_status():
    # Ensure MongoDB knows to query by email string
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter is missing"}), 400

    mongo = PyMongo(current_app)
    try:
        # Explicitly use string comparison for email
        user = mongo.db.users.find_one({"email": str(email)})
        portfolio = mongo.db.portfolios.find_one({"email": str(email)})

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Missing data tracking
        missing_data = []

        # Check user fields
        if not user.get("first_name"):
            missing_data.append("First name is missing.")
        if not user.get("last_name"):
            missing_data.append("Last name is missing.")
        if not user.get("picture"):
            missing_data.append("Profile picture is missing.")

        # Check portfolio fields
        if not portfolio:
            missing_data.append("Portfolio data is missing.")
        else:
            if not portfolio.get("links") or len(portfolio["links"]) == 0:
                for link in portfolio.get("links", []):
                                    if not link.get("name") or not link.get("url"):
                                        missing_data.append(f"Link '{link.get('name', 'Unnamed')}' is missing a valid URL.")
            if not portfolio.get("skills") or len(portfolio["skills"]) == 0:
                missing_data.append("Skills are missing.")
            if not portfolio.get("links") or len(portfolio["links"]) == 0:
                missing_data.append("Links are missing.")
            if not portfolio.get("education") or len(portfolio["education"]) == 0:
                missing_data.append("Education details are missing.")
            if not portfolio.get("work_experience") or len(portfolio["work_experience"]) == 0:
                missing_data.append("Work experience details are missing.")
                

        # Determine profile completeness
        is_profile_complete = len(missing_data) == 0

        return jsonify({
            "profile_complete": is_profile_complete,
            "missing_data": missing_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.form.to_dict()  # Use form data for both text and file inputs
    required_fields = ["first_name", "last_name", "job_title", "phone_number",
                       "age", "email", "address", "description", "links", "password", "pseudonym"]

    # Validate required fields
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Get profile picture and files
    picture = request.files.get("picture")
    files = request.files.get("files")

    # Database instance
    mongo = PyMongo(current_app)
    db = mongo.db

    # Check for duplicate email
    if db.users.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already exists"}), 400

    # Check for duplicate pseudonym
    if db.users.find_one({"pseudonym": data["pseudonym"]}):
        return jsonify({"error": "Pseudonym already exists"}), 400

    # File upload handling
    upload_folder = os.path.join(current_app.root_path, "static/uploads")
    os.makedirs(upload_folder, exist_ok=True)

    picture_path = None
    if picture and allowed_file(picture.filename):
        picture_filename = secure_filename(
            f"{data['pseudonym']}_picture_{picture.filename}")
        picture_path = os.path.join(
            upload_folder, "pictures", picture_filename)
        os.makedirs(os.path.dirname(picture_path), exist_ok=True)
        picture.save(picture_path)
        db_picture_path = os.path.join(picture_filename)

    files_path = None
    if files and allowed_file(files.filename):
        files_filename = secure_filename(
            f"{data['pseudonym']}_files_{files.filename}")
        files_path = os.path.join(upload_folder, "files", files_filename)
        os.makedirs(os.path.dirname(files_path), exist_ok=True)
        files.save(files_path)
        db_files_path = os.path.join(files_filename)

    # Build user data
    user_data = {key: data[key] for key in data if key != "password"}
    user_data["picture"] = db_picture_path
    user_data["files"] = db_files_path

    # Add user to database
    try:
        user = User(**user_data)
        user.set_password(data["password"])
        db.users.insert_one(user.to_dict())
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@user_bp.route('/<email>', methods=['GET'])
def get_user(email):
    mongo = PyMongo(current_app)
    db = mongo.db

    try:
        user = db.users.find_one({"email": email})  # Query by email directly
        if user:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
            return jsonify({"user": user}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"error": "User not found"}), 404
# Route to get all users (GET request)


@user_bp.route('/list_users', methods=['GET'])
def list_users():
    mongo = PyMongo(current_app)
    db = mongo.db

    # Retrieve all users and convert their IDs to strings
    users = list(db.users.find())
    for user in users:
        user['_id'] = str(user['_id'])

    return jsonify({"users": users}), 200

# Upload profile photo


@user_bp.route('/upload_profile_pic/<user_id>', methods=['POST'])
def upload_profile_pic(user_id):
    mongo = PyMongo(current_app)
    db = mongo.db

    # Check if a file was submitted
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # If no file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Check if the file has an allowed extension
    if file and allowed_file(file.filename):
        # Fetch the user's username from the database
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Fallback if first_name doesn't exist
        username = user.get("first_name", "user")

        # Generate a new filename based on username and current date
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{username}_{current_date}.{file_extension}"

        # Secure the filename and save the file
        filename = secure_filename(new_filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Ensure the upload folder exists
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])

        file.save(file_path)

        # Store only the filename in the database
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_pic": filename}}  # Save the filename only
        )

        return jsonify({
            "message": "Profile picture uploaded successfully!",
            "picture": filename  # Return the filename only for use in URLs
        }), 200

    return jsonify({"error": "Invalid file format"}), 400


@user_bp.route('/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    mongo = PyMongo(current_app)
    db = mongo.db

    data = request.json

    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    try:
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )

        if result.matched_count:
            return jsonify({"message": "User profile updated successfully"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to upload files


@user_bp.route("/upload_files/<user_id>", methods=["POST"])
def upload_files(user_id):
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Rename file: pseudonym_date.extension
        mongo = PyMongo(current_app)
        db = mongo.db

        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get user's pseudonym to use in the file name
        pseudonym = user.get("pseudonym", "user")
        filename = secure_filename(f"{pseudonym}_files_{file.filename}")

        # Save file to uploads directory
        upload_folder = os.path.join(
            current_app.root_path, "static/uploads/files")
        # Ensure the directory exists
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Store only the filename in the database for files
        db.users.update_one({"_id": ObjectId(user_id)}, {
                            "$set": {"files": filename}})

        return jsonify({"message": "files uploaded successfully", "files": filename}), 200

    return jsonify({"error": "File type not allowed"}), 400

# Route for user registration









