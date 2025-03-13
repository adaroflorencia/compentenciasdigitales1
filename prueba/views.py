from django.http import JsonResponse
from .scraping import scrape_cursos

def actualizar_cursos(request):
    scrape_cursos()
    return JsonResponse({'status': 'Cursos actualizados correctamente'})
