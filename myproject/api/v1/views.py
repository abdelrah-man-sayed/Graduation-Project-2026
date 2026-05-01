from datetime import datetime
from django.db.models import Q
from .serializers import FieldImageSerializer, LoginDataSerializer, UserSerializer, BookingsSerializer, FieldsSerializer
from myapp.models import FieldImages, Users, Bookings, Fields
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .permissions import IsOwner, IsPlayer
from rest_framework_simplejwt.views import TokenObtainPairView


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "User created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginDataView(TokenObtainPairView):
    serializer_class = LoginDataSerializer

class UsersViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

class BookingsViewSet(ModelViewSet):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def get_queryset(self):
            user = self.request.user
            
            if user.user_type == 'owner':
                return Bookings.objects.filter(field__owner=user).order_by('-created_at')
            
            return Bookings.objects.filter(user=user).order_by('-created_at')

    def get_permissions(self):
        if self.action == 'create':
            return [IsPlayer()]
        
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        field = serializer.validated_data['field']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        booking_date = serializer.validated_data['booking_date']

        overlapping_bookings = Bookings.objects.filter(
            field=field,
            booking_date=booking_date,
        ).exclude(
            status='cancelled'
        ).filter(
            Q(start_time__lt=end_time, end_time__gt=start_time)
        )

        if overlapping_bookings.exists():
            raise serializers.ValidationError("هذا الملعب محجوز بالفعل في هذا التوقيت!")

        fmt = '%H:%M:%S'
        t1 = datetime.strptime(str(start_time), fmt)
        t2 = datetime.strptime(str(end_time), fmt)
        
        duration_hours = (t2 - t1).total_seconds() / 3600

        if duration_hours <= 0:
            raise serializers.ValidationError("وقت الانتهاء يجب أن يكون بعد وقت البدء!")

        calculated_total_price = float(field.price_per_hour) * duration_hours

        serializer.save(
            user=self.request.user, 
            total_price=calculated_total_price, 
            status='pending'
        )

class FieldsViewSet(ModelViewSet):
    queryset = Fields.objects.all()
    serializer_class = FieldsSerializer
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOwner()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class FieldImagesViewSet(ModelViewSet):
    queryset = FieldImages.objects.all()
    serializer_class = FieldImageSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsOwner()]
        return [permissions.AllowAny()]