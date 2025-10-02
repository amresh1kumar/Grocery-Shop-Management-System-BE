from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework import status,permissions
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db import IntegrityError



# Create your views here.

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

def get_tokens_for_user(user):
   if not user.is_active:
      raise AuthenticationFailed("User is not active")
   
   refresh = RefreshToken.for_user(user)
   return{
      'refresh': str(refresh),
      'access' : str(refresh.access_token),
   }

class UserInformationView(APIView):
   # permission_classes = [permissions.IsAuthenticated]  # ✅ Protected
   def get(self,request,id=None):
      if id:
         try:
            user=MyCustomUser.objects.get(pk=id)
            serializer = UserInfoSerializer(user)
            return Response(serializer.data ,status=200)
         except MyCustomUser.DoesNotExist:
            return Response({"error": f"User with id {id} not found"},status=404)
      else: 
         users=MyCustomUser.objects.all()
         serializer =UserInfoSerializer(users,many=True)
         return Response(serializer .data,status=200)

   def post(self, request):
      serializer = UserInfoSerializer(data=request.data)
      if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Success
      else:
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Invalid Data

   def put(self,request,id=None):
      try:
         user=MyCustomUser.objects.get(pk=id)
      except User.DoesNotExist:
         return Response({"error":"User not found"}, status=status.HTTP_404_NOT_FOUND)
         
      serializer=UserInfoSerializer(user,data= request.data,partial=True)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
   
   def delete(self,request,id=None):
      try:
         user=MyCustomUser.objects.get(pk=id)
         user.delete()
         return Response({"message":f'User with id {id} is deleted successfully'},status=status.HTTP_204_NO_CONTENT)
      except User.DoesNotExist:
         return Response({"error":"User 5 not found"},status=status.HTTP_404_NOT_FOUND)


class UserRegisterView(APIView):

   permission_classes = [AllowAny]  

   def post(self,request):
      serializer=UserInfoSerializer(data=request.data)
      if serializer.is_valid():
         user=serializer.save()
         tokens= get_tokens_for_user(user)
         return Response(
            {
               "message":"User registered successfully",
               "user":serializer.data,
               "tokens":tokens
               },status=status.HTTP_201_CREATED
         )
      else:
         # validation error (like duplicate email)
         return Response(
            {  "success":False,
               "message":"Registration failed",
               "error":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST
         )

   
from django.contrib.auth import get_user_model
User = get_user_model()

class UserLoginView(APIView):
   def post(self,request):
      email=request.data.get('email')
      password= request.data.get("password")

      try:
         user=User.objects.get(email=email)
      except User.DoesNotExist:
         return Response({"error":"Invalid credentials"},status=status.HTTP_401_UNAUTHORIZED)

      user = authenticate(username=user.username, password=password)

      if user is not None:
         refresh= RefreshToken.for_user(user)
         return Response({
               "message": "Login successful",
               "user": {
                  "id": user.id,
                  "username": user.username,
                  "email": user.email,
               },
               "tokens": {
                  "refresh": str(refresh),
                  "access": str(refresh.access_token),
               }
         })
      else:
         return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



