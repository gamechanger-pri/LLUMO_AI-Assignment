from django.urls import path
from .views import EmployeeListCreateView, EmployeeDetailView, department_average_salary_view

urlpatterns = [
    path('employees/avg-salary/', department_average_salary_view, name='average-salary'),
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<str:employee_id>/', EmployeeDetailView.as_view(), name='employee-detail'),
]