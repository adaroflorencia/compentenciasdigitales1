from django.db import models

class Curso(models.Model):
    curso = models.CharField(max_length=200)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    enlace = models.URLField()
