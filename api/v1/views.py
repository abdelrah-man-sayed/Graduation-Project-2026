from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from rest_framework.views import APIView
from datetime import datetime
from django.db.models import Q

from myproject import settings
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
from django.core.mail import send_mail
import random
from myapp.models import PasswordResetOTP
from .serializers import RequestOTPSerializer, ResetPasswordWithOTPSerializer

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

    def get_queryset(self):
        user = self.request.user
        
        # إذا كان المستخدم مسجل دخول ونوعه صاحب ملعب (Owner)، يرى ملاعبه هو فقط
        if user.is_authenticated and user.user_type == 'owner':
            return Fields.objects.filter(owner=user).order_by('-created_at')
            
        # للاعبين أو الزوار (في حالة AllowAny)، يتم عرض جميع الملاعب
        return Fields.objects.all().order_by('-created_at')

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
    
class OwnerDashboardAPIView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        user = request.user
        # تحديد تواريخ اليوم وآخر 7 أيام
        today = timezone.localdate()
        seven_days_ago = today - timedelta(days=6) 

        # 1. إجمالي الملاعب (Total Courts)
        owner_fields = Fields.objects.filter(owner=user)
        total_courts = owner_fields.count()

        # استخراج كل حجوزات ملاعب هذا المالك
        owner_bookings = Bookings.objects.filter(field__in=owner_fields)

        # 2. الطلبات المعلقة (Pending Requests)
        pending_requests = owner_bookings.filter(status='pending').count()

        # 3. حجوزات اليوم (Today's Bookings)
        today_bookings = owner_bookings.filter(booking_date=today).count()

        # 4. أرباح هذا الأسبوع (Earnings This Week)
        # هنجمع الفلوس للحجوزات المؤكدة في آخر 7 أيام
        weekly_bookings = owner_bookings.filter(
            booking_date__range=[seven_days_ago, today],
            status='confirmed'
        )
        earnings_this_week = weekly_bookings.aggregate(total=Sum('total_price'))['total'] or 0.0

        # 5. بيانات الرسم البياني (Weekly Revenue Chart)
        # هنعمل لوب على آخر 7 أيام عشان نطلع ربح كل يوم لوحده
        chart_data = []
        for i in range(7):
            current_day = seven_days_ago + timedelta(days=i)
            daily_total = weekly_bookings.filter(booking_date=current_day).aggregate(total=Sum('total_price'))['total'] or 0.0
            
            chart_data.append({
                "day": current_day.strftime("%a"), # بيطبع اسم اليوم زي: Mon, Tue, Wed
                "revenue": float(daily_total)
            })

        # تجميع كل الداتا في رد واحد (Response)
        return Response({
            "today_bookings": today_bookings,
            "earnings_this_week": float(earnings_this_week),
            "pending_requests": pending_requests,
            "total_courts": total_courts,
            "weekly_revenue_chart": chart_data
        }, status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    serializer = RequestOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    # توليد كود عشوائي من 6 أرقام
    otp_code = str(random.randint(100000, 999999))
    
    # حفظ الكود في الداتا بيز (مسح الأكواد القديمة للإيميل ده أولاً)
    PasswordResetOTP.objects.filter(email=email).delete()
    PasswordResetOTP.objects.create(email=email, otp=otp_code)
    
    # إرسال الإيميل
    subject = "كود إعادة تعيين كلمة المرور - ملاعبنا"
    message = f"كود التحقق الخاص بك هو: {otp_code}\nصالح لفترة محدودة، برجاء عدم مشاركته مع أحد."
    
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return Response({"message": "تم إرسال كود الـ OTP إلى بريدك الإلكتروني بنجاح."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": "حدث خطأ أثناء إرسال الإيميل، برجاء المحاولة لاحقاً."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_with_otp(request):
    serializer = ResetPasswordWithOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    otp = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']
    
    # التأكد من صحة الكود
    otp_record = PasswordResetOTP.objects.filter(email=email, otp=otp).first()
    
    if not otp_record:
        return Response({"detail": "كود التحقق غير صحيح أو منتهي الصلاحية!"}, status=status.HTTP_400_BAD_REQUEST)
    
    # تغيير كلمة المرور للمستخدم
    user = Users.objects.get(email=email)
    user.set_password(new_password)
    user.save()
    
    # مسح الكود بعد الاستخدام الناجح
    otp_record.delete()
    
    return Response({"message": "تم تغيير كلمة المرور بنجاح، يمكنك تسجيل الدخول الآن."}, status=status.HTTP_200_OK)