from django.urls import path
from . import views

urlpatterns = [
    path('docente/', views.docente, name='docentes'),
    path('estudiante/', views.estudiante, name='estudiantes'),
    path('no_docentes/', views.no_docentes, name='no_docentes'),

    path('examen/', views.evaluate, name='evaluate'),
    path('submit_answers/', views.submit_answers, name='submit_answers'),
    path('results/', views.results, name='results'),

]
