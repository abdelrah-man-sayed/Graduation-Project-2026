from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from .serializers import UserSerializer, BookingsSerializer, FieldsSerializer
from myapp.models import Users, Bookings, Fields

class ApiUsers(APIView):
    def get(self, request):
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# @api_view(['GET', 'POST'])
# def api_users(request):
#     if request.method == 'GET':
        
#     elif request.method == 'POST':
        
class ApiUser(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(Users, user_id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    def put(self, request, user_id):
        user = get_object_or_404(Users, user_id=user_id)
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, user_id):
        user = get_object_or_404(Users, user_id=user_id)
        user.delete()
        return Response(status=HTTP_204_NO_CONTENT)

# @api_view(['GET', 'PUT', 'DELETE'])
# def api_user(request, user_id):
#     user = get_object_or_404(Users, user_id=user_id)
#     if request.method == 'GET':
        
#     elif request.method == 'PUT':
        
#     elif request.method == 'DELETE':
#         user.delete()
#         return Response(status=HTTP_204_NO_CONTENT)

class ApiBookings(APIView):
    def get(self, request):
        booking = Bookings.objects.all()
        serializer = BookingsSerializer(booking, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = BookingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# @api_view(['GET', 'POST'])
# def api_bookings(request):
#     if request.method == 'GET':
        
#     elif request.method == 'POST':
        
class ApiBooking(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(Bookings, booking_id=booking_id)
        serializer = BookingsSerializer(booking)
        return Response(serializer.data)
    def post(self, request, booking_id):
        booking = get_object_or_404(Bookings, booking_id=booking_id)
        serializer = BookingsSerializer(booking, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, user_id, booking_id):
        booking = get_object_or_404(Bookings, booking_id=booking_id)
        booking.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    
# @api_view(['GET', 'PUT', 'DELETE'])
# def api_booking(request, booking_id):
#     booking = get_object_or_404(Bookings, booking_id=booking_id)
#     if request.method == 'GET':
        
#     elif request.method == 'PUT':
        
#     elif request.method == 'DELETE':
        
class ApiFields(APIView):
    def get(self, request):
        fields = Fields.objects.all()
        serializer = FieldsSerializer(fields, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = FieldsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# @api_view(['GET', 'POST'])
# def api_fields(request):
#     if request.method == 'GET':
        
#     elif request.method == 'POST':
        
class ApiField(APIView):
    def get(self, request, field_id):
        field = get_object_or_404(Fields, field_id=field_id)
        serializer = FieldsSerializer(field)
        return Response(serializer.data)
    def post(self, request, field_id):
        field = get_object_or_404(Fields, field_id=field_id)
        serializer = FieldsSerializer(field, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, user_id, field_id):
        field = get_object_or_404(Fields, field_id=field_id)
        field.delete()
        return Response(status=HTTP_204_NO_CONTENT)

# @api_view(['GET', 'PUT', 'DELETE'])
# def api_field(request, field_id):
#     field = get_object_or_404(Fields, field_id=field_id)
#     if request.method == 'GET':
#         serializer = FieldsSerializer(field)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = FieldsSerializer(field, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         field.delete()
#         return Response(status=HTTP_204_NO_CONTENT)
    