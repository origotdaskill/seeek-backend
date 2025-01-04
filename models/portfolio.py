from datetime import datetime

class Portfolio:
    def __init__(self, email, skills, work_experience, education , links ):
        self.email = email  # User ID to associate portfolio with the user
        self.skills = skills  # List of skills (strings or dictionaries)
        self.work_experience = work_experience  # List of work experiences (dictionaries)
        self.education = education  # List of education details (dictionaries)
        self.links = links 
        
    def to_dict(self):
        """Converts the Portfolio object to a dictionary for MongoDB"""
        return {
            "email": self.email,  # Store the User ID in the portfolio
            "skills": self.skills,
            "work_experience": self.work_experience,
            "education": self.education,
            "links" : self.links, 
            "created_at": datetime.utcnow()  # Add creation timestamp
        }
