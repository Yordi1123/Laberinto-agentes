# Agentes inteligentes en un laberinto

Proyecto académico para comparar dos estrategias de búsqueda sobre laberintos aleatorios:

- **Búsqueda determinista (BFS):** encuentra un camino mínimo sin expandir una celda más de una vez.
- **Exploración por fronteras:** construye un mapa con percepción local y usa A* únicamente para desplazarse hacia una frontera conocida.

El generador utiliza **Kruskal aleatorio** y Union-Find para construir entre uno y tres componentes. La entrada y la salida se agregan después, por lo que el generador no determina si existe solución.

## Demostración interactiva

La aplicación permite:

- Configurar las dimensiones y la semilla.
- Generar laberintos reproducibles.
- Elegir el algoritmo.
- Observar el laberinto completo desde la vista del espectador.
- Reproducir, pausar, reiniciar o recorrer paso a paso la búsqueda animada.
- Regular la velocidad de reproducción entre 1 y 30 eventos por segundo.
- Alternar con la vista parcial que representa el conocimiento real del agente.
- Comparar longitud de ruta, celdas expandidas, movimientos y replanificaciones.
- Mostrar únicamente el camino mínimo cuando termina la búsqueda determinista.

La animación utiliza **Canvas y JavaScript** dentro del navegador. Python envía el
laberinto y una secuencia compacta de eventos una sola vez; después el agente se
mueve con interpolación mediante `requestAnimationFrame`, sin generar una imagen
Matplotlib nueva en cada fotograma.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

En Linux o macOS, la activación del entorno es:

```bash
source .venv/bin/activate
```

## Estructura

```text
.
├── app.py                         # Interfaz Streamlit
├── laberinto/
│   ├── modelo.py                  # Celdas, paredes y direcciones
│   ├── generador.py               # Kruskal y Union-Find
│   ├── entorno.py                 # Percepción local
│   ├── agentes.py                 # BFS determinista y exploración por fronteras
│   ├── eventos.py                 # Instantáneas para la interfaz
│   ├── interfaz_canvas.py         # Reproductor animado en el navegador
│   └── visualizacion.py           # Renderizado con Matplotlib
├── notebooks/
│   ├── Reto_Laberinto.ipynb       # Presentación y experimentos
│   └── Reto_Laberinto_original.ipynb
└── tests/                          # Pruebas automatizadas
```

El notebook original se conserva únicamente como historial. La implementación vigente está en el paquete `laberinto`.

## Ejecución del notebook

Desde la raíz del repositorio:

```bash
jupyter lab notebooks/Reto_Laberinto.ipynb
```

El notebook importa los módulos del proyecto para evitar mantener copias diferentes de los algoritmos.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

Las pruebas verifican:

- Simetría de paredes.
- Entre uno y tres componentes.
- Un máximo de cuatro ciclos independientes.
- Reproducibilidad mediante semillas.
- Coincidencia de los agentes sobre la existencia de solución.
- Validez de los caminos encontrados.
- Optimalidad del camino devuelto por BFS y ausencia de expansiones repetidas.
- Eventos reproducibles y truncamiento seguro.

## Modelo de información

El agente de fronteras no recibe las dimensiones ni la posición de la salida. Solo utiliza:

- Su posición actual.
- Pasillos visibles desde esa posición.
- El mapa que construye durante la exploración.

La distancia Manhattan se utiliza exclusivamente cuando A* navega hacia una frontera ya descubierta. No se emplea como estimación de la salida desconocida.

BFS se presenta como una búsqueda sobre el grafo: la marca roja indica la celda que
se está expandiendo y no un desplazamiento físico entre elementos de la cola. En
cambio, el explorador por fronteras sí registra todos sus movimientos reales.

## Publicación

El repositorio puede desplegarse en [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) seleccionando:

```text
Rama: main
Archivo principal: app.py
```

Una vez publicado, se recomienda agregar la URL de la aplicación al inicio de este README.
