"""Búsqueda BFS determinista y exploración estocástica por fronteras."""

from __future__ import annotations

import heapq
import random
from collections import deque
from typing import Any

from .entorno import Entorno
from .eventos import Evento
from .modelo import Posicion, SUPERIOR

Informe = dict[str, Any]


class AgenteBusquedaDeterminista:
    """Encuentra un camino mínimo mediante búsqueda en anchura (BFS)."""

    def __init__(self, entorno: Entorno, max_pasos: int = 5_000_000) -> None:
        if type(max_pasos) is not int or max_pasos <= 0:
            raise ValueError("max_pasos debe ser un entero positivo.")
        self.entorno = entorno
        self.max_pasos = max_pasos
        self._reiniciar(False)

    def _reiniciar(self, registrar_eventos: bool) -> None:
        self.entrada: Posicion | None = None
        self.salida: tuple[Posicion, int] | None = None
        self.camino: list[Posicion] | None = None
        self.exploradas: set[Posicion] = set()
        self.descubiertas: set[Posicion] = set()
        self.padres: dict[Posicion, Posicion | None] = {}
        self.pasos = self.expandidas = 0
        self.truncado = False
        self.motivo_truncado: str | None = None
        self._registrar_eventos = registrar_eventos
        self.eventos: list[Evento] = []

    def resolver(self) -> Informe:
        return self._resolver(False)

    def ejecutar(self) -> tuple[Informe, tuple[Evento, ...]]:
        informe = self._resolver(True)
        return informe, tuple(self.eventos)

    def _emitir(
        self,
        tipo: str,
        posicion: Posicion | None,
        ruta: list[Posicion],
        fronteras: deque[Posicion],
        mensaje: str,
    ) -> None:
        if self._registrar_eventos:
            self.eventos.append(
                Evento(
                    tipo=tipo,
                    posicion=posicion,
                    visitadas=frozenset(self.exploradas),
                    fronteras=frozenset(fronteras),
                    ruta=tuple(ruta),
                    mensaje=mensaje,
                )
            )

    def _resolver(self, registrar_eventos: bool) -> Informe:
        self._reiniciar(registrar_eventos)
        entradas = self.entorno.entradas()
        if not entradas:
            return self._informe()

        self.entrada = entradas[0]
        frontera = deque([self.entrada])
        self.descubiertas.add(self.entrada)
        self.padres[self.entrada] = None
        self._emitir(
            "inicio",
            self.entrada,
            [self.entrada],
            frontera,
            "Inicio de la búsqueda en anchura",
        )

        while frontera:
            if self.expandidas >= self.max_pasos:
                self.truncado = True
                self.motivo_truncado = "límite de expansiones alcanzado"
                posicion = frontera[0]
                self._emitir(
                    "truncado",
                    posicion,
                    self._reconstruir(posicion),
                    frontera,
                    self.motivo_truncado,
                )
                break

            posicion = frontera.popleft()
            self.exploradas.add(posicion)
            self.expandidas += 1
            self.pasos = self.expandidas
            ruta = self._reconstruir(posicion)

            for direccion, tipo, destino in self.entorno.percibir(posicion):
                if tipo == "borde":
                    if posicion == self.entrada and direccion == SUPERIOR:
                        continue
                    self.salida = (posicion, direccion)
                    self.camino = ruta
                    self._emitir(
                        "salida",
                        posicion,
                        ruta,
                        frontera,
                        "Salida encontrada por el camino más corto",
                    )
                    return self._informe()

                assert destino is not None
                if destino not in self.descubiertas:
                    self.descubiertas.add(destino)
                    self.padres[destino] = posicion
                    frontera.append(destino)

            self._emitir(
                "expandir",
                posicion,
                ruta,
                frontera,
                "Celda expandida; nuevas vecinas agregadas a la frontera",
            )

        if not self.truncado:
            self._emitir(
                "sin_solucion",
                None,
                [],
                frontera,
                "Se agotaron todas las celdas accesibles",
            )
        return self._informe()

    def _reconstruir(self, posicion: Posicion) -> list[Posicion]:
        camino = []
        actual: Posicion | None = posicion
        while actual is not None:
            camino.append(actual)
            actual = self.padres[actual]
        return camino[::-1]

    def _informe(self) -> Informe:
        return {
            "algoritmo": "Búsqueda determinista (BFS)",
            "entrada": self.entrada,
            "salida": self.salida,
            "camino": self.camino,
            "tiene_solucion": self.salida is not None,
            "pasos": self.pasos,
            "expandidas": self.expandidas,
            "celdas_descubiertas": len(self.descubiertas),
            "truncado": self.truncado,
            "motivo_truncado": self.motivo_truncado,
        }

