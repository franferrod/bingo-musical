"""
Bingo Musical — App web para generar el PDF de cartones.
Optimizada para móvil.
"""
import io, os, tempfile, math
import streamlit as st
from generar_bingo import PLAYLIST as PLAYLIST_DEFAULT, generar_pdf, CANCIONES_POR_CARTON

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

/* Botón secundario (Añadir / Eliminar) */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: white; color: #1A4A2E; border: 1.5px solid #1A4A2E;
    border-radius: 8px; font-weight: bold;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover { background: #F0EBD8; border-color: #1A4A2E; color: #1A4A2E; }

/* Botón primario (Generar) */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #1A4A2E; color: white; border: none;
    border-radius: 8px; font-weight: bold; font-size: 1.1rem;
    padding: 0.6rem;
}
div[data-testid="stButton"] > button[kind="primary"]:hover { background: #133822; }

/* Botón Descargar PDF */
div[data-testid="stDownloadButton"] > button {
    background: #B8872A !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-size: 1.1rem !important; font-weight: bold !important;
    width: 100%; padding: 0.8rem !important;
}
div[data-testid="stDownloadButton"] > button:hover { background: #966C20 !important; }

.counter-box {
    background: #F0EBD8; border: 1px solid #C8B878;
    border-radius: 8px; padding: 0.8rem 1rem;
    text-align: center; margin: 0.8rem 0;
}
.counter-ok  { color: #1A4A2E; font-weight: bold; font-size: 1.1rem; }
.counter-err  { color: #C0392B; font-weight: bold; }

/* Ajustes para móvil */
@media (max-width: 640px) {
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    h1 { font-size: 2rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Título ─────────────────────────────────────────────────────────────────────
st.markdown("<h1>🎵 Bingo Musical</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">60 cumpleaños de Paco y Mariadel</p>', unsafe_allow_html=True)

# ── Estado de la sesión ────────────────────────────────────────────────────────
if "canciones" not in st.session_state:
    st.session_state.canciones = [
        {"titulo": t, "artista": a} for t, a in PLAYLIST_DEFAULT
    ]

canciones = st.session_state.canciones

# ── Foto ───────────────────────────────────────────────────────────────────────
st.markdown("### 📷 Foto central")
foto_subida = st.file_uploader(
    "Sube una foto (opcional)",
    type=["jpg", "jpeg", "png"],
    label_visibility="visible",
    help="Se usará la foto de Paco y Mariadel por defecto si no subes ninguna."
)
if foto_subida:
    st.image(foto_subida, width=150)

st.markdown("---")

# ── Lista de canciones ─────────────────────────────────────────────────────────
st.markdown("### 🎶 Canciones del bingo")
st.caption("Añade, edita o elimina canciones. Necesitas mínimo 8 para generar al menos 1 cartón.")

if st.button("➕ Añadir canción", use_container_width=True):
    # Insertar al principio para no tener que hacer scroll hacia abajo
    st.session_state.canciones.insert(0, {"titulo": "", "artista": ""})
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

indices_a_borrar = []
for i, cancion in enumerate(canciones):
    with st.container(border=True):
        st.markdown(f"<div style='color:#1A4A2E; font-weight:bold; margin-bottom:0.5rem;'>🎵 Canción {i+1}</div>", unsafe_allow_html=True)
        st.session_state.canciones[i]["titulo"] = st.text_input(
            f"titulo_{i}", value=cancion["titulo"],
            placeholder="Título de la canción",
            label_visibility="collapsed"
        )
        st.session_state.canciones[i]["artista"] = st.text_input(
            f"artista_{i}", value=cancion["artista"],
            placeholder="Artista de la canción",
            label_visibility="collapsed"
        )
        if st.button("🗑️ Eliminar", key=f"del_{i}", use_container_width=True):
            indices_a_borrar.append(i)

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

if n >= CANCIONES_POR_CARTON:
    max_unicos = math.comb(n, CANCIONES_POR_CARTON)
    clase = "counter-ok"
    msg = f"✔ {n} canciones <br> <span style='font-size:0.9rem; font-weight:normal;'>Hasta <b>{max_unicos:,}</b> cartones únicos posibles</span>"
else:
    max_unicos = 0
    clase = "counter-err"
    msg = f"✘ {n} canciones <br> <span style='font-size:0.9rem; font-weight:normal;'>Necesitas al menos <b>{CANCIONES_POR_CARTON}</b></span>"

st.markdown(f'<div class="counter-box"><div class="{clase}">{msg}</div></div>',
            unsafe_allow_html=True)

# ── Opciones ───────────────────────────────────────────────────────────────────
if n >= CANCIONES_POR_CARTON:
    num_cartones = st.number_input(
        f"Número de cartones a generar",
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

if st.button("🖨️ Generar PDF", type="primary", disabled=not puede_generar, use_container_width=True):
    with st.spinner("Generando PDF... ⏳"):
        try:
            if foto_subida:
                suf = ".jpg" if foto_subida.name.lower().endswith(("jpg", "jpeg")) else ".png"
                tmp_foto = tempfile.NamedTemporaryFile(delete=False, suffix=suf)
                tmp_foto.write(foto_subida.read())
                tmp_foto.flush()
                foto_path = tmp_foto.name
            else:
                foto_path = None

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

if "pdf_bytes" in st.session_state:
    st.download_button(
        label="⬇️ Descargar PDF",
        data=st.session_state["pdf_bytes"],
        file_name="bingo_musical.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.markdown("---")
st.caption("Bingo Musical · 2025")
