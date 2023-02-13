from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import Employee

class EmployeeView(ViewSet):
    """Honey Rae api for employees"""
    def list(self, request):
        """Handle GET request for all employees
        Returns a json string representing an array of objects"""
        employees = Employee.objects.all() #employee variable is assigned to the queryset from the Employee table as a list of instances.
        serialized = EmployeeSerializer(employees, many=True) #serialized variable is assigned to the json string representation of a list of Employee instances
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET request for a single employee
        Returns a JSON string representing and employee object"""
        employee = Employee.objects.get(pk=pk)
        serialized = EmployeeSerializer(employee, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

class EmployeeSerializer(serializers.ModelSerializer): #Accepts a list of instances and passes them through the Employee class, converting them into objects, and then serializing them into a json string.
    """Serializes a list of instances into a json string"""
    class Meta:
        model = Employee
        fields = ('id','user','specialty','full_name')