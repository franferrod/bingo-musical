"""
Bingo Musical - 60 cumpleanios Paco y Mariadel
PDF de 17 paginas A4, 65 cartones unicos.
Diseno premium con fuentes Abril Fatface + Merriweather.
"""

import random
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACION
# ─────────────────────────────────────────────────────────────────────────────

SEED = 42
NUM_CARTONES = 65
CANCIONES_POR_CARTON = 8

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
FOTO_PATH = os.path.join(BASE_DIR, "foto_paco_mariadel.jpeg")
OUTPUT_PATH = os.path.join(BASE_DIR, "bingo_paco_mariadel.pdf")

# ── Paleta premium (UI/UX Pro Max: Elegant Celebration + Luxury Brand) ────────
COLOR_CREMA       = colors.HexColor("#F8F3E6")   # warm cream background
COLOR_CREMA_DARK  = colors.HexColor("#EDE7D3")   # slightly darker for alternation
COLOR_VERDE       = colors.HexColor("#1A4A2E")   # dark green (brand)
COLOR_DORADO      = colors.HexColor("#B8872A")   # gold accent (CA8A04 darkened for print)
COLOR_GRIS_TEXTO  = colors.HexColor("#2A2A2A")   # near-black for song text
COLOR_GRIS_BORDE  = colors.HexColor("#8A7A5A")   # warm grey border for cells
COLOR_BLANCO      = colors.white

# ─────────────────────────────────────────────────────────────────────────────
# REGISTRO DE FUENTES
# ─────────────────────────────────────────────────────────────────────────────

def register_fonts():
    font_files = {
        "AbrilFatface":         "AbrilFatface-Regular.ttf",
        "Merriweather":         "Merriweather-Regular.ttf",
        "Merriweather-Bold":    "Merriweather-Bold.ttf",
        "Merriweather-Italic":  "Merriweather-Italic.ttf",
        "Merriweather-BoldItalic": "Merriweather-BoldItalic.ttf",
        "Lato":                 "Lato-Regular.ttf",
        "Lato-Bold":            "Lato-Bold.ttf",
        "Lato-Italic":          "Lato-Italic.ttf",
    }
    registered = []
    for name, fname in font_files.items():
        path = os.path.join(FONTS_DIR, fname)
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
            registered.append(name)
        else:
            print(f"  WARN: fuente no encontrada: {path}")

    # Registrar familias para bold/italic automatico
    if "Merriweather" in registered and "Merriweather-Bold" in registered:
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        try:
            registerFontFamily(
                "Merriweather",
                normal="Merriweather",
                bold="Merriweather-Bold",
                italic="Merriweather-Italic",
                boldItalic="Merriweather-BoldItalic",
            )
        except Exception:
            pass

    print(f"Fuentes registradas: {registered}")
    return registered

# ─────────────────────────────────────────────────────────────────────────────
# PLAYLIST
# ─────────────────────────────────────────────────────────────────────────────

