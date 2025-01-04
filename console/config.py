import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Connection URI
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://oriwill22:root4202@cluster0.smqn4.mongodb.net/portfolio_db?retryWrites=true&w=majority&appName=Cluster0")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
