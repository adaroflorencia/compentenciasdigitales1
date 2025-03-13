from django.urls import path
from . import views

urlpatterns = [

    path('actualizar-cursos/', views.actualizar_cursos, name='actualizar_cursos'),

]
