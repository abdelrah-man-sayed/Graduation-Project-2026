from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import UserSerializer, BookingsSerializer, FieldsSerializer
from myapp.models import Users, Bookings, Fields

class ApiUsers(ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
        
class ApiUser(RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

class ApiBookings(ListCreateAPIView):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

class ApiBooking(RetrieveUpdateDestroyAPIView):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer
        
class ApiFields(ListCreateAPIView):
    queryset = Fields.objects.all()
    serializer_class = FieldsSerializer

class ApiField(RetrieveUpdateDestroyAPIView):
    queryset = Fields.objects.all()
    serializer_class = FieldsSerializer
    