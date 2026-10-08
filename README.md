# Agentes inteligentes en un laberinto

🚀 **Aplicación en vivo:** [Jugar con el simulador en Streamlit](https://laberinto-agentes-negkceajbljalgglgalgkg.streamlit.app/)

Este proyecto académico implementa y compara dos estrategias de búsqueda sobre laberintos aleatorios:

- **DFS determinista:** Algoritmo exhaustivo que explora sistemáticamente para encontrar todos los caminos posibles hasta la salida, implementando backtracking para contar las rutas totales y evitar ciclos infinitos.
- **A* heurístico (no determinista):** Algoritmo que utiliza la heurística de distancia Manhattan para acercarse a la salida, introduciendo desempate aleatorio para descubrir y evaluar múltiples rutas óptimas sin volverse predecible.

### 📓 Fuente del Proyecto
La fuente principal de conocimiento, análisis, estructura y lógica algorítmica de todo el proyecto se encuentra en el cuaderno de Jupyter: 
**`notebooks/Reto_Laberinto.ipynb`**.

El resto de archivos y carpetas del repositorio representan simplemente una **implementación gráfica interactiva** construida sobre la lógica de dicho cuaderno. Su propósito es proveer una plataforma visual (vía Streamlit y Canvas) para ver a los agentes en tiempo real, comparar animaciones y contrastar el rendimiento de ambas inteligencias en un mismo entorno.

---

## 🚀 Guía de Ejecución (Interfaz Gráfica)

Sigue estos sencillos pasos para levantar el simulador visual en tu computadora:

1. **Crear y activar un entorno virtual (Recomendado):**
   ```powershell
   # En Windows:
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   
   # En Linux / macOS:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lanzar la aplicación:**
   ```bash
   streamlit run app.py
   ```
   *(El navegador web se abrirá automáticamente con la interfaz del simulador).*

---

## 🔬 Exploración del Notebook (Código puro)

Si deseas explorar la matemática, la generación de matrices usando Kruskal o ejecutar el código base paso a paso sin la interfaz gráfica, puedes abrir directamente la fuente original:

```bash
pip install -r requirements-dev.txt
jupyter lab notebooks/Reto_Laberinto.ipynb
```

*(Opcional: puedes verificar la integridad de los algoritmos ejecutando los tests automatizados con el comando `pytest -q`)*.
