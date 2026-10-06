import os
import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
filename = f"Einmaleins_Tabelle_{timestamp}.pdf"
luecken = 15

class InteractiveFormField(Flowable):
    def __init__(self, width, height, name):
        super().__init__()
        self.width = width
        self.height = height
        self.name = name

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        form = self.canv.acroForm

        # Erstellt das relative Textfeld
        form.textfieldRelative(
            name=self.name,
            x=2,
            y=2,
            width=self.width - 4,
            height=self.height - 4,
            borderWidth=0,
            fillColor=colors.HexColor("#eef2ff"),  # Hellblaues Feld für Lücken
            fontSize=11,
            textColor=colors.black
        )

        # Sichert die Zentrierung (PDF /Q 1)
        if self.name in form.fields:
            field_obj = form.fields[self.name]
            field_obj.Q = 1

        self.canv.restoreState()


def create_einmaleins_pdf(filename="einmaleins_uebung.pdf"):
    # 1. Dokumenten-Setup (DIN A4 Maße trennen)
    a4_width, a4_height = A4
    margin = 3 * 28.35  # 3 cm
    bottom_margin = 4 * 28.35  # 4 cm Platz für Fußzeile

    doc = BaseDocTemplate(filename, pagesize=A4)

    # Inhaltsbereich (Frame) definieren
    frame = Frame(
        margin, bottom_margin,
        a4_width - (2 * margin), a4_height - margin - bottom_margin,
        id='normal'
    )

    # Fußzeile exklusiv für den Dateinamen
    def footer_callback(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.HexColor("#555555"))
        canvas_obj.drawString(margin, 1.5 * 28.35, f"Datei: {os.path.basename(filename)}")

        if hasattr(canvas_obj, 'acroForm') and canvas_obj.acroForm:
            canvas_obj.acroForm.need_appearances = True

        canvas_obj.restoreState()

    template = PageTemplate(id='einmaleins_layout', frames=frame, onPage=footer_callback)
    doc.addPageTemplates([template])

    story = []
    styles = getSampleStyleSheet()

    # Text-Styles für die Beschriftungen (Weißer Text für dunkelblauen Hintergrund)
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        alignment=1,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        fontSize=11
    )

    # 2. Titel
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'],
        fontSize=24, leading=28, alignment=1, spaceAfter=30
    )
    story.append(Paragraph("Das kleine 1x1 – Übung", title_style))
    story.append(Spacer(1, 15))

    # 3. 15 zufällige Lücken-Positionen bestimmen
    all_positions = [(r, c) for r in range(1, 11) for c in range(1, 11)]
    gap_positions = set(random.sample(all_positions, luecken))

    # 4. Tabellen-Größen berechnen
    available_width = a4_width - (2 * margin)
    col_width = available_width / 11.0
    row_height = col_width  # Quadratische Zellen

    # 5. Tabellendaten generieren
    table_data = []

    # Kopfzeile (X, 1, 2, ... 10) mit weißem Text
    header_row = [Paragraph("*", header_style)] + [Paragraph(str(i), header_style) for i in range(1, 11)]
    table_data.append(header_row)

    # Datenzeilen befüllen
    for r in range(1, 11):
        row = [Paragraph(str(r), header_style)]  # Erste Spalte (Faktor) ebenfalls mit weißem Text
        for c in range(1, 11):
            if (r, c) in gap_positions:
                row.append(InteractiveFormField(col_width, row_height, f"luecke_{r}_{c}"))
            else:
                cell_style = ParagraphStyle('Cell', parent=styles['Normal'], alignment=1, fontSize=11)
                row.append(Paragraph(str(r * c), cell_style))
        table_data.append(row)

    # 6. Tabellen-Styling (Dunkelblaue Hintergründe und Gitter)
    t = Table(table_data, colWidths=[col_width] * 11, rowHeights=[row_height] * 11)

    dunkelblau = colors.HexColor("#1e3a8a")  # Klassisches, edles Dunkelblau

    t_style = TableStyle([
        # Dunkelblauer Hintergrund für die gesamte erste Zeile (Kopfzeile)
        ('BACKGROUND', (0, 0), (-1, 0), dunkelblau),
        # Dunkelblauer Hintergrund für die gesamte erste Spalte
        ('BACKGROUND', (0, 1), (0, -1), dunkelblau),
        # Ausrichtung
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Gitterlinien (ein helles Grau passt optisch sehr gut zu Dunkelblau)
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor("#cccccc")),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ])
    t.setStyle(t_style)
    story.append(t)

    # PDF generieren
    doc.build(story)
    print(f"PDF erfolgreich erstellt: {filename}")


if __name__ == "__main__":
    create_einmaleins_pdf(filename)
