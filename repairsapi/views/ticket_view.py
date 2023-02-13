from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer

class TicketView(ViewSet):
    """Handles HTTP requests to the ServiceTicket table"""
    def list(self, request):
        """Handles GET requests and queries the database for all rows in the service ticket table and 
        returns a json serialized string representing a list of ServiceTicket instances and a 200 status code"""
        service_tickets=[]
        ticket_description = None
        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = service_tickets.filter(date_completed__isnull=False)
                elif request.query_params['status'] == "all":
                    pass
                elif request.query_params['status'] == "unclaimed":
                    service_tickets = service_tickets.filter(date_completed__isnull=True, employee_id__isnull=True)
                elif request.query_params['status'] == "inprogress":
                    service_tickets = service_tickets.filter(date_completed__isnull=True, employee_id__isnull=False)
            if "description" in request.query_params:
                ticket_description = request.query_params['description']
                service_tickets = service_tickets.filter(description__contains = ticket_description)

        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user) # service_tickets is assigned to the queryset from the serviceticket table as a list of ServiceTicket instances
        serialized = TicketSerializer(service_tickets, many=True) # serialized is assigned to the json serialized string representation of a list of ServiceTicket instances
        return Response(serialized.data, status=status.HTTP_200_OK) # returns a response serialized and assigns a 200 status code

    def retrieve(self, request, pk=None):
        """Handles GET requests and queries the database for a singular row in the service ticket table that
        matches the primary key (pk) and returns a json serialized string representing an instance of 
        ServiceTicket and a 200 status code"""
        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Handles POST requests to insert a new row into the database under the ServiceTicket table, creates 
        an instance of the ServiceTicket model, serializes this instance, and returns the 
        serialized json string as a Response instance with a status code of 201"""
        ticket = ServiceTicket()
        ticket.customer = Customer.objects.get(user=request.auth.user)
        ticket.description = request.data['description']
        ticket.emergency = request.data['emergency']
        ticket.save()

        serialized = TicketSerializer(ticket, many=False)

        return Response(serialized.data, status = status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Handles PUT requests to the ServiceTicket table"""
        ticket = ServiceTicket.objects.get(pk=pk)

        if ticket.employee is None:
            employee_id = request.data['employee']
            assigned_employee = Employee.objects.get(pk = employee_id)
            ticket.employee = assigned_employee

        if ticket.date_completed is None:
            date = request.data['date_completed']
            ticket.date_completed = date
        ticket.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handles DELETE requests"""
        ServiceTicket.objects.get(pk=pk).delete()
        return Response(None, status = status.HTTP_204_NO_CONTENT)
        
#serializes the specific instance of 
class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=('id', 'full_name')

class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Employee
        fields=('id','specialty','full_name')

class TicketSerializer(serializers.ModelSerializer):
    customer = TicketCustomerSerializer(many=False)
    employee = TicketEmployeeSerializer(many=False)
    class Meta:
        model = ServiceTicket
        fields = ('id','customer', 'employee', 'description', 'emergency', 'date_completed',)
        depth = 1