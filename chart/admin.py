from django.contrib import admin

from chart.models import Cargo, Colaborador, User

# Register your models here.
admin.site.register(User)
admin.site.register(Colaborador)
admin.site.register(Cargo)