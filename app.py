"""Interfaz Streamlit para generar y explorar laberintos."""

from __future__ import annotations

import streamlit as st

from laberinto import AgenteDFS, AgenteExploradorFronteras, Entorno, crear_laberinto
from laberinto.visualizacion import dibujar_laberinto

st.set_page_config(page_title="Agentes en un laberinto", page_icon="🧭", layout="wide")


def generar(filas: int, columnas: int, semilla: int) -> None:
    laberinto, entrada, salida = crear_laberinto(filas, columnas, semilla)
    st.session_state.ejecucion = {
        "laberinto": laberinto,
        "entrada": entrada,
        "salida": salida,
        "eventos": (),
        "informe": None,
        "algoritmo": None,
        "id": st.session_state.get("id_ejecucion", 0) + 1,
    }
    st.session_state.id_ejecucion = st.session_state.ejecucion["id"]


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
        id=estado["id"] + 1,
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
    vista_agente = st.toggle("Mostrar solo lo conocido por el agente", value=True)

    if "ejecucion" not in st.session_state:
        generar(filas, columnas, int(semilla))

    if st.button("Generar laberinto", use_container_width=True, type="primary"):
        generar(filas, columnas, int(semilla))
    if st.button(
        "Ejecutar algoritmo",
        use_container_width=True,
        disabled="ejecucion" not in st.session_state,
    ):
        ejecutar(algoritmo, int(semilla), int(limite))

estado = st.session_state.ejecucion
eventos = estado["eventos"]
evento = None
if eventos:
    paso = st.slider(
        "Paso de la ejecución",
        0,
        len(eventos) - 1,
        0,
        key=f"paso_{estado['id']}",
    )
    evento = eventos[paso]
    st.caption(f"{paso + 1} de {len(eventos)} — {evento.mensaje}")

col_laberinto, col_metricas = st.columns((3, 1), gap="large")
with col_laberinto:
    figura = dibujar_laberinto(
        estado["laberinto"],
        estado["entrada"],
        estado["salida"],
        evento,
        vista_agente,
    )
    st.pyplot(figura, clear_figure=True)
    st.caption(
        "🔴 agente · 🔵 visitadas · 🟡 fronteras · 🟣 ruta planificada · "
        "gris: espacio desconocido"
    )

with col_metricas:
    st.subheader("Resultados")
    informe = estado["informe"]
    if informe is None:
        st.info("Ejecuta un algoritmo para obtener métricas.")
    else:
        if informe["truncado"]:
            st.warning(f"Resultado inconcluso: {informe['motivo_truncado']}")
        elif informe["tiene_solucion"]:
            st.success("Salida encontrada")
        else:
            st.error("No existe una ruta accesible a la salida")

        st.metric("Celdas expandidas", informe["expandidas"])
        if estado["algoritmo"] == "DFS determinista":
            st.metric("Caminos encontrados", informe["total_caminos"])
            st.metric("Retrocesos", informe["retrocesos"])
            st.metric("Opciones evaluadas", informe["pasos"])
        else:
            st.metric("Celdas visitadas", informe["celdas_visitadas"])
            st.metric("Movimientos", informe["movimientos"])
            st.metric("Replanificaciones", informe["replanificaciones"])

        camino = informe.get("camino")
        if camino:
            st.metric("Longitud de la ruta", len(camino))
