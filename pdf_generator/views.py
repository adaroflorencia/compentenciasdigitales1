# pdf_generator/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

def generar_pdf(request, template_name, context=None):
    # Renderiza la plantilla HTML a partir del nombre de la plantilla y el contexto
    html = render_to_string(template_name, context or {})

    # Genera el PDF a partir del HTML
    pdf = HTML(string=html).write_pdf()

    # Crea la respuesta HTTP con el archivo PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{template_name}.pdf"'

    return response
