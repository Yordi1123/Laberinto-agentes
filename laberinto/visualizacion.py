"""Renderizado del laberinto y de los eventos de búsqueda."""

from __future__ import annotations

import matplotlib

# Streamlit renderiza las figuras en memoria; no necesita una ventana de escritorio.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from .eventos import Evento
from .modelo import Laberinto, Posicion

COLORES = {
    "desconocida": "#263238",
    "libre": "#ffffff",
    "visitada": "#b3e5fc",
    "frontera": "#ffd166",
    "ruta": "#c4b5fd",
    "agente": "#ef476f",
}


def dibujar_laberinto(
    laberinto: Laberinto,
    entrada: Posicion,
    salida: Posicion,
    evento: Evento | None = None,
    vista_agente: bool = False,
) -> Figure:
    """Crea una figura completa o limitada al conocimiento del agente."""
    filas, columnas = len(laberinto), len(laberinto[0])
    visitadas = set(evento.visitadas) if evento else set()
    fronteras = set(evento.fronteras) if evento else set()
    ruta = set(evento.ruta) if evento else set()
    conocidas = visitadas | fronteras | {entrada}
    salida_visible = not vista_agente or (
        evento is not None and evento.tipo == "salida" and evento.posicion == salida
    )

    # Mantiene el laberinto completo dentro de una pantalla convencional.
    escala = min(0.55, 9 / columnas, 6.8 / filas)
    ancho = max(4.5, columnas * escala)
    alto = max(4, filas * escala)
    figura, eje = plt.subplots(figsize=(ancho, alto))

    for fila in range(filas):
        for columna in range(columnas):
            posicion = (fila, columna)
            x, y = columna, filas - fila - 1
            color = COLORES["libre"]
            if vista_agente and posicion not in conocidas:
                color = COLORES["desconocida"]
            elif posicion in visitadas:
                color = COLORES["visitada"]
            if posicion in fronteras:
                color = COLORES["frontera"]
            if posicion in ruta:
                color = COLORES["ruta"]
            if evento and posicion == evento.posicion:
                color = COLORES["agente"]
            eje.add_patch(Rectangle((x, y), 1, 1, facecolor=color, edgecolor="none"))

            if vista_agente and posicion not in conocidas:
                continue
            celda = laberinto[fila][columna]
            if celda.pared_superior:
                eje.plot((x, x + 1), (y + 1, y + 1), color="#111827", linewidth=1.6)
            if celda.pared_inferior:
                eje.plot((x, x + 1), (y, y), color="#111827", linewidth=1.6)
            if celda.pared_izquierda:
                eje.plot((x, x), (y, y + 1), color="#111827", linewidth=1.6)
            if celda.pared_derecha:
                eje.plot((x + 1, x + 1), (y, y + 1), color="#111827", linewidth=1.6)

    # Entrada y salida se colocan en una esquina para no tapar al agente.
    _etiqueta(eje, entrada, filas, "S", "#0f766e", centrada=False)
    if salida_visible:
        _etiqueta(eje, salida, filas, "E", "#15803d", centrada=False)
    if evento and evento.posicion is not None:
        _etiqueta(eje, evento.posicion, filas, "A", "#ffffff")

    titulo = "Laberinto generado"
    if evento:
        titulo = f"Paso: {evento.tipo.replace('_', ' ').title()}"
    eje.set_title(titulo, fontsize=13, fontweight="bold", pad=10)
    eje.set_xlim(0, columnas)
    eje.set_ylim(0, filas)
    eje.set_aspect("equal")
    eje.axis("off")
    figura.tight_layout()
    return figura


def _etiqueta(
    eje,
    posicion: Posicion,
    filas: int,
    texto: str,
    color: str,
    centrada: bool = True,
) -> None:
    fila, columna = posicion
    x = columna + (0.5 if centrada else 0.17)
    y = filas - fila - (0.5 if centrada else 0.18)
    eje.text(
        x,
        y,
        texto,
        ha="center" if centrada else "left",
        va="center" if centrada else "top",
        color=color,
        fontsize=10 if centrada else 8,
        fontweight="bold",
        zorder=5,
    )
