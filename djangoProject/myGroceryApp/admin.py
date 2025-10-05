from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin #i importred

# Register your models here.
class CustomUserAdmin(UserAdmin):
      model = MyCustomUser
      list_display = ['username', 'email', 'contact_number', 'is_staff', 'is_active', 'role', 'address']
      search_fields = ['username', 'email', 'contact_number']
      ordering = ['username']

      fieldsets = (
            (None, {'fields': ('username', 'password')}),
            ('Personal info', {
                  'fields': ('first_name', 'last_name', 'email', 'contact_number', 'role', 'address')
            }),
            ('Permissions', {
                  'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
            }),
            ('Important dates', {'fields': ('last_login', 'date_joined')}),
      )

admin.site.register(MyCustomUser, CustomUserAdmin)

admin.site.register(productStockModel)
