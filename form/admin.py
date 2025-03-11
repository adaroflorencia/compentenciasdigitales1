from django.contrib import admin
from .models import Topic, Question, Option, Role

admin.site.register(Role)
admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Option)