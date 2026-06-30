from rest_framework import serializers
from myapp.models import FieldImages, Users, Bookings, Fields, Review
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db.models import Avg, Q
from django.utils import timezone

Users = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False)

    class Meta:
        model = Users
        fields = ['id', 'full_name', 'username', 'email', 'password', 'phone_number', 'user_type', 'profile_image']

    def create(self, validated_data):

        email = validated_data['email']
        default_username = email.split('@')[0]
        username = validated_data.get('username', default_username)

        user = Users.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            user_type=validated_data.get('user_type', 'player')
        )

        if 'profile_image' in validated_data:
            user.profile_image = validated_data['profile_image']
            user.save()
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'id', 'username', 'full_name', 'email', 'phone_number', 
            'bio', 'profile_image', 
            'instagram_link', 'tiktok_link', 'facebook_link'
        ]
        read_only_fields = ['email']

class BookingsSerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source='user.full_name')
    player_image = serializers.ImageField(source='user.profile_image', read_only=True)
    field_name = serializers.ReadOnlyField(source='field.name')
    sport_type = serializers.ReadOnlyField(source='field.sport_type')
    
    duration = serializers.SerializerMethodField()

    def validate(self, attrs):
        field = attrs.get('field') 
        
        if field and not field.is_active:
            raise serializers.ValidationError(
                {"error": "عذراً، هذا الملعب مغلق حالياً ولا يمكن الحجز عليه."}
            )
            
        return super().validate(attrs)

    class Meta:
        model = Bookings
        fields = [
            'booking_id', 
            'user',
            'player_name', 
            'player_image', 
            'field', 
            'field_name', 
            'sport_type',  
            'booking_date', 
            'start_time', 
            'end_time', 
            'duration',     
            'total_price', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['status', 'user', 'total_price']

    def get_duration(self, obj):
        from datetime import datetime
        dt1 = datetime.combine(datetime.min, obj.start_time)
        dt2 = datetime.combine(datetime.min, obj.end_time)
        duration_hours = (dt2 - dt1).total_seconds() / 3600
        return duration_hours
    
class FieldImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldImages
        fields = ['image_id', 'field', 'image', 'is_main']
        extra_kwargs = {'field': {'required': False}}
        
class FieldsSerializer(serializers.ModelSerializer):
    field_images = FieldImageSerializer(many=True, read_only=True) 
    owner_name = serializers.ReadOnlyField(source='owner.full_name')
    owner = serializers.ReadOnlyField(source='owner.id')

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Fields
        fields = '__all__'

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        field = Fields.objects.create(**validated_data)
        
        for image in uploaded_images:
            FieldImages.objects.create(field=field, image=image)
            
        return field

class LoginDataSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_type'] = self.user.user_type
        data['full_name'] = self.user.full_name
        data['user_id'] = self.user.id
        return data

class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

class AuthResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserSerializer() 
    tokens = TokenSerializer()

class FieldToggleStatusSerializer(serializers.Serializer):
    maintenance_type = serializers.ChoiceField(
        choices=[('lights', 'عطل في الإضاءة'), ('turf', 'صيانة أرضية الملعب'), ('facilities', 'صيانة في المرافق'), ('periodic', 'صيانة دورية'), ('other', 'أخرى')],
        required=False
    )
    maintenance_description = serializers.CharField(required=False, allow_blank=True)

class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني غير مسجل لدينا!")
        return value

class ResetPasswordWithOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_image = serializers.ImageField(source='user.profile_image', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'field', 'user', 'user_name', 'user_image', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']

    def validate(self, attrs):
        user = self.context['request'].user
        field = attrs['field']

        if Review.objects.filter(user=user, field=field).exists():
            raise serializers.ValidationError("لقد قمت بتقييم هذا الملعب من قبل.")

        confirmed_bookings = Bookings.objects.filter(user=user, field=field, status='confirmed')
        
        if not confirmed_bookings.exists():
            raise serializers.ValidationError("عذراً، لا يمكنك تقييم ملعب لم تقم بحجزه مسبقاً.")

        current_date = timezone.localdate()
        current_time = timezone.localtime().time()

        past_bookings = confirmed_bookings.filter(
            Q(booking_date__lt=current_date) | 
            Q(booking_date=current_date, end_time__lte=current_time)
        )

        if not past_bookings.exists():
            raise serializers.ValidationError("عذراً، لا يمكنك تقييم الملعب إلا بعد انتهاء وقت الحجز الفعلي وممارسة اللعب.")

        return attrs
    
class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("كلمة المرور غير صحيحة.")
        return value