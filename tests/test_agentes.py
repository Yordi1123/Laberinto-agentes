from __future__ import annotations

from collections import deque

import pytest

from laberinto import (
    AgenteDFS,
    AgenteExploradorFronteras,
    DIRECCIONES,
    Entorno,
    crear_laberinto,
)


def existe_solucion(laberinto, entrada):
    filas, columnas = len(laberinto), len(laberinto[0])
    cola = deque([entrada])
    visitadas = {entrada}
    while cola:
        fila, columna = cola.popleft()
        for direccion, (df, dc, pared, _) in enumerate(DIRECCIONES):
            if getattr(laberinto[fila][columna], pared):
                continue
            vecina = (fila + df, columna + dc)
            if not (0 <= vecina[0] < filas and 0 <= vecina[1] < columnas):
                if not ((fila, columna) == entrada and direccion == 0):
                    return True
            elif vecina not in visitadas:
                visitadas.add(vecina)
                cola.append(vecina)
    return False


def ruta_valida(laberinto, ruta):
    if not ruta:
        return False
    for (fila, columna), (vecina_f, vecina_c) in zip(ruta, ruta[1:]):
        delta = (vecina_f - fila, vecina_c - columna)
        direccion = next(
            (d for d, (df, dc, _, _) in enumerate(DIRECCIONES) if (df, dc) == delta),
            None,
        )
        if direccion is None:
            return False
        pared = DIRECCIONES[direccion][2]
        if getattr(laberinto[fila][columna], pared):
            return False
    return True


@pytest.mark.parametrize("semilla", range(40))
def test_agentes_coinciden_sobre_existencia_de_solucion(semilla):
    laberinto, entrada, salida = crear_laberinto(12, 12, semilla)
    esperado = existe_solucion(laberinto, entrada)

    dfs = AgenteDFS(Entorno(laberinto)).resolver()
    fronteras = AgenteExploradorFronteras(
        Entorno(laberinto), semilla=semilla
    ).resolver()

    assert dfs["tiene_solucion"] == esperado
    assert fronteras["tiene_solucion"] == esperado
    if esperado:
        assert dfs["camino"][0] == entrada and dfs["camino"][-1] == salida
        assert fronteras["camino"][0] == entrada and fronteras["camino"][-1] == salida
        assert ruta_valida(laberinto, dfs["camino"])
        assert ruta_valida(laberinto, fronteras["camino"])


def test_ejecucion_genera_eventos_reproducibles():
    laberinto, _, _ = crear_laberinto(10, 10, 19)
    agente = AgenteExploradorFronteras(Entorno(laberinto), semilla=7)
    informe_1, eventos_1 = agente.ejecutar()
    informe_2, eventos_2 = agente.ejecutar()
    assert informe_1 == informe_2
    assert eventos_1 == eventos_2
    assert eventos_1[0].tipo == "inicio"
    assert eventos_1[-1].tipo in {"salida", "sin_solucion"}


def test_truncamiento_es_inconcluso():
    laberinto, _, _ = crear_laberinto(15, 15, 2)
    informe = AgenteExploradorFronteras(
        Entorno(laberinto), max_movimientos=1, semilla=0
    ).resolver()
    assert informe["truncado"]
    assert informe["motivo_truncado"] == "límite de movimientos alcanzado"
