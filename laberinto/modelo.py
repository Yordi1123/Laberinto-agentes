"""Estructuras y operaciones básicas del laberinto."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

Posicion: TypeAlias = tuple[int, int]
Laberinto: TypeAlias = list[list["Celda"]]

SUPERIOR, INFERIOR, IZQUIERDA, DERECHA = range(4)
NOMBRES_DIRECCION = ("arriba", "abajo", "izquierda", "derecha")

# delta_fila, delta_columna, pared propia, pared opuesta
DIRECCIONES = (
    (-1, 0, "pared_superior", "pared_inferior"),
    (1, 0, "pared_inferior", "pared_superior"),
    (0, -1, "pared_izquierda", "pared_derecha"),
    (0, 1, "pared_derecha", "pared_izquierda"),
)


@dataclass(slots=True)
class Celda:
    pared_superior: bool = True
    pared_inferior: bool = True
    pared_izquierda: bool = True
    pared_derecha: bool = True


def abrir_paso(laberinto: Laberinto, fila: int, columna: int, direccion: int) -> None:
    """Abre una pared y su opuesta en la celda vecina."""
    df, dc, propia, opuesta = DIRECCIONES[direccion]
    setattr(laberinto[fila][columna], propia, False)
    setattr(laberinto[fila + df][columna + dc], opuesta, False)
