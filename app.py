import time
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

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

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

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
    return make_response(jsonify({'status': 'healthy', 'service': 'flask-crud-api'}), 200)

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
    
if __name__ == '__main__':
    # Use Railway's PORT environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
