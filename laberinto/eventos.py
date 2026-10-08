"""Instantáneas independientes de la interfaz gráfica."""

from __future__ import annotations

from dataclasses import dataclass

from .modelo import Posicion


@dataclass(frozen=True, slots=True)
class Evento:
    tipo: str
    posicion: Posicion | None = None
    visitadas: frozenset[Posicion] = frozenset()
    ruta: tuple[Posicion, ...] = ()
    mensaje: str = ""
