from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from myapp.models import *
# Create your views here.

@api_view(['GET', 'POST'])
def api_users(request):
    if request.method == 'GET':
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def api_user(request, user_id):
    user = get_object_or_404(Users, user_id=user_id)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def api_bookings(request):
    if request.method == 'GET':
        booking = Bookings.objects.all()
        serializer = BookingsSerializer(booking, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BookingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
def api_booking(request, booking_id):
    booking = get_object_or_404(Bookings, booking_id=booking_id)
    if request.method == 'GET':
        serializer = BookingsSerializer(booking)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BookingsSerializer(booking, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        booking.delete()
        return Response(status=HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def api_fields(request):
    if request.method == 'GET':
        fields = Fields.objects.all()
        serializer = FieldsSerializer(fields, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = FieldsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def api_field(request, field_id):
    field = get_object_or_404(Fields, field_id=field_id)
    if request.method == 'GET':
        serializer = FieldsSerializer(field)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = FieldsSerializer(field, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        field.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        {"message": "User registered successfully"},
        status=status.HTTP_201_CREATED
        )

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = Users.objects.filter(email__iexact=email).first()

    if not user or not check_password(password, user.password_hash):
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_400_BAD_REQUEST
        )

    refresh = RefreshToken()
    refresh['user_id'] = user.user_id
    refresh['user_type'] = user.user_type

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_type": user.user_type
    })