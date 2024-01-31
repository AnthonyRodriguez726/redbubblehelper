from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)  # Unique username
    email = db.Column(db.String(120), unique=True, nullable=False)  # User email
    password_hash = db.Column(db.String(128))  # Hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Account creation timestamp
    last_login = db.Column(db.DateTime)  # Timestamp for the last login
    is_active = db.Column(db.Boolean, default=True)  # Indicates if account is active
    is_admin = db.Column(db.Boolean, default=False)  # Indicates if user has admin privileges
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)  # User's subscriptions

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to User
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Subscription start date
    end_date = db.Column(db.DateTime, nullable=False)  # Subscription end date
    plan_type = db.Column(db.String(50), nullable=False)  # Type of subscription plan
    is_active = db.Column(db.Boolean, default=True)  # Indicates if the subscription is active
