from django.contrib import admin
from .models import Product
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Register the Product model
admin.site.register(Product)

# Use Django's built-in UserCreationForm for the admin
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

# Unregister the default User and re-register with the custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
