from rest_framework import serializers
from myapp.models import FieldImages, Users, Bookings, Fields
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import random


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['id', 'full_name', 'email', 'password', 'phone_number', 'user_type', 'profile_image']

    def create(self, validated_data):
        user = Users.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            user_type=validated_data.get('user_type', 'player')
        )
        return user

class BookingsSerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source='user.full_name')
    field_name = serializers.ReadOnlyField(source='field.name')

    class Meta:
        model = Bookings
        fields = [
            'booking_id', 
            'user',
            'player_name', 
            'field', 
            'field_name', 
            'booking_date', 
            'start_time', 
            'end_time', 
            'total_price', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['status', 'user', 'total_price']
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

    class Meta:
        model = Fields
        fields = '__all__'

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