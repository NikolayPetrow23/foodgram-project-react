from io import BytesIO

from django.db.models import QuerySet
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

NAME_INGREDIENT = 0
AMOUNT_INGREDIENT = 2
UNIT_INGREDIENT = 1


def generate_shopping_list(shopping_items: QuerySet):
    """
    Функция генерации PDF-файла.
    """
    pdf_buffer = BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdfmetrics.registerFont(
        TTFont(
            "DejaVuSerif",
            "DejaVuSerif.ttf",
            "UTF-8")
    )

    pdf_canvas.setFont("DejaVuSerif", 16)
    pdf_canvas.drawString(200, 750, "Продуктовый помощник")

    page_width, _ = letter
    line_y = 730
    pdf_canvas.line(100, 730, page_width - 100, line_y)

    pdf_canvas.setFont("DejaVuSerif", 13)
    pdf_canvas.drawString(100, 700, "Список покупок:")

    pdf_canvas.setFont("DejaVuSerif", 10)
    line = 670

    for shopping_item in shopping_items:
        pdf_canvas.drawString(
            120, line,
            (f"• {shopping_item[NAME_INGREDIENT]} - "
             f"{shopping_item[AMOUNT_INGREDIENT]} "
             f"{shopping_item[UNIT_INGREDIENT]}")
        )
        line -= 20

    pdf_canvas.save()

    return pdf_buffer
