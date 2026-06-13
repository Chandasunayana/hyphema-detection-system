from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reports = db.relationship('Report', backref='user', lazy=True)
    vision_reports = db.relationship('VisionReport', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Image paths
    original_image = db.Column(db.String(500))
    heatmap_image = db.Column(db.String(500))
    
    # Results
    prediction = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    severity_grade = db.Column(db.Integer)
    severity_label = db.Column(db.String(50))
    
    # Additional info
    recommendation = db.Column(db.Text)
    vision_score = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'prediction': self.prediction,
            'confidence': f"{self.confidence*100:.1f}%" if self.confidence else "N/A",
            'severity': self.severity_label,
            'original_image': self.original_image,
            'heatmap_image': self.heatmap_image,
            'recommendation': self.recommendation
        }

class VisionReport(db.Model):
    __tablename__ = 'vision_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    left_eye_score = db.Column(db.String(20))
    right_eye_score = db.Column(db.String(20))
    interpretation = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hospital_name = db.Column(db.String(200))
    hospital_id = db.Column(db.String(50))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    patient_name = db.Column(db.String(100))
    patient_email = db.Column(db.String(120))
    patient_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)