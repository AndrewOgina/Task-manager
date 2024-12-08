from django.contrib import admin
from .models import Task
from .models import TimeBlock


# Register your models here.

admin.site.register(Task)
admin.site.register(TimeBlock)
