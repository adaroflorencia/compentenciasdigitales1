from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

def generar_pdf(request, template_name, context=None):
    # Renderiza la plantilla HTML a partir del nombre de la plantilla y el contexto
    html = render_to_string(template_name, context or {})

    # Ruta base para los archivos estáticos
    base_url = request.build_absolute_uri('/static/')

    # Genera el PDF a partir del HTML y pasa la base_url
    pdf = HTML(string=html, base_url=base_url).write_pdf()

    # Crea la respuesta HTTP con el archivo PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Resultado competencias digitales.pdf"'

    return response