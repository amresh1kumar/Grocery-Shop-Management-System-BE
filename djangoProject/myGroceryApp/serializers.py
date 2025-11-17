from rest_framework import serializers
from .models import *

#for abstract user
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
User= get_user_model()

class UserInfoSerializer(serializers.ModelSerializer):
   email = serializers.EmailField(
      required=True,
      validators=[UniqueValidator(queryset=User.objects.all())]  # 👈 email must be unique
   )
   class Meta:
      model = User
      # fields= '__all__' #for show all fields
      fields = ['id', 'username', 'email', 'password',
                  'first_name', 'last_name', 'address',
                  'contact_number','role','is_staff', 'is_active', 'is_superuser'] #to show specific fields

      extra_kwargs={
         'password':{'write_only':True}
      }

   # Email uniqueness validation
   def validate_email(self, value):
      if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
      return value   

   #for create or post karne pe password hash ho aur fields dikhe fill karne pe
   def create(self, validated_data):
      user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            address=validated_data.get('address',''),
            contact_number=validated_data.get('contact_number',''),
            role=validated_data.get('role','')
      )
      user.is_staff = validated_data.get('is_staff', False)
      user.is_active = validated_data.get('is_active', True)   # default True
      user.is_superuser = validated_data.get('is_superuser', False)
      
      # 👇 Force role based on superuser
      if user.is_superuser:
         user.role = "admin"
         user.is_staff = True   # admin always staff bhi hota hai
      else:
         user.role = "staff"

      user.save()
      return user   
   

   #for  update karne pe password hash ho aur fields dikhe fill karne pe
   def update(self, instance, validated_data):
      instance.username = validated_data.get('username', instance.username)
      instance.email = validated_data.get('email', instance.email)
      instance.first_name = validated_data.get('first_name', instance.first_name)
      instance.last_name = validated_data.get('last_name', instance.last_name)
      instance.address = validated_data.get('address', instance.address)
      instance.contact_number = validated_data.get('contact_number', instance.contact_number)

      # Staff / Superuser / Active flags update
      instance.is_staff = validated_data.get('is_staff', instance.is_staff)
      instance.is_active = validated_data.get('is_active', instance.is_active)
      instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)

      # Role handling
      if instance.is_superuser:
         instance.role = "admin"
         instance.is_staff = True
      else:
         instance.role = "staff"

      # Password agar diya gaya hai to hash karke save karna
      password = validated_data.get('password', None)
      if password:
         instance.set_password(password)  # hash karega

      instance.save()
      return instance
   

#product list serilizer

class productStockSerializer(serializers.ModelSerializer):
   class Meta:
      model=productStockModel
      fields='__all__'


class CustomerInformationSerializer(serializers.ModelSerializer):
   class Meta:
      model = CustomerInformation
      fields = "__all__"      