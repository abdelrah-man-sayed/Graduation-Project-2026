from .serializers import UserSerializer, BookingsSerializer, FieldsSerializer
from myapp.models import Users, Bookings, Fields
from rest_framework.viewsets import ModelViewSet

class UsersViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

class BookingsViewSet(ModelViewSet):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer
        
class FieldsViewSet(ModelViewSet):
    queryset = Fields.objects.all()
    serializer_class = FieldsSerializer
    