from django.urls import path
from . import views

# Insert URLs patterns

urlpatterns = [
    # URL padrão
    path('', views.index, name='index'),

    # Signin URL
    path('signin/', views.signin, name='signin'),

    # Signup URL
    path('signup/', views.signup, name='signup'),
]
