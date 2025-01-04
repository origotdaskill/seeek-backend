from flask import Flask, jsonify, session
from flask_pymongo import PyMongo
from routes.portfolio import portfolio_bp, init_portfolio_routes
from routes.user import user_bp
from routes.profile import web_bp
import os
from flask_cors import CORS



# Create Flask app
app = Flask(__name__)
CORS(app)  # Allow all origins for development
app.config['SECRET_KEY'] = 'your_secret_key'

# Create a test request context
with app.test_request_context():
    # Now you can access the session object
    session['key'] = 'value'
    print(session['key'])  # Output: value
app.secret_key = 'secretkey'  # Replace with a unique and secure value

# Set the upload folder and allowed file extensions
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in a temporary filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True 
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', "pdf", "doc", "docx"}


# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    
# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
  

# Configure MongoDB URI
app.config["MONGO_URI"] = "mongodb+srv://oriwill22:root4202@cluster0.smqn4.mongodb.net/seeek?retryWrites=true&w=majority&appName=Cluster0"

# Initialize PyMongo with explicit client type
mongo = PyMongo(app, uri=app.config["MONGO_URI"])


# Test the connection
@app.route('/')
def index():
    try:
        # Force a simple database operation to test connection
        mongo.db.command('ping')
        return "Connected to MongoDB!"
    except Exception as e:
        return f"Failed to connect to MongoDB: {str(e)}"



# Register blueprint (Routes)
portfolio_bp = init_portfolio_routes(mongo)
app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(web_bp, url_prefix="/web")


if __name__ == "__main__":
    app.run(debug=True)
