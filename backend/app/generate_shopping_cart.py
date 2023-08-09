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
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdfmetrics.registerFont(
        TTFont(
            "DejaVuSerif",
            "DejaVuSerif.ttf",
            "UTF-8")
    )

    c.setFont("DejaVuSerif", 16)
    c.drawString(200, 750, "Продуктовый помощник")

    page_width, _ = letter
    line_y = 730
    c.line(100, 730, page_width - 100, line_y)

    c.setFont("DejaVuSerif", 13)
    c.drawString(100, 700, "Список покупок:")

    c.setFont("DejaVuSerif", 10)
    y = 670

    for shopping_item in shopping_items:
        c.drawString(
            120, y,
            (f"• {shopping_item[NAME_INGREDIENT]} - "
             f"{shopping_item[AMOUNT_INGREDIENT]} "
             f"{shopping_item[UNIT_INGREDIENT]}")
        )
        y -= 20

    c.save()

    return pdf_buffer
