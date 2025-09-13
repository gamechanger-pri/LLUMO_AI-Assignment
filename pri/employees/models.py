from mongoengine import Document, StringField, FloatField, DateField, ListField, connect, signals
from django.conf import settings
import os
import uuid

# Connect to MongoDB
connect(
    db=os.getenv('MONGO_DB_NAME', 'employee_db'),
    host=os.getenv('MONGO_URI', 'mongodb://localhost:27017/employee_db')
)

def generate_employee_id():
    """Generate a unique employee ID in the format EMPXXXX"""
    # Count the number of existing employees and add 1
    count = Employee.objects.count()
    
    # Generate a unique ID with retry logic to handle race conditions
    max_attempts = 10
    for attempt in range(max_attempts):
        # Format the new ID with leading zeros
        employee_id = f"EMP{count + attempt + 1:04d}"
        
        # Check if this ID already exists
        if not Employee.objects(employee_id=employee_id).first():
            return employee_id
    
    # If all attempts fail, generate a UUID-based ID as fallback
    return f"EMP{uuid.uuid4().hex[:4].upper()}"

def set_employee_id(sender, document, **kwargs):
    """Signal handler to set employee_id before saving if not already set"""
    if not document.employee_id:
        document.employee_id = generate_employee_id()

class Employee(Document):
    employee_id = StringField(required=True, unique=True)
    name = StringField(required=True, max_length=100)
    department = StringField(required=True, max_length=100)
    salary = FloatField(required=True, min_value=0)
    joining_date = DateField(required=True)
    skills = ListField(StringField())
    
    meta = {
        'collection': 'employees',
        'indexes': [
            'employee_id',
            'department',
            'joining_date',
            'skills'
        ]
    }
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"

# Connect the signal handler to the Employee model
signals.pre_save.connect(set_employee_id, sender=Employee)
