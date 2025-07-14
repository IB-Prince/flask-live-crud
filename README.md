# Flask Live CRUD API

A RESTful API built with Flask and PostgreSQL for managing users with full CRUD operations.

## 🚀 Features

- **Create** new users
- **Read** all users or specific user by ID
- **Update** existing users
- **Delete** users
- **PostgreSQL** database integration
- **Docker** containerization
- **Input validation** and error handling
- **Users can now register, login** and access protected endpoints

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.12)
- **Database**: PostgreSQL 12
- **ORM**: SQLAlchemy
- **Containerization**: Docker & Docker Compose

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/test`  | Test route |
| GET    | `/users` | Get all users |
| POST   | `/users` | Create a new user |
| GET    | `/users/<id>` | Get user by ID |
| PUT    | `/users/<id>` | Update user by ID |
| DELETE | `/users/<id>` | Delete user by ID |

## 🏃‍♂️ Quick Start

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd flask-live-crud
```

2. **Start the application:**
```bash
docker compose up
```

3. **Access the API:**
- Base URL: `http://localhost:4000`
- Test endpoint: `http://localhost:4000/test`

### API Usage Examples

#### Create a User
```bash
curl -X POST http://localhost:4000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com"}'
```

#### Get All Users
```bash
curl -X GET http://localhost:4000/users
```

#### Update a User
```bash
curl -X PUT http://localhost:4000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"username": "john_updated", "email": "john_new@example.com"}'
```

#### Delete a User
```bash
curl -X DELETE http://localhost:4000/users/1
```

## 🗄️ Database

The application uses PostgreSQL with the following configuration:
- **Database**: `flask_live_crud`
- **User**: `prince`
- **Password**: `prince`
- **Port**: `5432`

## 🐳 Docker

The application is fully containerized with Docker Compose:
- **Flask App**: Runs on port 4000
- **PostgreSQL**: Runs on port 5432
- **Health checks**: Ensures database is ready before starting the app

## 🔧 Development

### Local Development Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export DB_URL=postgresql://prince:prince@localhost:5432/flask_live_crud
```

3. **Run the application:**
```bash
python app.py
```

## 📦 Deployment

This application is ready for deployment on platforms like:
- Heroku
- Render
- Railway
- AWS
- Google Cloud Platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.