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

# ── Estado de la sesión ────────────────────────────────────────────────────────
if "titulo_carton" not in st.session_state:
    st.session_state.titulo_carton = "60 cumpleaños de Paco y Mariadel"

if "canciones" not in st.session_state:
    st.session_state.canciones = [
        {"titulo": t, "artista": a} for t, a in PLAYLIST_DEFAULT
    ]

# Contador de versión: al cambiarlo, todas las claves de widget de canciones
# se regeneran con nombres nuevos, evitando que Streamlit restaure valores viejos.
if "ver" not in st.session_state:
    st.session_state.ver = 0

st.markdown('<p class="subtitle">' + st.session_state.titulo_carton + '</p>',
            unsafe_allow_html=True)

st.info("""
**👋 ¡Hola! Pasos rápidos:**
1. 📷 **Sube la foto** que irá en el centro del cartón (opcional).
2. 🖨️ **Elige cuántos cartones** quieres generar.
3. 🎵 Revisa la **lista de canciones** abajo si quieres cambiar alguna.
4. Pulsa **"Generar PDF"** y descarga el archivo listo para imprimir.
""")

canciones = st.session_state.canciones
ver = st.session_state.ver  # versión actual para las claves de widget

# ── Título del cartón ──────────────────────────────────────────────────────────
st.markdown("### ✏️ Título del cartón")
titulo_input = st.text_input(
    "Título que aparecerá en los cartones",
    value=st.session_state.titulo_carton,
    placeholder="Escribe el título del evento",
    key="titulo_carton_input",
    help="Este texto aparecerá en el óvalo dorado de cada cartón.",
)
if titulo_input != st.session_state.titulo_carton:
    st.session_state.titulo_carton = titulo_input
    st.rerun()

st.markdown("---")

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

# ───────────────────────────────────────────────────────────────────────────────
# 🖨️ ZONA DE GENERACIÓN
# ───────────────────────────────────────────────────────────────────────────────
st.markdown("### 🖨️ Generar Bingo")

# Leer valores actuales de los widgets de canciones para calcular la playlist válida
playlist_valida = []
for i, c in enumerate(canciones):
    t = st.session_state.get(f"t_{ver}_{i}", c["titulo"]).strip()
    a = st.session_state.get(f"a_{ver}_{i}", c["artista"]).strip()
    if t and a:
        playlist_valida.append((t, a))

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
                titulo=st.session_state.titulo_carton,
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

# ───────────────────────────────────────────────────────────────────────────────
# 🎶 LISTA DE CANCIONES
# ───────────────────────────────────────────────────────────────────────────────
st.markdown("### 🎶 Canciones del bingo")
st.caption("Añade, edita o elimina canciones. Necesitas mínimo 8 para generar al menos 1 cartón.")


# ── Callbacks para Añadir y Eliminar ──────────────────────────────────────────
def _sync_widgets_to_list():
    """Copia los valores actuales de los widgets de texto a la lista de canciones."""
    for i, c in enumerate(st.session_state.canciones):
        c["titulo"] = st.session_state.get(f"t_{ver}_{i}", c["titulo"])
        c["artista"] = st.session_state.get(f"a_{ver}_{i}", c["artista"])


def _add_song():
    _sync_widgets_to_list()
    st.session_state.canciones.insert(0, {"titulo": "", "artista": ""})
    st.session_state.ver += 1  # nueva versión → claves nuevas


def _delete_song(idx):
    _sync_widgets_to_list()
    st.session_state.canciones.pop(idx)
    st.session_state.ver += 1  # nueva versión → claves nuevas


st.button("➕ Añadir canción", use_container_width=True, on_click=_add_song)

st.markdown("<br>", unsafe_allow_html=True)

for i, cancion in enumerate(canciones):
    with st.container(border=True):
        st.markdown(f"<div style='color:#1A4A2E; font-weight:bold; margin-bottom:0.5rem;'>🎵 Canción {i+1}</div>", unsafe_allow_html=True)
        st.text_input(
            f"titulo_{ver}_{i}", value=cancion["titulo"],
            placeholder="Título de la canción",
            label_visibility="collapsed",
            key=f"t_{ver}_{i}"
        )
        st.text_input(
            f"artista_{ver}_{i}", value=cancion["artista"],
            placeholder="Artista de la canción",
            label_visibility="collapsed",
            key=f"a_{ver}_{i}"
        )
        st.button("🗑️ Eliminar", key=f"del_{ver}_{i}", use_container_width=True,
                   on_click=_delete_song, args=(i,))

st.markdown("---")
st.caption("Bingo Musical · 2025")
