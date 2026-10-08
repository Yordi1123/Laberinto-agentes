"""Generación de bosques aleatorios mediante Kruskal."""

from __future__ import annotations

import random

from .modelo import (
    DERECHA,
    INFERIOR,
    Celda,
    DIRECCIONES,
    Laberinto,
    Posicion,
    abrir_paso,
)

MAX_COMPONENTES = 3
MAX_CONEXIONES_EXTRA = 4


class _ConjuntosDisjuntos:
    def __init__(self, cantidad: int) -> None:
        self.padre = list(range(cantidad))
        self.rango = [0] * cantidad

    def buscar(self, elemento: int) -> int:
        while elemento != self.padre[elemento]:
            self.padre[elemento] = self.padre[self.padre[elemento]]
            elemento = self.padre[elemento]
        return elemento

    def unir(self, primero: int, segundo: int) -> bool:
        raiz_1, raiz_2 = self.buscar(primero), self.buscar(segundo)
        if raiz_1 == raiz_2:
            return False
        if self.rango[raiz_1] < self.rango[raiz_2]:
            raiz_1, raiz_2 = raiz_2, raiz_1
        self.padre[raiz_2] = raiz_1
        if self.rango[raiz_1] == self.rango[raiz_2]:
            self.rango[raiz_1] += 1
        return True


def _indice(fila: int, columna: int, columnas: int) -> int:
    return fila * columnas + columna


def generar_bosque_aleatorio(
    laberinto: Laberinto,
    rng: random.Random,
    max_componentes: int = MAX_COMPONENTES,
    max_conexiones_extra: int = MAX_CONEXIONES_EXTRA,
) -> None:
    """Construye de uno a tres componentes sin comprobar entrada ni salida."""
    filas, columnas = len(laberinto), len(laberinto[0])
    conexiones: list[tuple[int, int, int, int, int]] = []
    for fila in range(filas):
        for columna in range(columnas):
            if fila + 1 < filas:
                conexiones.append((fila, columna, INFERIOR, fila + 1, columna))
            if columna + 1 < columnas:
                conexiones.append((fila, columna, DERECHA, fila, columna + 1))
    rng.shuffle(conexiones)

    total = filas * columnas
    objetivo = rng.randint(1, min(max_componentes, total))
    componentes = total
    conjuntos = _ConjuntosDisjuntos(total)

    for fila, columna, direccion, vecina_f, vecina_c in conexiones:
        if componentes == objetivo:
            break
        actual = _indice(fila, columna, columnas)
        vecina = _indice(vecina_f, vecina_c, columnas)
        if conjuntos.unir(actual, vecina):
            abrir_paso(laberinto, fila, columna, direccion)
            componentes -= 1

    # Las conexiones extra solo crean ciclos dentro de un componente existente.
    candidatas: list[tuple[int, int, int]] = []
    for fila in range(filas):
        for columna in range(columnas):
            for direccion in (INFERIOR, DERECHA):
                df, dc, pared, _ = DIRECCIONES[direccion]
                vecina_f, vecina_c = fila + df, columna + dc
                if not (0 <= vecina_f < filas and 0 <= vecina_c < columnas):
                    continue
                if not getattr(laberinto[fila][columna], pared):
                    continue
                actual = _indice(fila, columna, columnas)
                vecina = _indice(vecina_f, vecina_c, columnas)
                if conjuntos.buscar(actual) == conjuntos.buscar(vecina):
                    candidatas.append((fila, columna, direccion))

    rng.shuffle(candidatas)
    cantidad = rng.randint(0, min(max_conexiones_extra, len(candidatas)))
    for fila, columna, direccion in candidatas[:cantidad]:
        abrir_paso(laberinto, fila, columna, direccion)


def establecer_entrada_salida(
    laberinto: Laberinto, rng: random.Random
) -> tuple[Posicion, Posicion]:
    filas, columnas = len(laberinto), len(laberinto[0])
    entrada = (0, rng.randrange(columnas))
    salida = (filas - 1, rng.randrange(columnas))
    laberinto[entrada[0]][entrada[1]].pared_superior = False
    laberinto[salida[0]][salida[1]].pared_inferior = False
    return entrada, salida


def crear_laberinto(
    filas: int, columnas: int, semilla: int | None = None
) -> tuple[Laberinto, Posicion, Posicion]:
    """Genera un laberinto sin determinar si entrada y salida están conectadas."""
    if type(filas) is not int or type(columnas) is not int:
        raise TypeError("Las dimensiones deben ser números enteros.")
    if filas <= 0 or columnas <= 0:
        raise ValueError("Las dimensiones deben ser mayores que cero.")

    rng = random.Random(semilla)
    laberinto = [[Celda() for _ in range(columnas)] for _ in range(filas)]
    generar_bosque_aleatorio(laberinto, rng)
    entrada, salida = establecer_entrada_salida(laberinto, rng)
    return laberinto, entrada, salida
