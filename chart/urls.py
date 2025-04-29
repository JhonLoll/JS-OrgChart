from django.urls import path

from OrgChart import settings
from . import views

from django.conf.urls.static import static

# Insert URLs patterns

urlpatterns = [
    # URL padrão
    path('', views.index, name='index'),

    # ==================================================
    # Signin URL
    path('signin/', views.signin, name='signin'),
    path('accounts/login/', views.signin, name='signin'),

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

    # Register Employee with Excel - URL
    path('listemployee/upload_excel', views.view_upload_excel, name='view_upload_excel'),

    # Download Excel - URL
    path('download_excel/', views.view_download_excel, name='view_download_excel'),

    # List Employee - URL
    path('listemployee/', views.list_employee, name='list_employee'),
    path('listemployee/<int:id>', views.list_employee, name='list_employee'),

    # Edit Employee - URL
    path('listemployee/editemployee/<int:id>', views.edit_employee, name='edit_employee'),

    # Delete Employee - URL
    path('listemployee/deleteemployee/<int:id>', views.delete_employee, name='delete_employee'),
    # ==================================================
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)