PLAYLIST = [
    ("Berghain", "Rosalia"),
    ("Ella y yo", "Don Omar"),
    ("La mujer de verde", "Izal"),
    ("Mil calles llevan hacia ti", "La Guardia"),
    ("Cien gaviotas", "Duncan Dhu"),
    ("Pero a tu lado", "Los Secretos"),
    ("Dejame", "Los Secretos"),
    ("Cuando brille el sol", "La Guardia"),
    ("Una foto en blanco y negro", "El Canto del Loco"),
    ("Tenia tanto que darte", "Nena Daconte"),
    ("Princesas", "Pereza"),
    ("20 de Abril", "Celtas Cortos"),
    ("Por la boca vive el pez", "Fito y Fitipaldis"),
    ("Estrella polar", "Pereza"),
    ("El ultimo vals", "Oreja de Van Gogh"),
    ("La casa por el tejado", "Fito y Fitipaldis"),
    ("Volvera", "El Canto del Loco"),
    ("Noche de sexo", "Wisin & Yandel"),
    ("Limbo", "Daddy Yankee"),
    ("Waka Waka", "Shakira"),
    ("La morocha", "Luck Ra"),
    ("La mujer del pelotero", "Baby Lores"),
    ("Purpurina", "Gambino"),
    ("El Niagara en bicicleta", "Juan Luis Guerra"),
    ("La Bilirrubina", "Juan Luis Guerra"),
    ("19 dias y 500 noches", "Sabina"),
    ("Y nos dieron las diez", "Sabina"),
    ("Si antes te hubiera conocido", "Karol G"),
    ("Caminando por la vida", "Melendi"),
    ("Pan y mantequilla", "Efecto Pasillo"),
    ("No puedo vivir sin ti", "Los Ronaldos"),
    ("Cuando zarpa el amor", "Camela"),
    ("Ave Maria", "David Bisbal"),
    ("Pasa la vida", "Albahaca"),
    ("Como Camaron", "Estopa"),
    ("Toda la noche en la calle", "Amaral"),
    ("Yo quiero bailar", "Sonia y Selena"),
    ("Como te atreves", "Morat"),
    ("La revolucion sexual", "La Casa Azul"),
    ("Chica de ayer", "Nacha Pop"),
    ("Nada fue un error", "Coti"),
    ("Marta, Sebas, Guille y los demas", "Amaral"),
    ("Limon y sal", "Julieta Venegas"),
    ("Fisica o quimica", "Despistaos"),
    ("La primavera trompetera", "Los Delincuentes"),
    ("El fin del mundo", "La La Love You"),
    ("Dos hombres y un destino", "Alex & Bustamante"),
    ("Un ano mas", "Mecano"),
    ("Hijo de la Luna", "Mecano"),
    ("Cruz de Navajas", "Mecano"),
    ("Puedes contar conmigo", "Oreja de Van Gogh"),
    ("20 de enero", "Oreja de Van Gogh"),
    ("Labios compartidos", "Mana"),
    ("Clavado en un bar", "Mana"),
    ("Hala Madrid", "Real Madrid"),
]

# ─────────────────────────────────────────────────────────────────────────────
# GENERACION DE CARTONES UNICOS
# ─────────────────────────────────────────────────────────────────────────────

def generar_cartones():
    rng = random.Random(SEED)
    cartones = []
    usados = set()
    intentos = 0
    while len(cartones) < NUM_CARTONES:
        intentos += 1
        if intentos > 200000:
            raise RuntimeError("No se pudo generar cartones unicos suficientes.")
        muestra = tuple(sorted(rng.sample(range(len(PLAYLIST)), CANCIONES_POR_CARTON)))
        if muestra not in usados:
            usados.add(muestra)
            indices = list(muestra)
            rng.shuffle(indices)
            cartones.append([PLAYLIST[i] for i in indices])
    print(f"OK: {len(cartones)} cartones unicos generados.")
    return cartones

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────

