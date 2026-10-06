import datetime
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generiere_tabelle_daten():
    """Generiert zufällige Zahlen für eine 4x4 Rechentabelle (Addition)."""
    top_numbers = [random.randint(2, 9) for _ in range(3)]
    left_numbers = [random.randint(2, 9) for _ in range(3)]

    aufgabe = [
        ['+'] + top_numbers,
        [left_numbers[0], '', '', ''],
        [left_numbers[1], '', '', ''],
        [left_numbers[2], '', '', '']
    ]

    loesung = [
        ['+'] + top_numbers,
        [left_numbers[0], left_numbers[0] + top_numbers[0], left_numbers[0] + top_numbers[1],
         left_numbers[0] + top_numbers[2]],
        [left_numbers[1], left_numbers[1] + top_numbers[0], left_numbers[1] + top_numbers[1],
         left_numbers[1] + top_numbers[2]],
        [left_numbers[2], left_numbers[2] + top_numbers[0], left_numbers[2] + top_numbers[1],
         left_numbers[2] + top_numbers[2]]
    ]

    return aufgabe, loesung


def zeichne_fusszeile(canvas, doc, dateiname):
    """Zeichnet den Dateinamen dezent unten links auf die Seite."""
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.gray)
    canvas.drawString(30, 20, f"Datei: {dateiname}")
    canvas.restoreState()


def baue_seiten_inhalt(story, tabellen_daten, ist_loesung, styles):
    """Erzeugt den Tabellen-Inhalt für eine einzelne Seite mit Nummern."""
    titel_style = ParagraphStyle(
        'TitelStyle_' + str(ist_loesung), parent=styles['Heading1'],
        fontSize=20, leading=24, spaceAfter=15, alignment=1
    )
    zell_style = ParagraphStyle(
        'ZellStyle_' + str(ist_loesung), parent=styles['Normal'],
        fontSize=13, leading=15, alignment=1
    )
    nummer_style = ParagraphStyle(
        'NummerStyle_' + str(ist_loesung), parent=styles['Normal'],
        fontSize=11, leading=13, alignment=0, fontName='Helvetica-Bold',
        spaceAfter=4
    )

    titel_text = "Rechentabellen - LÖSUNGSBLATT" if ist_loesung else "Rechentabellen - Übungsblatt"
    story.append(Paragraph(titel_text, titel_style))

    einzel_blöcke = []
    for idx, daten in enumerate(tabellen_daten, start=1):
        formatiere_daten = [[Paragraph(str(zelle), zell_style) for zelle in zeile] for zeile in daten]

        # Erstellung der mathematischen Tabelle
        t = Table(formatiere_daten, colWidths=[52] * 4, rowHeights=[26] * 4)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ]))

        # Nummerierung über der Tabelle platzieren
        beschriftung = Paragraph(f"Aufgabe {idx}:", nummer_style)

        # Block aus Nummer und Tabelle zusammenfügen
        block_tabelle = Table([[beschriftung], [t]], colWidths=[210])
        block_tabelle.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        einzel_blöcke.append(block_tabelle)

    # Erstelle Paare für das 2-Spalten-Layout auf der Seite
    grid_elemente = []
    for i in range(0, len(einzel_blöcke), 2):
        zeile = einzel_blöcke[i:i + 2]
        if len(zeile) < 2:
            zeile.append('')
        grid_elemente.append(zeile)

    # Haupttabelle für die Seitenstruktur
    haupt_tabelle = Table(grid_elemente, colWidths=[250, 250])
    haupt_tabelle.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))

    story.append(haupt_tabelle)


def main():
    zeitstempel = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    dateiname = f"Rechentabellen_{zeitstempel}.pdf"

    doc = SimpleDocTemplate(
        dateiname, pagesize=A4,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    aufgaben_liste = []
    loesungen_liste = []

    for _ in range(10):
        aufgabe, loesung = generiere_tabelle_daten()
        aufgaben_liste.append(aufgabe)
        loesungen_liste.append(loesung)

    # Seite 1: Aufgaben
    baue_seiten_inhalt(story, aufgaben_liste, ist_loesung=False, styles=styles)

    # Umbruch zu Seite 2
    story.append(PageBreak())

    # Seite 2: Lösungen
    baue_seiten_inhalt(story, loesungen_liste, ist_loesung=True, styles=styles)

    doc.build(
        story,
        onFirstPage=lambda c, d: zeichne_fusszeile(c, d, dateiname),
        onLaterPages=lambda c, d: zeichne_fusszeile(c, d, dateiname)
    )
    print(f"Datei erfolgreich generiert: {dateiname}")


if __name__ == "__main__":
    main()