class AgenteExploradorFronteras:
    """Explora sin conocer dimensiones ni ubicación de la salida."""

    def __init__(
        self,
        entorno: Entorno,
        max_movimientos: int = 5_000_000,
        semilla: int | None = None,
    ) -> None:
        if type(max_movimientos) is not int or max_movimientos <= 0:
            raise ValueError("max_movimientos debe ser un entero positivo.")
        self.entorno = entorno
        self.max_movimientos = max_movimientos
        self.semilla = semilla
        self._reiniciar(False)

    def _reiniciar(self, registrar_eventos: bool) -> None:
        self.rng = random.Random(self.semilla)
        self.entrada: Posicion | None = None
        self.posicion: Posicion | None = None
        self.salida: tuple[Posicion, int] | None = None
        self.mapa: dict[Posicion, set[Posicion]] = {}
        self.visitadas: set[Posicion] = set()
        self.fronteras: set[Posicion] = set()
        self.trayectoria: list[Posicion] = []
        self.movimientos = self.replanificaciones = self.expandidas = 0
        self.truncado = False
        self.motivo_truncado: str | None = None
        self._registrar_eventos = registrar_eventos
        self.eventos: list[Evento] = []

    def resolver(self) -> Informe:
        return self._resolver(False)

    def ejecutar(self) -> tuple[Informe, tuple[Evento, ...]]:
        informe = self._resolver(True)
        return informe, tuple(self.eventos)

    def _emitir(self, tipo: str, ruta: list[Posicion] | None, mensaje: str) -> None:
        if self._registrar_eventos:
            self.eventos.append(
                Evento(
                    tipo=tipo,
                    posicion=self.posicion,
                    visitadas=frozenset(self.visitadas),
                    fronteras=frozenset(self.fronteras),
                    ruta=tuple(ruta or ()),
                    trayectoria=tuple(self.trayectoria),
                    mensaje=mensaje,
                )
            )

    def _resolver(self, registrar_eventos: bool) -> Informe:
        self._reiniciar(registrar_eventos)
        entradas = self.entorno.entradas()
        if not entradas:
            return self._informe(None)

        self.entrada = self.rng.choice(entradas)
        self.posicion = self.entrada
        self.trayectoria = [self.entrada]
        self._emitir("inicio", [self.entrada], "Inicio de la exploración")

        while True:
            direccion_salida = self._percibir_actual()
            if direccion_salida is not None:
                self.salida = (self.posicion, direccion_salida)
                camino = self._ruta_conocida(self.entrada, self.posicion)
                self._emitir("salida", camino, "Salida descubierta mediante percepción local")
                return self._informe(camino)
            if not self.fronteras:
                self._emitir("sin_solucion", None, "Se agotaron todas las fronteras accesibles")
                return self._informe(None)

            objetivo = self._seleccionar_frontera()
            ruta = self._ruta_conocida(self.posicion, objetivo)
            self.replanificaciones += 1
            if ruta is None:
                self.truncado = True
                self.motivo_truncado = "frontera inaccesible en el mapa conocido"
                self._emitir("truncado", None, self.motivo_truncado)
                return self._informe(None)
            self._emitir("planificar", ruta, f"Frontera seleccionada: {objetivo}")
            if not self._seguir(ruta):
                return self._informe(None)

    def _percibir_actual(self) -> int | None:
        assert self.posicion is not None and self.entrada is not None
        self.visitadas.add(self.posicion)
        self.fronteras.discard(self.posicion)
        self.mapa.setdefault(self.posicion, set())

        salida = None
        for direccion, tipo, destino in self.entorno.percibir(self.posicion):
            if tipo == "borde":
                if not (self.posicion == self.entrada and direccion == SUPERIOR):
                    salida = direccion
                continue
            assert destino is not None
            self.mapa[self.posicion].add(destino)
            self.mapa.setdefault(destino, set()).add(self.posicion)
            if destino not in self.visitadas:
                self.fronteras.add(destino)
        self._emitir("percibir", None, "Mapa local actualizado")
        return salida

    def _seleccionar_frontera(self) -> Posicion:
        assert self.posicion is not None
        distancias = {frontera: self._h(self.posicion, frontera) for frontera in self.fronteras}
        minima = min(distancias.values())
        candidatas = sorted(f for f, distancia in distancias.items() if distancia == minima)
        return self.rng.choice(candidatas)

    @staticmethod
    def _h(origen: Posicion, meta: Posicion) -> int:
        return abs(origen[0] - meta[0]) + abs(origen[1] - meta[1])

    def _ruta_conocida(self, origen: Posicion, meta: Posicion) -> list[Posicion] | None:
        """A* hacia una meta conocida usando únicamente el mapa descubierto."""
        costos = {origen: 0}
        padres: dict[Posicion, Posicion | None] = {origen: None}
        abiertos = [(self._h(origen, meta), self.rng.random(), 0, origen)]

        while abiertos:
            _, _, costo, posicion = heapq.heappop(abiertos)
            if costo != costos.get(posicion):
                continue
            if posicion == meta:
                ruta: list[Posicion] = []
                while posicion is not None:
                    ruta.append(posicion)
                    posicion = padres[posicion]
                return ruta[::-1]

            self.expandidas += 1
            for vecina in self.mapa.get(posicion, ()):
                nuevo = costo + 1
                if nuevo < costos.get(vecina, float("inf")):
                    costos[vecina] = nuevo
                    padres[vecina] = posicion
                    prioridad = nuevo + self._h(vecina, meta)
                    heapq.heappush(abiertos, (prioridad, self.rng.random(), nuevo, vecina))
        return None

    def _seguir(self, ruta: list[Posicion]) -> bool:
        for destino in ruta[1:]:
            if self.movimientos >= self.max_movimientos:
                self.truncado = True
                self.motivo_truncado = "límite de movimientos alcanzado"
                self._emitir("truncado", ruta, self.motivo_truncado)
                return False
            self.posicion = destino
            self.trayectoria.append(destino)
            self.movimientos += 1
            self._emitir("mover", ruta, "Movimiento por el mapa conocido")
            if destino not in self.visitadas:
                break
        return True

    def _informe(self, camino: list[Posicion] | None) -> Informe:
        return {
            "algoritmo": "Exploración por fronteras",
            "entrada": self.entrada,
            "salida": self.salida,
            "camino": camino,
            "trayectoria": list(self.trayectoria),
            "tiene_solucion": self.salida is not None,
            "celdas_visitadas": len(self.visitadas),
            "movimientos": self.movimientos,
            "replanificaciones": self.replanificaciones,
            "expandidas": self.expandidas,
            "fronteras_pendientes": len(self.fronteras),
            "truncado": self.truncado,
            "motivo_truncado": self.motivo_truncado,
        }
