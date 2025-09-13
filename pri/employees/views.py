from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from mongoengine.queryset.visitor import Q
from pymongo import MongoClient
from django.conf import settings
import os
from .models import Employee
from .serializers import EmployeeSerializer, EmployeeCreateSerializer

class EmployeeListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Employee.objects
        department = self.request.query_params.get('department', None)
        skill = self.request.query_params.get('skill', None)
        
        if department:
            queryset = queryset.filter(department=department)
        
        if skill:
            # Filter employees who have the specified skill
            queryset = queryset.filter(skills__in=[skill])
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Apply pagination manually since mongoengine doesn't support django pagination directly
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        employees = list(queryset.skip(start).limit(page_size))
        total_count = queryset.count()
        
        serializer = self.get_serializer(employees, many=True)
        
        return Response({
            'count': total_count,
            'results': serializer.data
        })

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'employee_id'
    
    def get_object(self):
        employee_id = self.kwargs[self.lookup_field]
        try:
            return Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            from django.http import Http404
            raise Http404("Employee not found")
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Allow partial updates by default
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def average_salary_view(request):
    """
    Calculate overall average salary using MongoDB aggregation
    """
    try:
        # Get the database name from the connection
        db_name = os.getenv('MONGO_DB_NAME', 'employee_db')
        
        # Get MongoDB client using the same connection as in models.py
        from mongoengine.connection import get_db
        db = get_db()
        collection = db['employees']
        
        # MongoDB aggregation pipeline
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'average_salary': {'$avg': '$salary'}
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        
        if result:
            average_salary = result[0]['average_salary']
        else:
            average_salary = 0
            
        return Response({
            'average_salary': average_salary
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_average_salary_view(request):
    """
    Calculate average salary for each department using MongoDB aggregation
    """
    try:
        # Get MongoDB client using the same connection as in models.py
        from mongoengine.connection import get_db
        db = get_db()
        collection = db['employees']
        
        # MongoDB aggregation pipeline to group by department and calculate average salary
        pipeline = [
            {
                '$group': {
                    '_id': '$department',
                    'average_salary': {'$avg': '$salary'},
                    'employee_count': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id': 1}  # Sort by department name
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        
        # Format the response
        department_salaries = []
        for item in result:
            department_salaries.append({
                'department': item['_id'],
                'avg_salary': round(item['average_salary'], 2),
            })
            
        return Response({
            'department_salaries': department_salaries
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
