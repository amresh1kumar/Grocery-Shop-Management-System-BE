from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class MyCustomUser(AbstractUser):
   roles=(
      ('admin','Admin'),
      ('staff','Staff')
   )
   email = models.EmailField(unique=True)
   contact_number= models.CharField(max_length=13,blank=True,null=True)
   role = models.CharField(max_length=50, choices=roles,default='staff')
   address= models.TextField(blank=True, null=True)

   def save(self,*args,**kwargs):
      if self.is_superuser==True:
         self.role="admin"
      super().save(*args,**kwargs)

#product list model
class productStockModel(models.Model):
   item_name= models.CharField(max_length=50)
   item_qty= models.CharField(max_length=50)
   item_price= models.CharField(max_length=50)
   item_category= models.CharField(max_length=50)

class CustomerInformation(models.Model):
   customer_name= models.CharField(max_length=50)
   customer_contact_no= models.CharField(max_length=12,unique=True)
