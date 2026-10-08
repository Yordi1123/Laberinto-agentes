from laberinto import AgenteExploradorFronteras, Entorno, crear_laberinto
from laberinto.interfaz_canvas import crear_html_animacion, preparar_animacion


def test_prepara_eventos_compactos_para_canvas():
    laberinto, entrada, salida = crear_laberinto(8, 9, semilla=26)
    informe, eventos = AgenteExploradorFronteras(
        Entorno(laberinto), semilla=26
    ).ejecutar()

    datos = preparar_animacion(
        laberinto,
        entrada,
        salida,
        eventos,
        informe,
        "Exploración por fronteras",
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
