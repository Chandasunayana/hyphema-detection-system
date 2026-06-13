import os

class Config:
    SECRET_KEY = 'your-secret-key-here-change-this'

    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "reports.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "uploads")
    HEATMAP_FOLDER = os.path.join(BASE_DIR, "static", "images", "heatmaps")
    REPORTS_FOLDER = os.path.join(BASE_DIR, "reports", "saved_reports")

    # Model
    MODEL_PATH = os.path.join(BASE_DIR, "model", "hyphema_model.h5")
    IMAGE_SIZE = (224, 224)

    # Severity grades
    SEVERITY_GRADES = {
        0: {"label": "Normal", "color": "green", "description": "Eye appears healthy"},
        1: {"label": "Mild", "color": "yellow", "description": "Minor bleeding detected"},
        2: {"label": "Moderate", "color": "orange", "description": "Moderate bleeding visible"},
        3: {"label": "Severe", "color": "red", "description": "Significant bleeding detected"},
        4: {"label": "Critical", "color": "darkred", "description": "Emergency - Immediate attention required"}
    }

# Create folders
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.HEATMAP_FOLDER, exist_ok=True)
os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)