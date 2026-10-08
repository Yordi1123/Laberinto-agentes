from pathlib import Path

from laberinto import crear_laberinto
from laberinto.visualizacion import dibujar_laberinto
import matplotlib.pyplot as plt
from streamlit.testing.v1 import AppTest


def _boton(app: AppTest, etiqueta: str):
    return next(boton for boton in app.button if boton.label == etiqueta)


def test_aplicacion_carga_laberinto_y_controles():
    ruta_app = Path(__file__).parents[1] / "app.py"
    app = AppTest.from_file(ruta_app, default_timeout=30).run()
    assert not app.exception
    assert app.radio[0].value == "Vista del espectador"
    assert not _boton(app, "Ejecutar algoritmo").disabled
    assert any(control.label == "Velocidad de animación" for control in app.slider)
    assert any("Laberinto listo" in mensaje.value for mensaje in app.info)


def test_figura_limita_su_tamano_y_muestra_entrada_y_salida():
    laberinto, entrada, salida = crear_laberinto(30, 30, semilla=26)
    figura = dibujar_laberinto(laberinto, entrada, salida)

    ancho, alto = figura.get_size_inches()
    etiquetas = {texto.get_text() for texto in figura.axes[0].texts}
    assert ancho <= 9
    assert alto <= 6.8
    assert {"S", "E"} <= etiquetas
    plt.close(figura)
