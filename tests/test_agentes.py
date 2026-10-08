from __future__ import annotations

from collections import deque

import pytest

from laberinto import (
    AgenteDFS,
    AgenteAStar,
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
    fronteras = AgenteAStar(
        Entorno(laberinto), salida=salida, semilla=semilla
    ).resolver()

    assert dfs["tiene_solucion"] == esperado
    assert fronteras["tiene_solucion"] == esperado
    if esperado:
        assert dfs["camino"][0] == entrada
        assert dfs["camino"][-1] == salida
        assert fronteras["camino"][0] == entrada and fronteras["camino"][-1] == salida
        assert ruta_valida(laberinto, dfs["camino"])
        assert ruta_valida(laberinto, fronteras["camino"])


@pytest.mark.parametrize("semilla", range(20))
def test_dfs_devuelve_ruta_minima_entre_todas_las_rutas(semilla):
    laberinto, entrada, _ = crear_laberinto(12, 12, semilla)
    informe, eventos = AgenteDFS(Entorno(laberinto)).ejecutar()

    if informe["tiene_solucion"]:
        distancias = {entrada: 1}
        cola = deque([entrada])
        longitud_minima = None
        entorno = Entorno(laberinto)
        while cola and longitud_minima is None:
            posicion = cola.popleft()
            for direccion, tipo, destino in entorno.percibir(posicion):
                if tipo == "borde" and not (
                    posicion == entrada and direccion == 0
                ):
                    longitud_minima = distancias[posicion]
                    break
                if tipo != "borde" and destino not in distancias:
                    distancias[destino] = distancias[posicion] + 1
                    cola.append(destino)
        assert len(informe["camino"]) == longitud_minima
        assert eventos[-1].ruta == tuple(informe["camino"])


def test_dfs_registra_podas_y_conserva_el_mejor_camino_al_final():
    laberinto, _, _ = crear_laberinto(15, 15, semilla=26)
    informe, eventos = AgenteDFS(Entorno(laberinto)).ejecutar()

    assert informe["podas"] > 0
    assert eventos[-1].tipo == "final"
    if informe["tiene_solucion"]:
        assert eventos[-1].ruta == tuple(informe["camino"])


def test_ejecucion_genera_eventos_reproducibles():
    laberinto, _, salida = crear_laberinto(10, 10, 19)
    agente = AgenteAStar(Entorno(laberinto), salida=salida, semilla=7)
    informe_1, eventos_1 = agente.ejecutar()
    informe_2, eventos_2 = agente.ejecutar()
    assert informe_1 == informe_2
    assert eventos_1 == eventos_2
    assert eventos_1[0].tipo == "inicio"
    assert eventos_1[-1].tipo in {"salida", "sin_solucion", "final"}


def test_truncamiento_es_inconcluso():
    laberinto, _, salida = crear_laberinto(15, 15, 2)
    informe = AgenteAStar(
        Entorno(laberinto), salida=salida, max_pasos=1, semilla=0
    ).resolver()
    assert informe["truncado"]
    assert informe["motivo_truncado"] == "límite de pasos alcanzado"
