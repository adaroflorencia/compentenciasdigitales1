from django.urls import path
from . import views

urlpatterns = [

    path('docente/', views.docente, name='docentes'),
    path('estudiante/', views.estudiante, name='estudiantes'),
    path('no_docentes/', views.no_docentes, name='no_docentes'),
    path('generate_form/<int:role_id>/', views.generate_form, name='generate_form'),
    path('evaluate/<int:role_id>/', views.evaluate, name='evaluate'),

    path('form/results/', views.results, name='results'),
    path('results/<int:role>/', views.results, name='results'),

]
