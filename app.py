"""Interfaz Streamlit para generar y explorar laberintos."""

from __future__ import annotations

import math

import streamlit as st

from laberinto import AgenteDFS, AgenteExploradorFronteras, Entorno, crear_laberinto
from laberinto.visualizacion import dibujar_laberinto

st.set_page_config(page_title="Agentes en un laberinto", page_icon="🧭", layout="wide")

st.markdown(
    """
    <style>
        .block-container {max-width: 1500px; padding-top: 1.4rem; padding-bottom: 2rem;}
        [data-testid="stMetric"] {background: #f8fafc; border: 1px solid #e2e8f0;
                                  border-radius: .65rem; padding: .55rem .7rem;}
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
        "paso": 0,
        "reproduciendo": False,
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
        paso=0,
        reproduciendo=True,
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
    modo_vista = st.radio(
        "Visualización",
        ("Vista del espectador", "Vista del agente"),
        help="El espectador ve todo el laberinto; la vista del agente oculta lo desconocido.",
    )
    velocidad = st.slider("Velocidad de animación", 1, 20, 8, format="%d fps")

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
    if estado["eventos"]:
        st.divider()
        st.caption("Controles de reproducción")
        controles = st.columns(3)
        if controles[0].button(
            "▶",
            help="Reproducir",
            disabled=estado["reproduciendo"] or estado["paso"] >= len(estado["eventos"]) - 1,
            use_container_width=True,
        ):
            estado["reproduciendo"] = True
        if controles[1].button(
            "⏸", help="Pausar", disabled=not estado["reproduciendo"], use_container_width=True
        ):
            estado["reproduciendo"] = False
        if controles[2].button("↺", help="Reiniciar", use_container_width=True):
            estado["paso"] = 0
            estado["reproduciendo"] = False

        pasos = st.columns(2)
        if pasos[0].button(
            "← Paso",
            disabled=estado["reproduciendo"] or estado["paso"] == 0,
            use_container_width=True,
        ):
            estado["paso"] -= 1
        if pasos[1].button(
            "Paso →",
            disabled=estado["reproduciendo"] or estado["paso"] >= len(estado["eventos"]) - 1,
            use_container_width=True,
        ):
            estado["paso"] += 1

estado = st.session_state.ejecucion
intervalo = 1 / velocidad if estado["reproduciendo"] and estado["eventos"] else None


@st.fragment(run_every=intervalo)
def mostrar_ejecucion() -> None:
    estado = st.session_state.ejecucion
    eventos = estado["eventos"]
    evento = None
    paso = estado["paso"]

    if eventos:
        paso = min(paso, len(eventos) - 1)
        if not estado["reproduciendo"]:
            paso = st.slider(
                "Paso de la ejecución",
                0,
                len(eventos) - 1,
                paso,
                key=f"paso_manual_{estado['id']}",
            )
            estado["paso"] = paso
        evento = eventos[paso]
        st.progress(
            (paso + 1) / len(eventos),
            text=f"Evento {paso + 1} de {len(eventos)} · {evento.mensaje}",
        )

    col_laberinto, col_metricas = st.columns((4, 1.25), gap="medium")
    with col_laberinto:
        figura = dibujar_laberinto(
            estado["laberinto"],
            estado["entrada"],
            estado["salida"],
            evento,
            vista_agente=modo_vista == "Vista del agente",
        )
        # Respeta el máximo definido por la figura para evitar desbordes verticales.
        st.pyplot(figura, clear_figure=True, use_container_width=False)
        st.caption(
            "🔴 agente · 🔵 visitadas · 🟡 fronteras · 🟣 ruta planificada · "
            "gris: espacio desconocido"
        )

    with col_metricas:
        st.subheader("Estado")
        informe = estado["informe"]
        final_visible = bool(eventos) and paso == len(eventos) - 1
        if informe is None:
            st.info("Laberinto listo. Ejecuta un algoritmo para iniciar la animación.")
        elif not final_visible:
            st.info(f"En ejecución: {evento.tipo.replace('_', ' ')}")
            st.metric("Celdas observadas", len(evento.visitadas))
            if estado["algoritmo"] == "DFS determinista":
                st.metric("Longitud de la ruta actual", len(evento.ruta))
            else:
                st.metric("Fronteras activas", len(evento.fronteras))
                st.metric("Movimientos visibles", max(0, len(evento.trayectoria) - 1))
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
            else:
                st.metric("Celdas visitadas", informe["celdas_visitadas"])
                st.metric("Movimientos", informe["movimientos"])
                st.metric("Replanificaciones", informe["replanificaciones"])
            if informe.get("camino"):
                st.metric("Longitud de la ruta", len(informe["camino"]))

    if estado["reproduciendo"] and eventos:
        if paso >= len(eventos) - 1:
            estado["reproduciendo"] = False
            st.rerun()
        else:
            salto = max(1, math.ceil(len(eventos) / 360))
            estado["paso"] = min(len(eventos) - 1, paso + salto)


mostrar_ejecucion()
