from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from .contracts import get_contract_text

def generate_contract_pdf(event, user):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    text = p.beginText(20 * mm, height - 20 * mm)
    text.setFont("Helvetica", 11)

    contract_text = get_contract_text(event, user)

    for line in contract_text.splitlines():
        text.textLine(line)
    p.drawText(text)
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