def make_cropped_reader(foto_path, cell_w, cell_h):
    """Pre-recorta la foto con PIL al aspect ratio exacto de la celda."""
    img = Image.open(foto_path).convert("RGB")
    iw, ih = img.size
    ratio = cell_w / cell_h
    if (iw / ih) > ratio:
        new_w = int(ih * ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        new_h = int(iw / ratio)
        top = (ih - new_h) // 2
        img = img.crop((0, top, iw, top + new_h))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return ImageReader(buf)


def wrap_text(c, text, font_name, font_size, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if c.stringWidth(test, font_name, font_size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def available_font(preferred, fallback="Helvetica"):
    """Devuelve preferred si esta registrado, si no fallback."""
    try:
        pdfmetrics.getFont(preferred)
        return preferred
    except Exception:
        return fallback


# ─────────────────────────────────────────────────────────────────────────────
# DIBUJO DE CABECERA
# ─────────────────────────────────────────────────────────────────────────────

def draw_header(c, x, y, w, h):
    """
    Cabecera: BINGO / MUSICAL / ovalo — distribuidos de arriba a abajo
    sin solapamientos. Calculo de posicion vertical desde arriba.
    x,y = esquina inferior izquierda de la cabecera.
    """
    # Fondo crema
    c.setFillColor(COLOR_CREMA)
    c.rect(x, y, w, h, fill=1, stroke=0)

    # Linea dorada inferior separadora
    c.setStrokeColor(COLOR_DORADO)
    c.setLineWidth(0.8)
    c.line(x + w * 0.06, y + 1, x + w * 0.94, y + 1)

    font_bingo   = available_font("AbrilFatface", "Helvetica-Bold")
    font_leyenda = available_font("Merriweather-Italic", "Helvetica-Oblique")
    cx = x + w / 2

    # ── Tamanios calculados para que quepan sin solaparse ────────────────────
    # Reservamos espacio: padding_top + BINGO + gap1 + MUSICAL + gap2 + oval + padding_bot
    padding_top = h * 0.05
    padding_bot = h * 0.04
    gap1 = h * 0.01   # entre BINGO y MUSICAL
    gap2 = h * 0.03   # entre MUSICAL y ovalo

    # El ovalo tendra altura fija = ~22% del header
    oval_frac   = 0.20
    oval_h_val  = h * oval_frac

    # El espacio para BINGO + MUSICAL = total - reservas
    text_space = h - padding_top - padding_bot - gap1 - gap2 - oval_h_val
    # BINGO toma 60% del text_space, MUSICAL el 40%
    size_bingo   = text_space * 0.60
    size_musical = text_space * 0.40
    size_leyenda = oval_h_val * 0.42   # texto = ~42% del alto del ovalo

    # ── Posiciones verticales (de arriba hacia abajo) ────────────────────────
    top = y + h  # tope de la cabecera

    # Baseline de BINGO: debajo del padding superior
    bingo_baseline = top - padding_top - size_bingo * 0.85

    # Baseline de MUSICAL: debajo de BINGO
    musical_baseline = bingo_baseline - size_bingo * 0.25 - gap1 - size_musical * 0.85

    # Ovalo: debajo de MUSICAL
    oval_top = musical_baseline - size_musical * 0.20 - gap2
    oval_y1  = oval_top - oval_h_val
    oval_y2  = oval_top

    # ── Estrellas doradas ────────────────────────────────────────────────────
    star_size = size_bingo * 0.45
    c.setFont(font_bingo, star_size)
    c.setFillColor(COLOR_DORADO)
    star_y = bingo_baseline - size_bingo * 0.05
    c.drawString(x + w * 0.04, star_y, "*")
    c.drawRightString(x + w * 0.96, star_y, "*")

    # ── BINGO ────────────────────────────────────────────────────────────────
    c.setFont(font_bingo, size_bingo)
    c.setFillColor(COLOR_VERDE)
    c.drawCentredString(cx, bingo_baseline, "BINGO")

    # ── MUSICAL ──────────────────────────────────────────────────────────────
    c.setFont(font_bingo, size_musical)
    c.setFillColor(COLOR_VERDE)
    c.drawCentredString(cx, musical_baseline, "MUSICAL")

    # ── Ovalo con leyenda ────────────────────────────────────────────────────
    leyenda_text = "60 cumpleaños Paco y Mariadel"
    text_width   = c.stringWidth(leyenda_text, font_leyenda, size_leyenda)
    oval_pad_h   = size_leyenda * 2.0   # padding horizontal holgado
    oval_w       = min(w * 0.88, text_width + 2 * oval_pad_h)
    oval_x1      = cx - oval_w / 2
    oval_x2      = cx + oval_w / 2

    c.setFillColor(COLOR_CREMA)
    c.setStrokeColor(COLOR_DORADO)
    c.setLineWidth(0.9)
    c.ellipse(oval_x1, oval_y1, oval_x2, oval_y2, fill=1, stroke=1)

    # Baseline del texto = centro del ovalo menos descenso tipografico
    text_y = oval_y1 + oval_h_val / 2 - size_leyenda * 0.30
    c.setFont(font_leyenda, size_leyenda)
    c.setFillColor(COLOR_VERDE)
    c.drawCentredString(cx, text_y, leyenda_text)


# ─────────────────────────────────────────────────────────────────────────────
# DIBUJO DE CELDA DE CANCION
# ─────────────────────────────────────────────────────────────────────────────

def draw_song_cell(c, cx, cy, cw, ch, titulo, artista):
    """Dibuja titulo (bold) + artista (dorado cursiva) centrados en la celda."""
    font_t = available_font("Merriweather-Bold", "Helvetica-Bold")
    font_a = available_font("Merriweather-Italic", "Helvetica-Oblique")

    pad   = cw * 0.07
    max_w = cw - 2 * pad

    # Tamanos calibrados: el titulo destaca, el artista es discreto
    size_t = max(5.5, min(7.5, ch * 0.145))
    size_a = max(4.0, min(6.0, ch * 0.115))
    lead_t = size_t * 1.35
    lead_a = size_a * 1.35
    gap    = ch * 0.03

    lines_t = wrap_text(c, titulo, font_t, size_t, max_w)
    lines_a = wrap_text(c, artista, font_a, size_a, max_w)

    total_h = len(lines_t) * lead_t + gap + len(lines_a) * lead_a

    # Centrado vertical: el bloque de texto queda centrado en la celda
    ty = cy + (ch + total_h) / 2 - lead_t * 0.78

    c.setFillColor(COLOR_GRIS_TEXTO)
    for line in lines_t:
        c.setFont(font_t, size_t)
        c.drawCentredString(cx + cw / 2, ty, line)
        ty -= lead_t

    ty -= gap
    c.setFillColor(COLOR_DORADO)
    for line in lines_a:
        c.setFont(font_a, size_a)
        c.drawCentredString(cx + cw / 2, ty, line)
        ty -= lead_a


# ─────────────────────────────────────────────────────────────────────────────
# DIBUJO DE UN CARTON COMPLETO
# ─────────────────────────────────────────────────────────────────────────────

def draw_carton(c, x, y, w, h, canciones, foto_reader):
    """
    Dibuja un carton en (x,y) con tamano (w,h).
    canciones: lista de 8 tuplas (titulo, artista).
    """
    # Sin radio en las esquinas: bordes rectos para recorte limpio
    # Sin sombra: el exterior de la pagina es blanco puro

    # ── Fondo del carton ─────────────────────────────────────────────────────
    c.setFillColor(COLOR_CREMA)
    c.rect(x, y, w, h, fill=1, stroke=0)



    # ── Cabecera ─────────────────────────────────────────────────────────────
    header_ratio = 0.32
    header_h = h * header_ratio
    header_y = y + h - header_h
    draw_header(c, x, header_y, w, header_h)

    # ── Grid 3x3 ─────────────────────────────────────────────────────────────
    grid_margin_x = w * 0.028
    grid_margin_y = w * 0.022
    grid_x = x + grid_margin_x
    grid_y = y + grid_margin_y
    grid_w = w - 2 * grid_margin_x
    grid_h = h - header_h - 2 * grid_margin_y

    cell_gap = w * 0.016
    cell_w = (grid_w - 2 * cell_gap) / 3
    cell_h = (grid_h - 2 * cell_gap) / 3

    song_idx = 0
    for row in range(3):
        for col in range(3):
            cx = grid_x + col * (cell_w + cell_gap)
            cy = grid_y + grid_h - (row + 1) * cell_h - row * cell_gap

            is_center = (row == 1 and col == 1)

            # Fondo blanco de celda con borde dorado sutil
            c.setFillColor(COLOR_BLANCO)
            c.setStrokeColor(COLOR_GRIS_BORDE)
            c.setLineWidth(0.55)
            c.rect(cx, cy, cell_w, cell_h, fill=1, stroke=1)

            if is_center:
                # Foto pre-recortada llenando la celda
                c.drawImage(
                    foto_reader, cx, cy,
                    width=cell_w, height=cell_h,
                    preserveAspectRatio=False, mask="auto"
                )
                # Re-dibujar borde encima de la foto
                c.setStrokeColor(COLOR_GRIS_BORDE)
                c.setLineWidth(0.55)
                c.rect(cx, cy, cell_w, cell_h, fill=0, stroke=1)
            else:
                draw_song_cell(c, cx, cy, cell_w, cell_h, *canciones[song_idx])
                song_idx += 1

    # ── Borde exterior: se dibuja AL FINAL para quedar sobre todo el contenido ──
    c.setStrokeColor(COLOR_VERDE)
    c.setLineWidth(1.5)
    c.rect(x, y, w, h, fill=0, stroke=1)

# ─────────────────────────────────────────────────────────────────────────────
# DIBUJO DE PAGINA
# ─────────────────────────────────────────────────────────────────────────────

def draw_page(c, cartones_pagina, foto_reader, page_w, page_h):
    # Fondo de pagina BLANCO puro — para recorte limpio de los cartones
    c.setFillColor(colors.white)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # ── Borde de pagina: marco verde alrededor de los 4 cartones ──────────────
    border_margin = 5 * mm
    c.setStrokeColor(COLOR_VERDE)
    c.setLineWidth(1.5)
    c.rect(border_margin, border_margin,
           page_w - 2 * border_margin, page_h - 2 * border_margin,
           fill=0, stroke=1)

    margin = 9 * mm
    gap    = 5 * mm
    area_w = page_w - 2 * margin
    area_h = page_h - 2 * margin

    card_w = (area_w - gap) / 2
    card_h = (area_h - gap) / 2

    # Posiciones: arriba-izq, arriba-der, abajo-izq, abajo-der
    positions = [
        (margin,          margin + card_h + gap),   # fila superior izq
        (margin + card_w + gap, margin + card_h + gap),  # fila superior der
        (margin,          margin),                  # fila inferior izq
        (margin + card_w + gap, margin),            # fila inferior der
    ]

    for i, canciones in enumerate(cartones_pagina):
        cx, cy = positions[i]
        draw_carton(c, cx, cy, card_w, card_h, canciones, foto_reader)



def generar_pdf(playlist=None, foto_path=None, output_path=None, num_cartones=None):
    """
    Funcion principal reutilizable.
    - playlist: lista de tuplas (titulo, artista). Si None, usa PLAYLIST global.
    - foto_path: ruta a la foto central. Si None, usa FOTO_PATH global.
    - output_path: ruta de salida del PDF. Si None, usa OUTPUT_PATH global.
    - num_cartones: numero de cartones a generar. Si None, usa NUM_CARTONES global.
    Devuelve la ruta del PDF generado.
    """
    _playlist    = playlist    if playlist    is not None else PLAYLIST
    _foto_path   = foto_path   if foto_path   is not None else FOTO_PATH
    _output_path = output_path if output_path is not None else OUTPUT_PATH
    _n           = num_cartones if num_cartones is not None else NUM_CARTONES

    register_fonts()

    # Generar cartones unicos con la playlist dada
    rng = random.Random(SEED)
    cartones = []
    usados = set()
    intentos = 0
    while len(cartones) < _n:
        intentos += 1
        if intentos > 500000:
            raise RuntimeError("No hay suficientes canciones para generar cartones unicos.")
        muestra = tuple(sorted(rng.sample(range(len(_playlist)), CANCIONES_POR_CARTON)))
        if muestra not in usados:
            usados.add(muestra)
            indices = list(muestra)
            rng.shuffle(indices)
            cartones.append([_playlist[i] for i in indices])

    # Calcular dimensiones
    margin = 9 * mm
    gap    = 5 * mm
    page_w, page_h = A4
    card_w = (page_w - 2 * margin - gap) / 2
    card_h = (page_h - 2 * margin - gap) / 2
    grid_margin_x = card_w * 0.028
    grid_margin_y = card_w * 0.022
    grid_w = card_w - 2 * grid_margin_x
    grid_h = card_h * (1 - 0.295) - 2 * grid_margin_y
    cell_gap = card_w * 0.016
    cell_w = (grid_w - 2 * cell_gap) / 3
    cell_h = (grid_h - 2 * cell_gap) / 3

    foto_reader = make_cropped_reader(_foto_path, cell_w, cell_h)

    c = canvas.Canvas(_output_path, pagesize=A4)
    c.setTitle("Bingo Musical - 60 cumpleaños Paco y Mariadel")
    c.setAuthor("Bingo Musical")

    i = 0
    while i < _n:
        lote = cartones[i : i + 4]
        c.saveState()
        draw_page(c, lote, foto_reader, page_w, page_h)
        c.restoreState()
        c.showPage()
        i += 4

    c.save()
    return _output_path


def main():
    """Punto de entrada por linea de comandos: usa valores por defecto."""
    print("Generando Bingo Musical...")
    out = generar_pdf()
    print(f"OK: PDF generado -> {out}")


if __name__ == "__main__":
    main()
