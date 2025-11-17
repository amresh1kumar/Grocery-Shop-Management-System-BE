from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework import status,permissions
from django.contrib.auth import authenticate
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser


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


#product list view 

class productStockView(APIView):
   # permission_classes = [permissions.IsAuthenticated]  # ✅ Protected

   def get(self, request, id=None):
      if id:  
            # item = productStockModel.objects.get(pk=id) # Agar id exist nahi karti to ye DoesNotExist exception dega.
            
            item = get_object_or_404(productStockModel, pk=id) # Ye bhi same kaam karta hai lekin agar id exist nahi karti to ye 404 response dega.

            serializer = productStockSerializer(item)
            return Response(serializer.data)
      else:
            # Get query params
            category = request.GET.get("item_category", "").strip() # strip to remove extra spaces
            items = productStockModel.objects.all()

            # Apply filters if query params exist
            if category:
               items = items.filter(item_category__icontains=category) #icontains for case insensitive matching chahe uppercase/lowercase ho, sab match karega.
            serializer = productStockSerializer(items, many=True)
            return Response(serializer.data)
      
# Get all items      http://127.0.0.1:8000/productList/`                                    
# Filter by category http://127.0.0.1:8000/productList/?item_category=Fruits              
# Filter by name     http://127.0.0.1:8000/productList/?item_name=Rice  
# Filter by both     http://127.0.0.1:8000/productList/?item_name=Apple&item_category=Fruits


   def post(self,request):
      serializer= productStockSerializer(data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      
   # def put(self,request,id=None):
      old_item=productStockModel.objects.get(pk=id)
      

      new_qty = request.data.get("item_qty")

      if new_qty is not None:
         try:
            new_qty = int(new_qty)
         except:
            return Response({"error": "Quantity must be a number"}, status=400)

         if new_qty < 0:
            return Response(
               {"error": "Not enough stock"},
               status=400
            )

      serializer =productStockSerializer(old_item, data=request.data , partial=True)
      if serializer .is_valid():
         serializer .save()
         return Response(serializer.data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
   def put(self, request, id=None):
      old_item = productStockModel.objects.get(pk=id)

      reduce_qty = request.data.get("reduce_qty")

      if reduce_qty is not None:
         try:
               reduce_qty = int(reduce_qty)
         except:
               return Response({"error": "Quantity must be a number"}, status=400)

         # Convert old stock to int
         try:
               old_qty = int(old_item.item_qty)
         except:
               return Response({"error": "Stored stock is not a valid number"}, status=400)

         # Calculate new stock
         new_qty = old_qty - reduce_qty

         if new_qty < 0:
               return Response({"error": "Not enough stock"}, status=400)

         # Save updated stock
         old_item.item_qty = new_qty
         old_item.save()

         return Response({
               "message": "Stock updated successfully",
               "new_stock": new_qty
         })

      serializer = productStockSerializer(old_item, data=request.data, partial=True)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)

      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   def delete(self,request,id=None):
      item= productStockModel.objects.get(pk=id)
      item.delete()
      return Response({"message": "Item deleted successfully!"})
   



class CustomerInformationView(APIView):

    # 🔹 GET All + GET by ID
    def get(self, request, pk=None):
        if pk:
            customer = get_object_or_404(CustomerInformation, pk=pk)
            serializer = CustomerInformationSerializer(customer)
            return Response(serializer.data)

        customers = CustomerInformation.objects.all()
        serializer = CustomerInformationSerializer(customers, many=True)
        return Response(serializer.data)

    # 🔹 POST - Create
    def post(self, request):
        serializer = CustomerInformationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 PUT - Update
    def put(self, request, pk):
        customer = get_object_or_404(CustomerInformation, pk=pk)
        serializer = CustomerInformationSerializer(customer, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 DELETE
    def delete(self, request, pk):
        customer = get_object_or_404(CustomerInformation, pk=pk)
        customer.delete()
        return Response({"message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
