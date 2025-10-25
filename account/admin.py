
from .models import User

from django.contrib import admin



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'age',
        'default_role',
    )

    actions = []