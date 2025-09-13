# Employee Management API

A Django REST Framework API for managing employee data with MongoDB as the database backend.

## Features

- CRUD operations for employees
- JWT authentication for protected routes
- Query employees by department
- Search employees by skill
- Calculate average salary using MongoDB aggregation
- Pagination support
- Schema validation
- MongoDB indexing for performance

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   MONGO_DB_NAME=employee_db
   MONGO_URI=mongodb://localhost:27017/employee_db
   SECRET_KEY=your-secret-key-here-change-in-production
   DEBUG=True
   JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Employee Management
- `GET /api/employees/` - List all employees (with pagination)
- `POST /api/employees/` - Create a new employee
- `GET /api/employees/{employee_id}/` - Get employee by ID
- `PUT /api/employees/{employee_id}/` - Update employee by ID
- `PATCH /api/employees/{employee_id}/` - Partial update employee by ID
- `DELETE /api/employees/{employee_id}/` - Delete employee by ID
- `GET /api/employees/?department={department}` - List employees by department
- `GET /api/employees/?skill={skill}` - List employees by skill
- `GET /api/employees/avg-salary/` - Get overall average salary of all employees
- `GET /api/employees/department-avg-salary/` - Get average salary for each department
- `GET /api/employees/department-avg-salary/` - Get average salary for each department

## Employee Schema

```json
{
  "employee_id": "string (unique)",
  "name": "string",
  "department": "string",
  "salary": "number",
  "joining_date": "date",
  "skills": ["string"]
}
```

## Environment Variables

- `MONGO_DB_NAME`: MongoDB database name
- `MONGO_URI`: MongoDB connection URI
- `SECRET_KEY`: Django secret key
- `DEBUG`: Django debug mode
- `JWT_SECRET_KEY`: JWT secret key

## Requirements

- Python 3.8+
- Django 5.2+
- MongoDB