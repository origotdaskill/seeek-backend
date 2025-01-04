from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # For hashing passwords

class User:
    def __init__(self, first_name, last_name, job_title, phone_number, age, email, address, description, links, pseudonym, picture, files ,password=None):
        self.first_name = first_name
        self.last_name = last_name
        self.job_title = job_title
        self.phone_number = phone_number
        self.age = age
        self.email = email
        self.address = address
        self.description = description
        self.picture = picture 
        self.files = files 
        self.links = links  # Social links should be stored as a dictionary
        self.pseudonym = pseudonym  # New field
        self.password = password  # Password should be stored as plain text for hashing

    def set_password(self, password):
        """Hashes the password before storing it"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the password matches the hashed one"""
        return check_password_hash(self.password, password)

    def to_dict(self):
        """Converts the User object to a dictionary for MongoDB"""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "job_title": self.job_title,
            "phone_number": self.phone_number,
            "age": self.age,
            "email": self.email,
            "address": self.address,
            "description": self.description,
            "links": self.links,
            "picture": self.picture, 
            "files": self.files,
            "pseudonym": self.pseudonym,  # Include pseudonym
            "password": self.password,  # Store the hashed password in MongoDB
            "created_at": datetime.utcnow()  # Add creation timestamp
        }
