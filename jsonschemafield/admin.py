from django.contrib import admin
from .models import UserInformation


@admin.register(UserInformation)
class UserInformationAdmin(admin.ModelAdmin):
    pass
