
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),

    path('form/', include('form.urls')),

    path('pdf/', include('pdf_generator.urls')),



]
