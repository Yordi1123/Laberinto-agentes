from __future__ import annotations

import pytest

from laberinto import DIRECCIONES, crear_laberinto


def analizar_estructura(laberinto):
    filas, columnas = len(laberinto), len(laberinto[0])
    visitadas = set()
    componentes = 0

    for origen_f in range(filas):
        for origen_c in range(columnas):
            origen = (origen_f, origen_c)
            if origen in visitadas:
                continue
            componentes += 1
            visitadas.add(origen)
            pila = [origen]
            while pila:
                fila, columna = pila.pop()
                for df, dc, pared, _ in DIRECCIONES:
                    vecina = (fila + df, columna + dc)
                    if not (0 <= vecina[0] < filas and 0 <= vecina[1] < columnas):
                        continue
                    if not getattr(laberinto[fila][columna], pared) and vecina not in visitadas:
                        visitadas.add(vecina)
                        pila.append(vecina)

    aristas = 0
    for fila in range(filas):
        for columna in range(columnas):
            if fila + 1 < filas and not laberinto[fila][columna].pared_inferior:
                aristas += 1
            if columna + 1 < columnas and not laberinto[fila][columna].pared_derecha:
                aristas += 1
    ciclos = aristas - filas * columnas + componentes
    return componentes, ciclos


@pytest.mark.parametrize("filas,columnas", [(1, 1), (2, 5), (10, 10), (20, 15)])
def test_kruskal_respeta_limites_estructurales(filas, columnas):
    for semilla in range(20):
        laberinto, _, _ = crear_laberinto(filas, columnas, semilla)
        componentes, ciclos = analizar_estructura(laberinto)
        assert 1 <= componentes <= min(3, filas * columnas)
        assert 0 <= ciclos <= 4


def test_generacion_es_reproducible():
    primero = crear_laberinto(10, 10, 42)
    segundo = crear_laberinto(10, 10, 42)
    assert primero == segundo


def test_paredes_vecinas_son_simetricas():
    laberinto, _, _ = crear_laberinto(15, 15, 8)
    for fila in range(15):
        for columna in range(15):
            if fila + 1 < 15:
                assert (
                    laberinto[fila][columna].pared_inferior
                    == laberinto[fila + 1][columna].pared_superior
                )
            if columna + 1 < 15:
                assert (
                    laberinto[fila][columna].pared_derecha
                    == laberinto[fila][columna + 1].pared_izquierda
                )


@pytest.mark.parametrize("filas,columnas", [(0, 5), (-1, 3), (3, 0)])
def test_dimensiones_invalidas(filas, columnas):
    with pytest.raises(ValueError):
        crear_laberinto(filas, columnas)
