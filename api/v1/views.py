from datetime import datetime
from django.db.models import Q
from .serializers import AuthResponseSerializer, FieldImageSerializer, LoginDataSerializer, UserSerializer, BookingsSerializer, FieldsSerializer, LoginRequestSerializer
from myapp.models import FieldImages, Users, Bookings, Fields
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .permissions import IsOwner, IsPlayer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    request=UserSerializer,
    responses={201: AuthResponseSerializer}, # الرد في حالة إنشاء مستخدم جديد
    description="إنشاء حساب ويرجع معاه الـ Tokens فوراً"
)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    
    return Response({
        "message": "User created successfully",
        "user": serializer.data,
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)

@extend_schema(
    operation_id="custom_user_login",    
    request=LoginRequestSerializer,
    responses={200: AuthResponseSerializer},
    description="تسجيل دخول ويرجع معاه الـ Tokens"
)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        from rest_framework.exceptions import ValidationError
        raise ValidationError({"detail": "Email and password are required."})

    user = authenticate(username=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)
        
        return Response({
            "message": "Login successful",
            "user": serializer.data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    from rest_framework.exceptions import AuthenticationFailed
    raise AuthenticationFailed({"detail": "Invalid email or password."})

@extend_schema(
    request=LoginRequestSerializer,
    responses={200: AuthResponseSerializer},
    description="تسجيل الدخول والحصول على الـ Access والـ Refresh tokens"
)

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