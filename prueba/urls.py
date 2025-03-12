from django.urls import path
from . import views

urlpatterns = [

    path('docente/', views.docente, name='docentes'),
    path('estudiante/', views.estudiante, name='estudiantes'),
    path('no_docentes/', views.no_docentes, name='no_docentes'),
    path('examen/', views.evaluate, name='evaluate'),
    path('generate_form/', views.generate_form, name='generate_form'),
    path('evaluate/', views.evaluate, name='evaluate'),
    path('results/<str:role.id>/', views.results, name='results'),

]
