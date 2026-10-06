import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
filename = f"Zahlenmauern_{timestamp}.pdf"


def generate_wall_data(rows=4):
    """Generiert die mathematischen Daten für eine vierreihige Zahlenmauer."""
    base = [random.randint(1, 10) for _ in range(rows)]
    wall = [base]

    for i in range(rows - 1):
        current_row = wall[-1]
        next_row = [current_row[j] + current_row[j + 1] for j in range(len(current_row) - 1)]
        wall.append(next_row)

    return wall


def is_solvable_and_unique(mask):
    """Prüft über ein Gleichungssystem, ob die 4 Felder eindeutig lösbar sind."""
    pos_to_coefficients = {
        (0, 0): [1, 0, 0, 0], (0, 1): [0, 1, 0, 0], (0, 2): [0, 0, 1, 0], (0, 3): [0, 0, 0, 1],
        (1, 0): [1, 1, 0, 0], (1, 1): [0, 1, 1, 0], (1, 2): [0, 0, 1, 1],
        (2, 0): [1, 2, 1, 0], (2, 1): [0, 1, 2, 1],
        (3, 0): [1, 3, 3, 1]
    }
    matrix = [pos_to_coefficients[pos] for pos in mask]

    def determinant_4x4(m):
        def det3x3(a, b, c, d, e, f, g, h, i):
            return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

        return (m[0][0] * det3x3(m[1][1], m[1][2], m[1][3], m[2][1], m[2][2], m[2][3], m[3][1], m[3][2], m[3][3])
                - m[0][1] * det3x3(m[1][0], m[1][2], m[1][3], m[2][0], m[2][2], m[2][3], m[3][0], m[3][2], m[3][3])
                + m[0][2] * det3x3(m[1][0], m[1][1], m[1][3], m[2][0], m[2][1], m[2][3], m[3][0], m[3][1], m[3][3])
                - m[0][3] * det3x3(m[1][0], m[1][1], m[1][2], m[2][0], m[2][1], m[2][2], m[3][0], m[3][1], m[3][2]))

    return determinant_4x4(matrix) != 0


def get_valid_visible_mask():
    """Generiert eine Maske aus genau 4 eindeutig lösbaren Feldern."""
    all_positions = []
    for row_idx in range(4):
        for col_idx in range(4 - row_idx):
            all_positions.append((row_idx, col_idx))

    while True:
        chosen_positions = random.sample(all_positions, 4)
        if is_solvable_and_unique(chosen_positions):
            return chosen_positions


def draw_single_wall(c, x_offset, y_offset, wall_data, visible_mask, is_solution=False):
    """Zeichnet die Zahlenmauer."""
    box_width = 32
    box_height = 18

    for row_idx, row in enumerate(wall_data):
        row_shift = (row_idx * box_width) / 2
        y = y_offset + (row_idx * box_height)

        for col_idx, val in enumerate(row):
            x = x_offset + row_shift + (col_idx * box_width)
            is_hint = (row_idx, col_idx) in visible_mask

            c.setStrokeColor(colors.black)
            c.setLineWidth(1)

            if is_solution:
                if not is_hint:
                    c.setFillColor(colors.HexColor("#EAEAEA"))
                    c.rect(x, y, box_width, box_height, fill=1, stroke=1)
                else:
                    c.rect(x, y, box_width, box_height, fill=0, stroke=1)
            else:
                c.rect(x, y, box_width, box_height, fill=0, stroke=1)

            c.setFillColor(colors.black)

            if is_solution or is_hint:
                c.setFont("Helvetica", 10)
                c.drawCentredString(x + box_width / 2, y + 5, str(val))


def build_page(c, title, walls_data, filename, is_solution=False):
    """Baut das Layout für eine PDF-Seite auf."""
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(297, 805, title)

    #if not is_solution:
    #    c.setFont("Helvetica", 10)
    #    c.drawString(50, 775, "Name: _______________________")
    #    c.drawRightString(545, 775, "Datum: _______________")
    #else:
    #    c.setFont("Helvetica-Oblique", 11)
    #    c.drawString(50, 775, "Graue Felder wurden berechnet — Eindeutige Lösung garantiert")

    col_width = 250
    row_height = 132 #132
    start_x = 110
    start_y = 100

    for idx, (wall_data, visible_mask) in enumerate(walls_data):
        col = idx % 2
        row = 4 - (idx // 2)

        x = start_x + (col * col_width)
        y = start_y + (row * row_height)

        c.setFont("Helvetica-Bold" if is_solution else "Helvetica-Bold", 9)
        c.drawString(x, y + 78, f"Aufgabe {idx + 1}:")

        draw_single_wall(c, x, y, wall_data, visible_mask, is_solution=is_solution)
    # NEU: Dateiname als kleine Fußzeile unten links andrucken
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawString(30, 20, f"Datei: {filename}")
    c.setFillColor(colors.black)


def create_math_walls_pdf():
    """Generiert den zeitabhängigen Dateinamen und baut das zweiseitige PDF."""
    # Zeitstempel generieren im Format YYYYMMDD_HHMMSS

    #timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    #filename = f"zahlenmauern_{timestamp}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)

    all_walls_data = []
    for _ in range(10):
        wall = generate_wall_data(rows=4)
        mask = get_valid_visible_mask()
        all_walls_data.append((wall, mask))

    # Seite 1
    build_page(c, "Zahlenmauern - Übungsblatt", all_walls_data, filename, is_solution=False)
    c.showPage()

    # Seite 2
    build_page(c, "Zahlenmauern - LÖSUNGSBLATT", all_walls_data, filename, is_solution=True)
    c.showPage()

    c.save()
    print(f"PDF erfolgreich unter '{filename}' gespeichert!")


if __name__ == "__main__":
    create_math_walls_pdf()
