from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from rest_framework.views import APIView
from datetime import datetime
from django.db.models import Q
from myproject import settings
from .serializers import AuthResponseSerializer, DeleteAccountSerializer, FieldImageSerializer, LoginDataSerializer, UserSerializer, BookingsSerializer, FieldsSerializer, LoginRequestSerializer, UserProfileSerializer, ReviewSerializer, RequestOTPSerializer, ResetPasswordWithOTPSerializer, FieldToggleStatusSerializer
from myapp.models import FieldImages, Users, Bookings, Fields, Review
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsOwner, IsPlayer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.core.mail import send_mail
import random
from myapp.models import PasswordResetOTP
from .serializers import RequestOTPSerializer, ResetPasswordWithOTPSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateAPIView

@extend_schema(
    request=UserSerializer,
    responses={201: AuthResponseSerializer},
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
        queryset = Bookings.objects.all()

        if user.is_authenticated and user.user_type == 'owner':
            queryset = queryset.filter(field__owner=user)
        else:
            queryset = queryset.filter(user=user)

        status_param = self.request.query_params.get('status', None)
        if status_param in ['pending', 'confirmed', 'cancelled']:
            queryset = queryset.filter(status=status_param)

        return queryset.order_by('-created_at')

    def get_permissions(self):
        if self.action == 'create':
            return [IsPlayer()]
        if self.action in ['accept', 'decline']:
            return [IsOwner()]
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

        from datetime import datetime
        t1 = datetime.combine(datetime.today(), start_time)
        t2 = datetime.combine(datetime.today(), end_time)
        
        duration_hours = (t2 - t1).total_seconds() / 3600

        if duration_hours <= 0:
            raise serializers.ValidationError("وقت الانتهاء يجب أن يكون بعد وقت البدء!")

        base_price = float(field.price_per_hour)
        
        if field.peak_start_time and field.peak_end_time and field.peak_price:
            peak_start_dt = datetime.combine(datetime.today(), field.peak_start_time)
            peak_end_dt = datetime.combine(datetime.today(), field.peak_end_time)
            
            overlap_start = max(t1, peak_start_dt)
            overlap_end = min(t2, peak_end_dt)
            
            if overlap_start < overlap_end:
                peak_duration = (overlap_end - overlap_start).total_seconds() / 3600
                off_peak_duration = duration_hours - peak_duration
                
                off_peak_rate = float(field.off_peak_price) if field.off_peak_price else base_price
                peak_rate = float(field.peak_price)
                
                calculated_total_price = (peak_duration * peak_rate) + (off_peak_duration * off_peak_rate)
            else:
                off_peak_rate = float(field.off_peak_price) if field.off_peak_price else base_price
                calculated_total_price = duration_hours * off_peak_rate
        else:
            calculated_total_price = duration_hours * base_price
    
        if field.membership_discount > 0:
            discount_percentage = float(field.membership_discount) / 100.0
            discount_amount = calculated_total_price * discount_percentage
            calculated_total_price -= discount_amount

        serializer.save(
            user=self.request.user, 
            total_price=calculated_total_price, 
            status='pending'
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        booking = self.get_object()
        
        if booking.status != 'pending':
            return Response({"detail": "لا يمكن تغيير حالة حجز غير معلق."}, status=status.HTTP_400_BAD_REQUEST)
            
        booking.status = 'confirmed'
        booking.save()
        return Response({"message": "تم قبول الحجز بنجاح.", "status": "confirmed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        booking = self.get_object()
        
        if booking.status != 'pending':
            return Response({"detail": "لا يمكن تغيير حالة حجز غير معلق."}, status=status.HTTP_400_BAD_REQUEST)
            
        booking.status = 'cancelled'
        booking.save()
        return Response({"message": "تم رفض الحجز بنجاح.", "status": "cancelled"}, status=status.HTTP_200_OK)

class FieldsViewSet(ModelViewSet):
    queryset = Fields.objects.all()
    serializer_class = FieldsSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.user_type == 'owner':
            return Fields.objects.filter(owner=user).order_by('-created_at')
        return Fields.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOwner()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        request=FieldToggleStatusSerializer,
        description="تغيير حالة الملعب (تشغيل/إيقاف). إذا كان الإجراء إيقاف، يجب إرسال نوع العطل وتفاصيله."
    )
    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        field = self.get_object()
        
        if field.is_active:
            serializer = FieldToggleStatusSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            maintenance_type = serializer.validated_data.get('maintenance_type')
            if not maintenance_type:
                return Response(
                    {"error": "يجب تحديد نوع العطل أو سبب إيقاف الملعب."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            field.is_active = False
            field.maintenance_type = maintenance_type
            field.maintenance_description = serializer.validated_data.get('maintenance_description', '')
            field.save()
            
            return Response({
                "message": "تم إيقاف الملعب بنجاح وتسجيل سبب العطل.",
                "is_active": field.is_active,
                "maintenance_type": field.maintenance_type,
                "maintenance_description": field.maintenance_description
            }, status=status.HTTP_200_OK)
            
        else:
            field.is_active = True
            field.maintenance_type = None
            field.maintenance_description = None
            field.save()
            
            return Response({
                "message": "تم إعادة تفعيل الملعب بنجاح وجعله متاحاً للحجز.",
                "is_active": field.is_active
            }, status=status.HTTP_200_OK)

class FieldImagesViewSet(ModelViewSet):
    queryset = FieldImages.objects.all()
    serializer_class = FieldImageSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsOwner()]
        return [permissions.AllowAny()]
    
class OwnerDashboardAPIView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        user = request.user

        today = timezone.localdate()
        seven_days_ago = today - timedelta(days=6) 

        owner_fields = Fields.objects.filter(owner=user)
        total_courts = owner_fields.count()

        owner_bookings = Bookings.objects.filter(field__in=owner_fields)

        pending_requests = owner_bookings.filter(status='pending').count()

        today_bookings = owner_bookings.filter(booking_date=today).count()

        weekly_bookings = owner_bookings.filter(
            booking_date__range=[seven_days_ago, today],
            status='confirmed'
        )
        earnings_this_week = weekly_bookings.aggregate(total=Sum('total_price'))['total'] or 0.0

        chart_data = []
        for i in range(7):
            current_day = seven_days_ago + timedelta(days=i)
            daily_total = weekly_bookings.filter(booking_date=current_day).aggregate(total=Sum('total_price'))['total'] or 0.0
            
            chart_data.append({
                "day": current_day.strftime("%a"),
                "revenue": float(daily_total)
            })

        return Response({
            "today_bookings": today_bookings,
            "earnings_this_week": float(earnings_this_week),
            "pending_requests": pending_requests,
            "total_courts": total_courts,
            "weekly_revenue_chart": chart_data
        }, status=status.HTTP_200_OK)
    
@extend_schema(request=RequestOTPSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    serializer = RequestOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    otp_code = str(random.randint(100000, 999999))
    
    PasswordResetOTP.objects.filter(email=email).delete()
    PasswordResetOTP.objects.create(email=email, otp=otp_code)
    
    subject = "كود إعادة تعيين كلمة المرور - ملاعبنا"
    message = f"كود التحقق الخاص بك هو: {otp_code}\nصالح لفترة محدودة، برجاء عدم مشاركته مع أحد."
    
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return Response({"message": "تم إرسال كود الـ OTP إلى بريدك الإلكتروني بنجاح."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(request=ResetPasswordWithOTPSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_with_otp(request):
    serializer = ResetPasswordWithOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    otp = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']
    
    otp_record = PasswordResetOTP.objects.filter(email=email, otp=otp).first()
    
    if not otp_record:
        return Response({"detail": "كود التحقق غير صحيح أو منتهي الصلاحية!"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = Users.objects.get(email=email)
    user.set_password(new_password)
    user.save()
    
    otp_record.delete()
    
    return Response({"message": "تم تغيير كلمة المرور بنجاح، يمكنك تسجيل الدخول الآن."}, status=status.HTTP_200_OK)

class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user
    
class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        field_id = self.request.query_params.get('field_id')
        if field_id:
            queryset = queryset.filter(field_id=field_id)
        return queryset
    
@extend_schema(
    request=DeleteAccountSerializer,
    description="حذف الحساب نهائياً باستخدام كلمة المرور الحالية. (تحذير: هذا الإجراء لا يمكن التراجع عنه)"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    serializer = DeleteAccountSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.delete() 
        return Response(
            {"message": "تم حذف الحساب وجميع البيانات المرتبطة به بنجاح."},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)