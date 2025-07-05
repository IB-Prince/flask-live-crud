import time
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration
db_url = os.getenv('DB_URL') or os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
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
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            db_url = os.getenv('DB_URL') or os.getenv('DATABASE_URL')
            engine = create_engine(db_url)
            conn = engine.connect()
            conn.close()
            return True
        except OperationalError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise

# Wait for the database and create tables
wait_for_db()

with app.app_context():
    db.create_all()
    
#create a test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'Flask CRUD API is running!'}), 200)

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
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port, debug=False)
    