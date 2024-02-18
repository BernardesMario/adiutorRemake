from io import StringIO, BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(template_src, context):
    template = get_template(template_src)
    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(StringIO(html).getvalue(), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Opa! Algo deu errado. Favor entrar em contato.')
