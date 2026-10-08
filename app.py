"""Interfaz Streamlit para generar y explorar laberintos."""

from __future__ import annotations

import streamlit as st

from laberinto import AgenteDFS, AgenteAStar, Entorno, crear_laberinto
from laberinto.interfaz_canvas import mostrar_animacion, preparar_animacion

DFS = "DFS determinista"
A_STAR = "A* no determinista"
COMPARAR = "Comparar ambos"

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
        "ejecuciones": [],
    }


def ejecutar(nombre: str, semilla: int, limite: int) -> None:
    estado = st.session_state.ejecucion
    seleccionados = (DFS, A_STAR) if nombre == COMPARAR else (nombre,)
    ejecuciones = []

    for seleccionado in seleccionados:
        entorno = Entorno(estado["laberinto"])
        agente = (
            AgenteDFS(entorno, max_pasos=limite)
            if seleccionado == DFS
            else AgenteAStar(
                entorno, salida=estado["salida"], max_pasos=limite, semilla=semilla
            )
        )
        informe, eventos = agente.ejecutar()
        ejecuciones.append(
            {"algoritmo": seleccionado, "informe": informe, "eventos": eventos}
        )

    estado["ejecuciones"] = ejecuciones


st.title("🧭 Agentes inteligentes en un laberinto")
st.write(
    "Compara una búsqueda DFS determinista exhaustiva con un algoritmo A* heuristico que evalúa la ruta óptima de manera no determinista."
)

with st.sidebar:
    st.header("Configuración")
    filas = st.slider("Filas", 2, 30, 15)
    columnas = st.slider("Columnas", 2, 30, 15)
    semilla = st.number_input("Semilla", min_value=0, value=26, step=1)
    algoritmo = st.selectbox("Algoritmo", (DFS, A_STAR, COMPARAR))
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
        "Ejecutar comparación" if algoritmo == COMPARAR else "Ejecutar algoritmo",
        use_container_width=True,
        disabled="ejecucion" not in st.session_state,
    ):
        with st.spinner("Ejecutando el algoritmo y preparando la animación..."):
            ejecutar(algoritmo, int(semilla), int(limite))

estado = st.session_state.ejecucion
ejecuciones = estado["ejecuciones"]


def datos_de(ejecucion=None):
    return preparar_animacion(
        estado["laberinto"],
        estado["entrada"],
        estado["salida"],
        ejecucion["eventos"] if ejecucion else (),
        ejecucion["informe"] if ejecucion else None,
        ejecucion["algoritmo"] if ejecucion else None,
        vista_agente=modo_vista == "Vista del agente",
        modo_comparacion=len(ejecuciones) > 1,
    )


if not ejecuciones:
    mostrar_animacion(datos_de())
elif len(ejecuciones) == 1:
    mostrar_animacion(datos_de(ejecuciones[0]))
else:
    st.subheader("Comparación simultánea")
    st.caption(
        "Ambos reproductores comienzan juntos y usan la misma velocidad inicial. "
        "Cada uno conserva controles independientes para inspeccionar sus eventos."
    )
    columnas_comparacion = st.columns(2, gap="medium")
    for columna, ejecucion in zip(columnas_comparacion, ejecuciones):
        with columna:
            st.markdown(f"#### {ejecucion['algoritmo']}")
            mostrar_animacion(datos_de(ejecucion))

    st.subheader("Resumen de resultados")
    st.caption(
        "Las expansiones representan nodos procesados por los algoritmos."
    )
    resumen = []
    for ejecucion in ejecuciones:
        informe = ejecucion["informe"]
        resumen.append(
            {
                "Algoritmo": ejecucion["algoritmo"],
                "Solución": "Sí" if informe["tiene_solucion"] else "No",
                "Rutas encontradas": informe.get("total_caminos", 0),
                "Longitud de ruta": len(informe.get("camino") or []),
                "Celdas observadas": informe.get("celdas_visitadas", 0),
                "Expansiones internas": informe.get("expandidas", 0),
                "Movimientos": informe.get("pasos", None),
                "Podas": informe.get("podas", None),
                "Retrocesos": informe.get("retrocesos", None),
            }
        )
    st.dataframe(resumen, hide_index=True, use_container_width=True)
