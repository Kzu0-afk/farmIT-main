from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FarmerUser


@admin.register(FarmerUser)
class FarmerUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            'Farmer Details',
            {
                'fields': (
                    'location',
                    'contact_number',
                )
            },
        ),
    )
    list_display = (
        'username',
        'email',
        'location',
        'contact_number',
        'is_active',
        'is_staff',
    )


