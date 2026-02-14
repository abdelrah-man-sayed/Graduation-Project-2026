from rest_framework import serializers
from myapp.models import *
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'

class FieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = '__all__'
     
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['full_name', 'email', 'password_hash', 'user_type']

    def create(self, validated_data):
        validated_data['password_hash'] = make_password(
            validated_data['password_hash']
        )
        return super().create(validated_data)