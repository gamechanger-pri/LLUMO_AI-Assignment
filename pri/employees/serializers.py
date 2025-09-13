from rest_framework import serializers
from .models import Employee, generate_employee_id
from datetime import date

class EmployeeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    employee_id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100)
    salary = serializers.FloatField()
    joining_date = serializers.DateField()
    skills = serializers.ListField(child=serializers.CharField())
    
    def create(self, validated_data):
        # Generate employee ID before creating the employee
        employee_id = generate_employee_id()
        validated_data['employee_id'] = employee_id
        return Employee.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def validate_salary(self, value):
        if value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value
    
    def validate_joining_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Joining date cannot be in the future")
        return value
    
    def validate_skills(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Skills must be a list of strings")
        for skill in value:
            if not isinstance(skill, str):
                raise serializers.ValidationError("Each skill must be a string")
        return value

class EmployeeCreateSerializer(EmployeeSerializer):
    # Override fields to make employee_id not required for creation
    employee_id = serializers.CharField(read_only=True, required=False)