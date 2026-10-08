from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_aplicacion_carga_y_ejecuta_explorador():
    ruta_app = Path(__file__).parents[1] / "app.py"
    app = AppTest.from_file(ruta_app, default_timeout=30).run()
    assert not app.exception
    assert not app.button[1].disabled

    app.selectbox[0].select("Exploración por fronteras")
    app.button[1].click().run()

    assert not app.exception
    assert any(control.label == "Paso de la ejecución" for control in app.slider)
    assert len(app.metric) >= 5
