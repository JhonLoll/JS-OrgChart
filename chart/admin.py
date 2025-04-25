from django.contrib import admin

from chart.models import Colaborador, User

# Register your models here.
admin.site.register(User)
admin.site.register(Colaborador)