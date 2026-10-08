"""Búsqueda DFS determinista y exploración estocástica por fronteras."""

from __future__ import annotations

import heapq
import random
from typing import Any

from .entorno import Entorno
from .eventos import Evento
from .modelo import Posicion, SUPERIOR

Informe = dict[str, Any]


class AgenteDFS:
    """Busca la ruta más corta mediante DFS con poda de ramas redundantes."""

    def __init__(self, entorno: Entorno, max_pasos: int = 5_000_000) -> None:
        if type(max_pasos) is not int or max_pasos <= 0:
            raise ValueError("max_pasos debe ser un entero positivo.")
        self.entorno = entorno
        self.max_pasos = max_pasos
        self._reiniciar(False)

    def _reiniciar(self, registrar_eventos: bool) -> None:
        self.entrada: Posicion | None = None
        self.salidas: dict[tuple[Posicion, int], list[list[Posicion]]] = {}
        self.exploradas: set[Posicion] = set()
        self.pasos = self.expandidas = self.retrocesos = self.podas = 0
        self.soluciones_evaluadas = 0
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
        mensaje: str,
    ) -> None:
        if self._registrar_eventos:
            self.eventos.append(
                Evento(
                    tipo=tipo,
                    posicion=posicion,
                    visitadas=frozenset(self.exploradas),
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
        ruta = [self.entrada]
        en_ruta = {self.entrada}
        pila = [iter(self.entorno.percibir(self.entrada))]
        self.exploradas.add(self.entrada)
        self.expandidas = 1
        self._emitir(
            "inicio", self.entrada, ruta, "Inicio de la búsqueda DFS exhaustiva"
        )

        while pila:
            if self.pasos >= self.max_pasos:
                self.truncado = True
                self.motivo_truncado = "límite de pasos alcanzado"
                self._emitir("truncado", ruta[-1], ruta, self.motivo_truncado)
                break

            try:
                direccion, tipo, destino = next(pila[-1])
                self.pasos += 1
            except StopIteration:
                pila.pop()
                anterior = ruta.pop()
                en_ruta.remove(anterior)
                self.retrocesos += 1
                posicion = ruta[-1] if ruta else None
                self._emitir("retroceder", posicion, ruta, "Retroceso por backtracking")
                continue

            if tipo == "borde":
                if ruta[-1] == self.entrada and direccion == SUPERIOR:
                    continue
                self.soluciones_evaluadas += 1
                
                clave = (ruta[-1], direccion)
                self.salidas.setdefault(clave, []).append(list(ruta))
                
                self._emitir(
                    "salida",
                    ruta[-1],
                    ruta,
                    f"Ruta encontrada (Total de rutas: {sum(len(v) for v in self.salidas.values())})",
                )
                continue

            assert destino is not None
            redundante = destino in en_ruta
            if redundante:
                self.podas += 1
                continue

            ruta.append(destino)
            en_ruta.add(destino)
            self.exploradas.add(destino)
            pila.append(iter(self.entorno.percibir(destino)))
            self.expandidas += 1
            self._emitir(
                "avanzar", destino, ruta, "Avance a una celda no visitada en esta ruta"
            )

        if not self.truncado:
            posicion = self.entrada
            mensaje = "Búsqueda completa, se encontraron todas las rutas" if self.salidas else "No se encontró salida"
            mejor = min((camino for caminos in self.salidas.values() for camino in caminos), key=len, default=[])
            self._emitir(
                "final", posicion, mejor, mensaje
            )
        return self._informe()

    def _informe(self) -> Informe:
        todos_caminos = [camino for caminos in self.salidas.values() for camino in caminos]
        mas_corto = min(todos_caminos, key=len) if todos_caminos else None
        
        salida_optima = None
        if mas_corto:
            for (pos, d), caminos in self.salidas.items():
                if mas_corto in caminos:
                    salida_optima = (pos, d)
                    break

        return {
            "algoritmo": "DFS determinista",
            "entrada": self.entrada,
            "salida": salida_optima,
            "camino": mas_corto,
            "salidas_encontradas": self.salidas,
            "total_caminos": len(todos_caminos),
            "tiene_solucion": len(todos_caminos) > 0,
            "pasos": self.pasos,
            "expandidas": self.expandidas,
            "celdas_visitadas": len(self.exploradas),
            "soluciones_evaluadas": self.soluciones_evaluadas,
            "retrocesos": self.retrocesos,
            "podas": self.podas,
            "truncado": self.truncado,
            "motivo_truncado": self.motivo_truncado,
        }

class AgenteAStar:
    """Busca la salida utilizando el algoritmo A* de manera lógica."""

    def __init__(
        self,
        entorno: Entorno,
        salida: Posicion,
        max_pasos: int = 5_000_000,
        semilla: int | None = None,
    ) -> None:
        if type(max_pasos) is not int or max_pasos <= 0:
            raise ValueError("max_pasos debe ser un entero positivo.")
        self.entorno = entorno
        self.salida_meta = salida
        self.max_pasos = max_pasos
        self.semilla = semilla
        self._reiniciar(False)

    def _reiniciar(self, registrar_eventos: bool) -> None:
        self.rng = random.Random(self.semilla)
        self.entrada: Posicion | None = None
        self.salida: tuple[Posicion, int] | None = None
        self.mejor_camino: list[Posicion] | None = None
        self.exploradas: set[Posicion] = set()
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
        mensaje: str,
    ) -> None:
        if self._registrar_eventos:
            self.eventos.append(
                Evento(
                    tipo=tipo,
                    posicion=posicion,
                    visitadas=frozenset(self.exploradas),
                    ruta=tuple(ruta),
                    mensaje=mensaje,
                )
            )

    @staticmethod
    def _h(origen: Posicion, meta: Posicion) -> int:
        return abs(origen[0] - meta[0]) + abs(origen[1] - meta[1])

    def _resolver(self, registrar_eventos: bool) -> Informe:
        self._reiniciar(registrar_eventos)
        entradas = self.entorno.entradas()
        if not entradas:
            return self._informe()

        self.entrada = self.rng.choice(entradas)
        
        abiertos = [(self._h(self.entrada, self.salida_meta), self.rng.random(), 0, self.entrada, [self.entrada])]
        costos = {self.entrada: 0}
        
        self.exploradas.add(self.entrada)
        self.expandidas = 1
        self._emitir("inicio", self.entrada, [self.entrada], "Inicio de la búsqueda A*")

        while abiertos:
            if self.pasos >= self.max_pasos:
                self.truncado = True
                self.motivo_truncado = "límite de pasos alcanzado"
                _, _, _, pos, ruta = abiertos[0]
                self._emitir("truncado", pos, ruta, self.motivo_truncado)
                break

            f, _, g, pos, ruta = heapq.heappop(abiertos)
            self.pasos += 1

            if pos == self.salida_meta:
                for direccion, tipo, destino in self.entorno.percibir(pos):
                    if tipo == "borde" and not (pos == self.entrada and direccion == SUPERIOR):
                        self.salida = (pos, direccion)
                        self.mejor_camino = list(ruta)
                        self._emitir("salida", pos, ruta, "Meta alcanzada por A*")
                        return self._informe()

            self._emitir("avanzar", pos, ruta, "Expandiendo nodo con menor f(n)")

            for direccion, tipo, destino in self.entorno.percibir(pos):
                if tipo == "borde":
                    continue
                assert destino is not None
                
                nuevo_costo = g + 1
                if nuevo_costo < costos.get(destino, float("inf")):
                    costos[destino] = nuevo_costo
                    prioridad = nuevo_costo + self._h(destino, self.salida_meta)
                    nueva_ruta = list(ruta)
                    nueva_ruta.append(destino)
                    heapq.heappush(abiertos, (prioridad, self.rng.random(), nuevo_costo, destino, nueva_ruta))
                    self.exploradas.add(destino)
            self.expandidas += 1

        if not self.truncado:
            posicion = self.mejor_camino[-1] if self.mejor_camino else None
            mensaje = "Ruta óptima encontrada" if self.mejor_camino else "No se encontró ruta a la meta"
            self._emitir("final", posicion, self.mejor_camino or [], mensaje)
        
        return self._informe()

    def _informe(self) -> Informe:
        return {
            "algoritmo": "A* no determinista",
            "entrada": self.entrada,
            "salida": self.salida,
            "camino": self.mejor_camino,
            "tiene_solucion": self.mejor_camino is not None,
            "pasos": self.pasos,
            "expandidas": self.expandidas,
            "celdas_visitadas": len(self.exploradas),
            "truncado": self.truncado,
            "motivo_truncado": self.motivo_truncado,
        }
