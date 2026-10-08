"""Interfaz Streamlit para generar y explorar laberintos."""

from __future__ import annotations

import streamlit as st

from laberinto import AgenteDFS, AgenteExploradorFronteras, Entorno, crear_laberinto
from laberinto.interfaz_canvas import mostrar_animacion, preparar_animacion

st.set_page_config(page_title="Agentes en un laberinto", page_icon="🧭", layout="wide")

st.markdown(
    """
    <style>
        .block-container {max-width: 1500px; padding-top: 1.4rem; padding-bottom: 2rem;}
        [data-testid="stSidebar"] {min-width: 280px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def generar(filas: int, columnas: int, semilla: int) -> None:
    laberinto, entrada, salida = crear_laberinto(filas, columnas, semilla)
    st.session_state.ejecucion = {
        "laberinto": laberinto,
        "entrada": entrada,
        "salida": salida,
        "eventos": (),
        "informe": None,
        "algoritmo": None,
    }


def ejecutar(nombre: str, semilla: int, limite: int) -> None:
    estado = st.session_state.ejecucion
    entorno = Entorno(estado["laberinto"])
    if nombre == "DFS determinista":
        agente = AgenteDFS(entorno, max_pasos=limite)
    else:
        agente = AgenteExploradorFronteras(
            entorno, max_movimientos=limite, semilla=semilla
        )
    informe, eventos = agente.ejecutar()
    estado.update(
        informe=informe,
        eventos=eventos,
        algoritmo=nombre,
    )


st.title("🧭 Agentes inteligentes en un laberinto")
st.write(
    "Compara una búsqueda DFS exhaustiva con un agente que explora fronteras "
    "sin conocer las dimensiones ni la ubicación de la salida."
)

with st.sidebar:
    st.header("Configuración")
    filas = st.slider("Filas", 2, 30, 15)
    columnas = st.slider("Columnas", 2, 30, 15)
    semilla = st.number_input("Semilla", min_value=0, value=26, step=1)
    algoritmo = st.selectbox(
        "Algoritmo", ("DFS determinista", "Exploración por fronteras")
    )
    limite = st.number_input(
        "Límite de pasos o movimientos", min_value=1, value=100_000, step=1_000
    )
    modo_vista = st.radio(
        "Visualización",
        ("Vista del espectador", "Vista del agente"),
        help="El espectador ve todo el laberinto; la vista del agente oculta lo desconocido.",
    )

    if "ejecucion" not in st.session_state:
        generar(filas, columnas, int(semilla))

    if st.button("Generar laberinto", use_container_width=True, type="primary"):
        generar(filas, columnas, int(semilla))
    if st.button(
        "Ejecutar algoritmo",
        use_container_width=True,
        disabled="ejecucion" not in st.session_state,
    ):
        with st.spinner("Ejecutando el algoritmo y preparando la animación..."):
            ejecutar(algoritmo, int(semilla), int(limite))

estado = st.session_state.ejecucion
datos_animacion = preparar_animacion(
    estado["laberinto"],
    estado["entrada"],
    estado["salida"],
    estado["eventos"],
    estado["informe"],
    estado["algoritmo"],
    vista_agente=modo_vista == "Vista del agente",
)
mostrar_animacion(datos_animacion)
