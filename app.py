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

# Configuration
db_url = os.getenv('DB_URL')
if not db_url:
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Fix Heroku/Railway postgres:// to postgresql://
        db_url = database_url.replace('postgres://', 'postgresql://') if database_url.startswith('postgres://') else database_url

# If still no database URL, provide a fallback for Railway
if not db_url:
    # Check for Railway's automatic database variables
    railway_db_url = os.getenv('PGDATABASE')
    railway_db_host = os.getenv('PGHOST')
    railway_db_user = os.getenv('PGUSER')
    railway_db_password = os.getenv('PGPASSWORD')
    railway_db_port = os.getenv('PGPORT', '5432')
    
    if all([railway_db_host, railway_db_user, railway_db_password, railway_db_url]):
        db_url = f"postgresql://{railway_db_user}:{railway_db_password}@{railway_db_host}:{railway_db_port}/{railway_db_url}"
        print(f"🔧 Constructed database URL from Railway variables")

if not db_url:
    print("❌ No database configuration found!")
    # Don't fail completely, let the app start for health checks
    db_url = 'postgresql://dummy:dummy@localhost:5432/dummy'

print(f"🔗 Using database URL: {db_url[:50]}..." if db_url else "❌ No database URL found!")
print(f"🔍 Available environment variables: {[k for k in os.environ.keys() if 'PG' in k or 'DB' in k or 'DATABASE' in k]}")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
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
    
def wait_for_db():
    max_retries = 10  # Increased for Railway
    retry_delay = 3   # Reduced delay for faster startup

    print("🔄 Waiting for database connection...")
    for attempt in range(max_retries):
        try:
            db_url = os.getenv('DB_URL')
            if not db_url:
                database_url = os.getenv('DATABASE_URL')
                if database_url:
                    db_url = database_url.replace('postgres://', 'postgresql://') if database_url.startswith('postgres://') else database_url
            
            if not db_url:
                print("❌ No database URL found in environment variables")
                return False
                
            engine = create_engine(db_url)
            conn = engine.connect()
            conn.close()
            print(f"✅ Database connection successful on attempt {attempt + 1}")
            return True
        except OperationalError as e:
            print(f"❌ Database connection failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            print("❌ All database connection attempts failed")
            return False

# Wait for the database and create tables
print("🚀 Starting Flask application...")
db_connected = wait_for_db()

if db_connected:
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
else:
    print("⚠️ Starting without database connection - health endpoint will still work")
    
#create a test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'Flask CRUD API is running!'}), 200)

# Health check endpoint that doesn't require database
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

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

# Add this to your app.py if you need to update existing tables
@app.cli.command('update-db')
def update_db():
    """Add new columns to existing tables."""
    with app.app_context():
        try:
            # Try to add password column if it doesn't exist
            db.engine.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS password TEXT')
            print("Database updated successfully!")
        except Exception as e:
            print(f"Error updating database: {e}")

with app.app_context():
    try:
        # Check if we need to update tables
        inspector = db.inspect(db.engine)
        if 'users' in inspector.get_table_names() and 'password' not in inspector.get_columns('users'):
            db.engine.execute('ALTER TABLE users ADD COLUMN password TEXT')
            print("Added password column to users table")
        
        # Create all tables if they don't exist
        db.create_all()
        print("Database tables created/verified!")
    except Exception as e:
        print(f"Database migration check error: {e}")
        # Continue anyway - don't crash the app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
