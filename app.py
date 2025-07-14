import time
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, flash, redirect, url_for
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

app = Flask(__name__)

# Database configuration for Railway
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Fix Heroku/Railway postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"🔗 Using DATABASE_URL: {database_url[:50]}...")
else:
    # Fallback for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallback.db'
    print("⚠️ No DATABASE_URL found, using SQLite fallback")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key-for-development')  # Change in production

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=True)

    def json(self):
        return {
            'id':self.id,
            'username': self.username,
            'email': self.email
        }
    
# Removed wait_for_db function to speed up startup

# Initialize database in a safer way for Railway
print("🚀 Starting Flask application...")
try:
    with app.app_context():
        # Try to create tables, but don't fail if database is not available
        db.create_all()
        print("✅ Database tables created successfully!")
except Exception as e:
    print(f"⚠️ Database initialization failed: {e}")
    print("⚠️ Starting without database connection - health endpoint will still work")
    
#create a test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'Flask CRUD API is running!'}), 200)

# Health check endpoint that doesn't require database
@app.route('/health', methods=['GET'])
def health():
    try:
        return jsonify({"status": "healthy", "timestamp": time.time()}), 200
    except Exception as e:
        print(f"Health check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# create a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Validate input data
        if not data or 'username' not in data or 'email' not in data:
            return make_response(jsonify({'message': 'username and email are required'}), 400)
        
        new_user = User(username=data['username'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message': 'user created'}), 201)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'message': 'error creating user'}), 500)

# get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(jsonify({'users': [user.json() for user in users]}), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting users'}), 500)
    
# get a user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting user'}), 500)

# update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            
            # Validate input data
            if not data or 'username' not in data or 'email' not in data:
                return make_response(jsonify({'message': 'username and email are required'}), 400)
            
            user.username = data['username']
            user.email = data['email']
            db.session.commit()
            return make_response(jsonify({'message': 'user updated'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'message': 'error updating user'}), 500)
    
# delete a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'message': 'error deleting user'}), 500)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users-page')
def users_page():
    return render_template('users.html')

@app.route('/docs')
def docs():
    """API Documentation endpoint"""
    api_docs = {
        "title": "Flask CRUD API",
        "version": "1.0.0",
        "description": "A RESTful API for managing users",
        "endpoints": {
            "GET /test": "Test API connection",
            "GET /users": "Get all users",
            "POST /users": "Create a new user",
            "GET /users/{id}": "Get user by ID",
            "PUT /users/{id}": "Update user by ID",
            "DELETE /users/{id}": "Delete user by ID"
        },
        "example_user": {
            "username": "john_doe",
            "email": "john@example.com"
        }
    }
    return jsonify(api_docs)

@app.route('/users/<int:user_id>/detail')
def user_detail(user_id):
    """Display detailed view of a specific user"""
    return render_template('user_detail.html', user_id=user_id)

# Authentication routes
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({"error": "Username, email, and password are required"}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 409
        
        hashed_pw = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'], 
            email=data['email'], 
            password=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password are required"}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password and check_password_hash(user.password, data['password']):
            token = create_access_token(identity=user.username)
            return jsonify({
                "access_token": token, 
                "message": "Login successful",
                "user": user.json()
            }), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    if user:
        return jsonify(user=user.json()), 200
    return jsonify({"error": "User not found"}), 404

# Update an existing route to require authentication
@app.route('/protected-data', methods=['GET'])
@jwt_required()
def protected_data():
    current_username = get_jwt_identity()
    return jsonify({
        "message": f"This is protected data for {current_username}",
        "timestamp": time.time()
    }), 200

@app.route('/login-page')
def login_page():
    """Render the login page"""
    return render_template('login.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

# Removed CLI command that used raw SQL - not compatible with Railway

with app.app_context():
    try:
        # Create all tables if they don't exist
        db.create_all()
        print("Database tables created/verified!")
    except Exception as e:
        print(f"Database setup error: {e}")
        # Continue anyway - don't crash the app

if __name__ == '__main__':
    print("🚀 Starting Flask app directly...")
    port = int(os.environ.get('PORT', 8080))
    print(f"🔗 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    print("🚀 Flask app loaded for gunicorn...")
    print(f"🔗 Environment variables: PORT={os.getenv('PORT')}, DATABASE_URL={bool(os.getenv('DATABASE_URL'))}")
