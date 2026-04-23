"""
Bingo Musical — App web para generar el PDF de cartones.
"""
import io, os, tempfile, math
import streamlit as st

st.set_page_config(page_title="Bingo Musical 🎵", page_icon="🎵", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400&family=Abril+Fatface&display=swap');

html, body, [class*="css"] { font-family: 'Merriweather', Georgia, serif; }

.stApp { background: #FAFAF5; }

h1 { color: #1A4A2E !important; font-family: 'Abril Fatface', Georgia, serif !important;
     text-align: center; font-size: 2.4rem !important; margin-bottom: 0 !important; }

.subtitle { text-align: center; color: #B8872A; font-style: italic;
            font-size: 1.05rem; margin-bottom: 1.5rem; }

.song-card {
    background: white;
    border: 1.5px solid #D4C5A0;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.5rem;
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

div[data-testid="stButton"] > button {
    background: #1A4A2E; color: white; border: none;
    border-radius: 6px; font-weight: bold;
    transition: background 0.2s;
}
div[data-testid="stButton"] > button:hover { background: #B8872A; }

div[data-testid="stDownloadButton"] > button {
    background: #B8872A !important; color: white !important;
    border: none !important; border-radius: 6px !important;
    font-size: 1.1rem !important; font-weight: bold !important;
    width: 100%;
}

.counter-box {
    background: #F0EBD8; border: 1px solid #C8B878;
    border-radius: 8px; padding: 0.8rem 1rem;
    text-align: center; margin: 0.8rem 0;
}
.counter-ok  { color: #1A4A2E; font-weight: bold; }
.counter-warn { color: #B8872A; font-weight: bold; }
.counter-err  { color: #C0392B; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Título ─────────────────────────────────────────────────────────────────────
st.markdown("<h1>🎵 Bingo Musical</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">60 cumpleaños de Paco y Mariadel</p>', unsafe_allow_html=True)

from generar_bingo import PLAYLIST as PLAYLIST_DEFAULT, generar_pdf, CANCIONES_POR_CARTON

# ── Estado de la sesión ────────────────────────────────────────────────────────
if "canciones" not in st.session_state:
    st.session_state.canciones = [
        {"titulo": t, "artista": a} for t, a in PLAYLIST_DEFAULT
    ]

canciones = st.session_state.canciones

# ── Foto ───────────────────────────────────────────────────────────────────────
st.markdown("### 📷 Foto central")
foto_subida = st.file_uploader(
    "Sube una foto (opcional, se usará la de Paco y Mariadel si no subes ninguna)",
    type=["jpg", "jpeg", "png"],
    label_visibility="visible",
)
if foto_subida:
    st.image(foto_subida, width=180)

st.markdown("---")

# ── Lista de canciones ─────────────────────────────────────────────────────────
st.markdown("### 🎶 Canciones del bingo")
st.caption("Añade, edita o elimina canciones. Necesitas mínimo 8 para generar al menos 1 cartón.")

# Botón añadir canción (arriba, bien visible)
if st.button("➕  Añadir canción", use_container_width=False):
    st.session_state.canciones.append({"titulo": "", "artista": ""})
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Renderizar cada canción como una fila compacta
indices_a_borrar = []
for i, cancion in enumerate(canciones):
    col_num, col_titulo, col_artista, col_del = st.columns([0.4, 3, 2.5, 0.6])
    with col_num:
        st.markdown(f"<div style='padding-top:0.45rem;color:#888;font-size:0.9rem;text-align:right'>{i+1}.</div>",
                    unsafe_allow_html=True)
    with col_titulo:
        nuevo_titulo = st.text_input(
            f"titulo_{i}", value=cancion["titulo"],
            placeholder="Título de la canción",
            label_visibility="collapsed", key=f"t_{i}"
        )
        st.session_state.canciones[i]["titulo"] = nuevo_titulo
    with col_artista:
        nuevo_artista = st.text_input(
            f"artista_{i}", value=cancion["artista"],
            placeholder="Artista",
            label_visibility="collapsed", key=f"a_{i}"
        )
        st.session_state.canciones[i]["artista"] = nuevo_artista
    with col_del:
        if st.button("🗑️", key=f"del_{i}", help="Eliminar esta canción"):
            indices_a_borrar.append(i)

# Eliminar canciones marcadas
if indices_a_borrar:
    st.session_state.canciones = [
        c for j, c in enumerate(st.session_state.canciones)
        if j not in indices_a_borrar
    ]
    st.rerun()

st.markdown("---")

# ── Validación y contador ──────────────────────────────────────────────────────
playlist_valida = [
    (c["titulo"].strip(), c["artista"].strip())
    for c in st.session_state.canciones
    if c["titulo"].strip() and c["artista"].strip()
]
n = len(playlist_valida)

# Calcular cuántos cartones únicos son posibles: C(n, 8)
if n >= CANCIONES_POR_CARTON:
    max_unicos = math.comb(n, CANCIONES_POR_CARTON)
    max_cartones = min(200, max_unicos)
    clase = "counter-ok"
    msg = f"✔ {n} canciones · hasta <b>{max_unicos:,}</b> cartones únicos posibles"
else:
    max_cartones = 0
    clase = "counter-err"
    msg = f"✘ {n} canciones — necesitas al menos <b>{CANCIONES_POR_CARTON}</b> para generar cartones"

st.markdown(f'<div class="counter-box"><span class="{clase}">{msg}</span></div>',
            unsafe_allow_html=True)

# ── Opciones ───────────────────────────────────────────────────────────────────
if n >= CANCIONES_POR_CARTON:
    num_cartones = st.number_input(
        f"Número de cartones a generar (máx. {min(200, max_unicos)})",
        min_value=1,
        max_value=min(200, max_unicos),
        value=min(65, min(200, max_unicos)),
        step=1,
    )
else:
    num_cartones = 0

st.markdown("<br>", unsafe_allow_html=True)

# ── Botón generar ──────────────────────────────────────────────────────────────
puede_generar = n >= CANCIONES_POR_CARTON

if st.button("🖨️  Generar PDF", disabled=not puede_generar, use_container_width=True):
    with st.spinner("Generando PDF... ⏳"):
        try:
            # Foto
            if foto_subida:
                suf = ".jpg" if foto_subida.name.lower().endswith(("jpg", "jpeg")) else ".png"
                tmp_foto = tempfile.NamedTemporaryFile(delete=False, suffix=suf)
                tmp_foto.write(foto_subida.read())
                tmp_foto.flush()
                foto_path = tmp_foto.name
            else:
                foto_path = None

            # PDF
            tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp_pdf.close()

            generar_pdf(
                playlist=playlist_valida,
                foto_path=foto_path,
                output_path=tmp_pdf.name,
                num_cartones=int(num_cartones),
            )

            with open(tmp_pdf.name, "rb") as f:
                pdf_bytes = f.read()

            os.unlink(tmp_pdf.name)
            if foto_subida and foto_path:
                os.unlink(foto_path)

            paginas = -(-int(num_cartones) // 4)
            st.success(f"✔ PDF generado: {num_cartones} cartones en {paginas} páginas")
            st.session_state["pdf_bytes"] = pdf_bytes

        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")

# Botón de descarga (persiste aunque se pulse generar de nuevo)
if "pdf_bytes" in st.session_state:
    st.download_button(
        label="⬇️  Descargar PDF",
        data=st.session_state["pdf_bytes"],
        file_name="bingo_musical.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.markdown("---")
st.caption("Bingo Musical · 2025")
