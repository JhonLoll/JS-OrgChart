from os import name
from django.urls import path
from . import views

# Insert URLs patterns

urlpatterns = [
    # URL padrão
    path('', views.index, name='index'),

    # ==================================================
    # Signin URL
    path('signin/', views.signin, name='signin'),

    # Signup URL
    path('signup/', views.signup, name='signup'),

    # Logout URL
    path('logout/', views._logout, name='logout'),
    # ==================================================

    # OrgChart URL
    path('orgchart/', views.orgchart, name='orgchart'),
    # ==================================================

    # Register Employee - URL
    path('registeremployee/', views.register_employee, name='register_employee'),

    # List Employee - URL
    path('listemployee/', views.list_employee, name='list_employee'),
    path('listemployee/<int:id>', views.list_employee, name='list_employee'),

    # Delete Employee - URL
    path('deleteemployee/<int:id>', views.delete_employee, name='delete_employee'),
    # ==================================================
]
