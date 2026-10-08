"""Interfaz de percepción local utilizada por los agentes."""

from __future__ import annotations

from .modelo import DIRECCIONES, Laberinto, Posicion

Percepcion = tuple[int, str, Posicion | None]


class Entorno:
    def __init__(self, laberinto: Laberinto) -> None:
        if not laberinto or not laberinto[0]:
            raise ValueError("El laberinto no puede estar vacío.")
        self._laberinto = laberinto
        self._filas = len(laberinto)
        self._columnas = len(laberinto[0])

    def entradas(self) -> list[Posicion]:
        """Devuelve las aberturas del borde superior."""
        return [
            (0, columna)
            for columna in range(self._columnas)
            if not self._laberinto[0][columna].pared_superior
        ]

    def percibir(self, posicion: Posicion) -> list[Percepcion]:
        """Informa solo los pasillos y aberturas visibles desde una celda."""
        fila, columna = posicion
        if not (0 <= fila < self._filas and 0 <= columna < self._columnas):
            raise ValueError(f"Posición fuera del laberinto: {posicion}")

        percepciones: list[Percepcion] = []
        celda = self._laberinto[fila][columna]
        for direccion, (df, dc, pared, _) in enumerate(DIRECCIONES):
            if getattr(celda, pared):
                continue
            vecina = (fila + df, columna + dc)
            if 0 <= vecina[0] < self._filas and 0 <= vecina[1] < self._columnas:
                percepciones.append((direccion, "celda", vecina))
            else:
                percepciones.append((direccion, "borde", None))
        return percepciones
