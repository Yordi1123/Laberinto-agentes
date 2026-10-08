from laberinto import (
    AgenteDFS,
    AgenteAStar,
    Entorno,
    crear_laberinto,
)
from laberinto.interfaz_canvas import crear_html_animacion, preparar_animacion


def test_prepara_eventos_compactos_para_canvas():
    laberinto, entrada, salida = crear_laberinto(8, 9, semilla=26)
    informe, eventos = AgenteAStar(
        Entorno(laberinto), salida=salida, semilla=26
    ).ejecutar()

    datos = preparar_animacion(
        laberinto,
        entrada,
        salida,
        eventos,
        informe,
        "A* no determinista",
        vista_agente=False,
    )

    visitadas = set()
    for evento in datos["eventos"]:
        visitadas.update(map(tuple, evento["v"]))

    assert len(datos["paredes"]) == 8
    assert len(datos["paredes"][0]) == 9
    assert visitadas == set(eventos[-1].visitadas)
    assert datos["resultado"]["tiene_solucion"] == informe["tiene_solucion"]


def test_html_anima_en_el_navegador():
    laberinto, entrada, salida = crear_laberinto(3, 4, semilla=7)
    datos = preparar_animacion(
        laberinto, entrada, salida, (), None, None, vista_agente=False
    )
    html = crear_html_animacion(datos)

    assert '<canvas id="maze"' in html
    assert "requestAnimationFrame" in html
    assert "ResizeObserver" in html
    assert "__DATOS_ANIMACION__" not in html


def test_estado_final_contiene_unicamente_la_ruta_minima():
    laberinto, entrada, salida = crear_laberinto(10, 10, semilla=1)
    informe, eventos = AgenteDFS(Entorno(laberinto)).ejecutar()
    datos = preparar_animacion(
        laberinto,
        entrada,
        salida,
        eventos,
        informe,
        "DFS determinista",
        vista_agente=False,
    )

    if informe["tiene_solucion"]:
        assert datos["eventos"][-1]["r"] == tuple(informe["camino"])
    assert "bestPathOnly" in crear_html_animacion(datos)
