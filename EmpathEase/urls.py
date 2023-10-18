from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name = 'login'),
    path('EmpathEase', views.empathEase, name = 'EmpathEase'),
    path('register', views.register, name = 'register'),
    path('logout', views.logout, name = 'logout'),
    path('help/', views.help_page, name='help'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)