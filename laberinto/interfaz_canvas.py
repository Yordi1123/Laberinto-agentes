"""Componente Canvas para reproducir búsquedas sin redibujar desde Python."""

from __future__ import annotations

import json
from typing import Any, Sequence

import streamlit as st

from .eventos import Evento
from .modelo import Celda, Laberinto, Posicion

MAX_FOTOGRAMAS = 3_000


def preparar_animacion(
    laberinto: Laberinto,
    entrada: Posicion,
    salida: Posicion,
    eventos: Sequence[Evento],
    informe: dict[str, Any] | None,
    algoritmo: str | None,
    vista_agente: bool,
) -> dict[str, Any]:
    """Convierte objetos Python a una carga compacta para el navegador."""
    indices = _seleccionar_indices(eventos)
    visitadas_anteriores: set[Posicion] = set()
    fotogramas = []

    for indice in indices:
        evento = eventos[indice]
        visitadas = set(evento.visitadas)
        nuevas = sorted(visitadas - visitadas_anteriores)
        visitadas_anteriores.update(visitadas)
        fotogramas.append(
            {
                "t": evento.tipo,
                "p": evento.posicion,
                "v": nuevas,
                "f": sorted(evento.fronteras),
                "r": evento.ruta,
                "m": evento.mensaje,
                "mv": max(0, len(evento.trayectoria) - 1),
                "o": indice,
            }
        )

    return {
        "filas": len(laberinto),
        "columnas": len(laberinto[0]),
        "paredes": [[_mascara(celda) for celda in fila] for fila in laberinto],
        "entrada": entrada,
        "salida": salida,
        "eventos": fotogramas,
        "totalEventos": len(eventos),
        "algoritmo": algoritmo,
        "vistaAgente": vista_agente,
        "resultado": _resumir_informe(informe),
    }


def mostrar_animacion(datos: dict[str, Any]) -> None:
    """Inserta el reproductor autónomo dentro de la aplicación Streamlit."""
    st.iframe(
        crear_html_animacion(datos),
        width="stretch",
        height="content",
        alt="Reproductor animado del agente dentro del laberinto",
    )


def crear_html_animacion(datos: dict[str, Any]) -> str:
    """Genera el documento autocontenido utilizado por el iframe."""
    carga = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    carga = (
        carga.replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    return _PLANTILLA.replace("__DATOS_ANIMACION__", carga)


def _seleccionar_indices(eventos: Sequence[Evento]) -> list[int]:
    """Limita ejecuciones extremas sin perder inicio, desenlace ni salidas."""
    total = len(eventos)
    if total <= MAX_FOTOGRAMAS:
        return list(range(total))

    paso = (total - 1) / (MAX_FOTOGRAMAS - 1)
    indices = {round(numero * paso) for numero in range(MAX_FOTOGRAMAS)}
    importantes = {"inicio", "salida", "sin_solucion", "truncado", "final"}
    indices.update(i for i, evento in enumerate(eventos) if evento.tipo in importantes)
    return sorted(indices)


def _mascara(celda: Celda) -> int:
    return (
        int(celda.pared_superior)
        | (int(celda.pared_inferior) << 1)
        | (int(celda.pared_izquierda) << 2)
        | (int(celda.pared_derecha) << 3)
    )


def _resumir_informe(informe: dict[str, Any] | None) -> dict[str, Any] | None:
    if informe is None:
        return None
    camino = informe.get("camino")
    claves = (
        "truncado",
        "motivo_truncado",
        "tiene_solucion",
        "expandidas",
        "total_caminos",
        "retrocesos",
        "pasos",
        "celdas_visitadas",
        "movimientos",
        "replanificaciones",
    )
    resumen = {clave: informe.get(clave) for clave in claves if clave in informe}
    resumen["longitud_ruta"] = len(camino) if camino else 0
    return resumen


_PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {
    color-scheme: light;
    --ink: #172033; --muted: #64748b; --line: #dbe3ef;
    --panel: #ffffff; --soft: #f4f7fb; --accent: #e83e5b;
    --blue: #b9e5f7; --yellow: #ffd166; --purple: #c9b8ff;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: transparent; color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
  button, input { font: inherit; }
  .player { border: 1px solid var(--line); border-radius: 16px; overflow: hidden; background: var(--panel); box-shadow: 0 10px 30px rgba(30, 41, 59, .07); }
  .toolbar { display: grid; grid-template-columns: auto minmax(180px, 1fr) auto; gap: 14px; align-items: center; padding: 12px 14px; background: #172033; color: white; }
  .buttons { display: flex; gap: 7px; }
  .icon { width: 36px; height: 34px; border: 1px solid #475569; border-radius: 9px; color: white; background: #263247; cursor: pointer; transition: .16s ease; }
  .icon:hover:not(:disabled) { background: #35445e; transform: translateY(-1px); }
  .icon.primary { background: var(--accent); border-color: var(--accent); }
  .icon:disabled { opacity: .38; cursor: default; }
  .timeline { min-width: 0; }
  .timeline input, .speed input { width: 100%; accent-color: var(--accent); cursor: pointer; }
  .timeline-row { display: flex; justify-content: space-between; gap: 12px; font-size: 12px; color: #cbd5e1; margin-top: 2px; }
  .speed { width: 130px; }
  .speed label { display: flex; justify-content: space-between; font-size: 12px; color: #cbd5e1; }
  .content { display: grid; grid-template-columns: minmax(0, 1fr) minmax(215px, 280px); min-height: 500px; }
  .maze-panel { min-width: 0; padding: 14px; background: var(--soft); }
  .canvas-wrap { position: relative; height: 470px; border-radius: 12px; overflow: hidden; background: white; border: 1px solid #e5eaf2; }
  canvas { width: 100%; height: 100%; display: block; }
  .progress { height: 4px; background: #e2e8f0; }
  .progress > div { height: 100%; width: 0; background: linear-gradient(90deg, #ef476f, #ff8b6a); transition: width .12s linear; }
  .legend { display: flex; flex-wrap: wrap; gap: 7px 14px; padding-top: 10px; color: var(--muted); font-size: 12px; }
  .legend span { display: inline-flex; align-items: center; gap: 5px; }
  .dot { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
  .side { padding: 18px; border-left: 1px solid var(--line); background: white; }
  .eyebrow { margin: 0 0 5px; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; font-size: 11px; font-weight: 700; }
  h3 { margin: 0; font-size: 19px; line-height: 1.2; }
  .message { min-height: 44px; margin: 10px 0 15px; color: var(--muted); font-size: 13px; line-height: 1.45; }
  .badge { display: none; width: fit-content; margin: 0 0 13px; padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 700; }
  .badge.ok { display: block; color: #166534; background: #dcfce7; }
  .badge.bad { display: block; color: #991b1b; background: #fee2e2; }
  .badge.warn { display: block; color: #92400e; background: #fef3c7; }
  .metrics { display: grid; gap: 8px; }
  .metric { padding: 10px 11px; border: 1px solid var(--line); border-radius: 10px; background: #fafcff; }
  .metric span { display: block; color: var(--muted); font-size: 11px; }
  .metric strong { display: block; margin-top: 2px; font-size: 18px; }
  .sampling { margin-top: 12px; color: var(--muted); font-size: 11px; line-height: 1.35; }
  @media (max-width: 760px) {
    .toolbar { grid-template-columns: auto 1fr; }
    .speed { grid-column: 1 / -1; width: 100%; display: grid; grid-template-columns: 95px 1fr; gap: 10px; align-items: center; }
    .content { grid-template-columns: 1fr; }
    .side { border-left: 0; border-top: 1px solid var(--line); }
    .canvas-wrap { height: 420px; }
  }
</style>
</head>
<body>
<main class="player">
  <section class="toolbar" aria-label="Controles de animación">
    <div class="buttons">
      <button class="icon primary" id="play" aria-label="Reproducir o pausar">▶</button>
      <button class="icon" id="restart" aria-label="Reiniciar">↺</button>
      <button class="icon" id="prev" aria-label="Paso anterior">←</button>
      <button class="icon" id="next" aria-label="Paso siguiente">→</button>
    </div>
    <div class="timeline">
      <input id="seek" type="range" min="0" value="0" step="1" aria-label="Línea de tiempo">
      <div class="timeline-row"><span id="counter">Laberinto listo</span><span id="eventType">Sin ejecutar</span></div>
    </div>
    <div class="speed">
      <label for="speed"><span>Velocidad</span><strong id="speedValue">8×</strong></label>
      <input id="speed" type="range" min="1" max="30" value="8" step="1">
    </div>
  </section>
  <div class="progress"><div id="progressBar"></div></div>
  <section class="content">
    <div class="maze-panel">
      <div class="canvas-wrap" id="canvasWrap"><canvas id="maze" aria-label="Animación del laberinto"></canvas></div>
      <div class="legend">
        <span><i class="dot" style="background:#ef476f"></i>Agente</span>
        <span><i class="dot" style="background:#b9e5f7"></i>Visitadas</span>
        <span><i class="dot" style="background:#ffd166"></i>Fronteras</span>
        <span><i class="dot" style="background:#c9b8ff"></i>Ruta planificada</span>
        <span><i class="dot" style="background:#263238"></i>Desconocido</span>
      </div>
    </div>
    <aside class="side">
      <p class="eyebrow">Estado del agente</p>
      <h3 id="statusTitle">Laberinto generado</h3>
      <p class="message" id="message">Ejecuta un algoritmo para comenzar la animación.</p>
      <div class="badge" id="badge"></div>
      <div class="metrics" id="metrics"></div>
      <p class="sampling" id="sampling"></p>
    </aside>
  </section>
</main>

<script>
const DATA = __DATOS_ANIMACION__;
const COLORS = {free:'#ffffff', unknown:'#263238', visited:'#b9e5f7', frontier:'#ffd166', route:'#c9b8ff', wall:'#172033', agent:'#ef476f'};
const events = DATA.eventos;
const canvas = document.getElementById('maze');
const wrap = document.getElementById('canvasWrap');
const ctx = canvas.getContext('2d');
const ui = Object.fromEntries(['play','restart','prev','next','seek','counter','eventType','speed','speedValue','progressBar','statusTitle','message','badge','metrics','sampling'].map(id => [id, document.getElementById(id)]));
let width = 0, height = 0, cell = 1, offsetX = 0, offsetY = 0;
let index = 0, playing = events.length > 1, speed = 8, transitionStart = null, frameRequest = null;
let visited = new Set(), exitFound = false;

const key = p => `${p[0]},${p[1]}`;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const ease = value => value * value * (3 - 2 * value);
const position = p => ({x: offsetX + (p[1] + .5) * cell, y: offsetY + (p[0] + .5) * cell});

function rebuildState(target) {
  visited = new Set(); exitFound = false;
  for (let i = 0; i <= target && i < events.length; i++) {
    events[i].v.forEach(p => visited.add(key(p)));
    if (events[i].t === 'salida') exitFound = true;
  }
}

function applyEvent(event) {
  event.v.forEach(p => visited.add(key(p)));
  if (event.t === 'salida') exitFound = true;
}

function resizeCanvas() {
  const box = wrap.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  width = box.width; height = box.height;
  canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  cell = Math.min((width - 28) / DATA.columnas, (height - 28) / DATA.filas);
  offsetX = (width - cell * DATA.columnas) / 2;
  offsetY = (height - cell * DATA.filas) / 2;
  draw(currentPosition());
}

function currentPosition() {
  return events.length && events[index].p ? position(events[index].p) : null;
}

function draw(agentPoint) {
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, width, height);
  const event = events[index] || {f:[], r:[]};
  const frontiers = new Set(event.f.map(key));
  const route = new Set(event.r.map(key));

  for (let row = 0; row < DATA.filas; row++) {
    for (let col = 0; col < DATA.columnas; col++) {
      const id = `${row},${col}`;
      const known = visited.has(id) || frontiers.has(id) || id === key(DATA.entrada);
      let fill = DATA.vistaAgente && !known ? COLORS.unknown : COLORS.free;
      if (known && visited.has(id)) fill = COLORS.visited;
      if (frontiers.has(id)) fill = COLORS.frontier;
      if (route.has(id)) fill = COLORS.route;
      ctx.fillStyle = fill;
      ctx.fillRect(offsetX + col * cell, offsetY + row * cell, cell + .35, cell + .35);
    }
  }

  ctx.beginPath();
  ctx.strokeStyle = COLORS.wall;
  ctx.lineWidth = clamp(cell * .085, 1.15, 3);
  ctx.lineCap = 'round';
  for (let row = 0; row < DATA.filas; row++) {
    for (let col = 0; col < DATA.columnas; col++) {
      const id = `${row},${col}`;
      if (DATA.vistaAgente && !(visited.has(id) || frontiers.has(id) || id === key(DATA.entrada))) continue;
      const mask = DATA.paredes[row][col];
      const x = offsetX + col * cell, y = offsetY + row * cell;
      if (mask & 1) { ctx.moveTo(x, y); ctx.lineTo(x + cell, y); }
      if (mask & 2) { ctx.moveTo(x, y + cell); ctx.lineTo(x + cell, y + cell); }
      if (mask & 4) { ctx.moveTo(x, y); ctx.lineTo(x, y + cell); }
      if (mask & 8) { ctx.moveTo(x + cell, y); ctx.lineTo(x + cell, y + cell); }
    }
  }
  ctx.stroke();
  drawLabel(DATA.entrada, 'S', '#0f766e');
  if (!DATA.vistaAgente || exitFound) drawLabel(DATA.salida, 'E', '#15803d');
  if (agentPoint) drawAgent(agentPoint);
}

function drawLabel(p, label, color) {
  const x = offsetX + (p[1] + .18) * cell, y = offsetY + (p[0] + .2) * cell;
  ctx.fillStyle = color; ctx.font = `700 ${clamp(cell * .27, 8, 12)}px system-ui`;
  ctx.textAlign = 'left'; ctx.textBaseline = 'top'; ctx.fillText(label, x, y);
}

function drawAgent(p) {
  const radius = clamp(cell * .29, 4.5, 13);
  ctx.save();
  ctx.shadowColor = 'rgba(239,71,111,.38)'; ctx.shadowBlur = radius * .9;
  ctx.fillStyle = COLORS.agent; ctx.beginPath(); ctx.arc(p.x, p.y, radius, 0, Math.PI * 2); ctx.fill();
  ctx.shadowBlur = 0; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(1.8, radius * .25), 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

function metric(label, value) {
  return `<div class="metric"><span>${label}</span><strong>${value ?? 0}</strong></div>`;
}

function updateUI() {
  const hasEvents = events.length > 0;
  const event = hasEvents ? events[index] : null;
  const originalStep = event ? event.o + 1 : 0;
  ui.seek.max = Math.max(0, events.length - 1); ui.seek.value = index; ui.seek.disabled = !hasEvents;
  ui.play.disabled = events.length < 2; ui.prev.disabled = !hasEvents || index === 0; ui.next.disabled = !hasEvents || index === events.length - 1;
  ui.play.textContent = playing ? '❚❚' : '▶';
  ui.counter.textContent = hasEvents ? `Evento ${originalStep} de ${DATA.totalEventos}` : 'Laberinto listo';
  ui.eventType.textContent = event ? event.t.replaceAll('_', ' ') : 'Sin ejecutar';
  ui.progressBar.style.width = hasEvents ? `${100 * originalStep / DATA.totalEventos}%` : '0%';
  ui.badge.className = 'badge'; ui.badge.textContent = '';

  if (!hasEvents) {
    ui.statusTitle.textContent = 'Laberinto generado';
    ui.message.textContent = 'Ejecuta un algoritmo para comenzar la animación.';
    ui.metrics.innerHTML = metric('Dimensiones', `${DATA.filas} × ${DATA.columnas}`);
  } else if (index < events.length - 1) {
    ui.statusTitle.textContent = event.t === 'salida' ? 'Salida detectada' : 'Exploración en curso';
    ui.message.textContent = event.m;
    ui.metrics.innerHTML = DATA.algoritmo === 'DFS determinista'
      ? metric('Celdas observadas', visited.size) + metric('Longitud de la ruta actual', event.r.length)
      : metric('Celdas observadas', visited.size) + metric('Fronteras activas', event.f.length) + metric('Movimientos', event.mv);
  } else {
    showResult(event);
  }
  ui.sampling.textContent = DATA.totalEventos > events.length
    ? `${DATA.totalEventos.toLocaleString('es')} eventos condensados en ${events.length.toLocaleString('es')} fotogramas para conservar la fluidez.` : '';
}

function showResult(event) {
  const result = DATA.resultado || {};
  ui.message.textContent = event.m;
  if (result.truncado) {
    ui.statusTitle.textContent = 'Ejecución inconclusa'; ui.badge.className = 'badge warn';
    ui.badge.textContent = result.motivo_truncado || 'Límite alcanzado';
  } else if (result.tiene_solucion) {
    ui.statusTitle.textContent = 'Salida encontrada'; ui.badge.className = 'badge ok'; ui.badge.textContent = 'Con solución';
  } else {
    ui.statusTitle.textContent = 'Exploración terminada'; ui.badge.className = 'badge bad'; ui.badge.textContent = 'Sin solución';
  }
  let html = metric('Celdas expandidas', result.expandidas);
  if (DATA.algoritmo === 'DFS determinista') {
    html += metric('Caminos encontrados', result.total_caminos) + metric('Retrocesos', result.retrocesos);
  } else {
    html += metric('Celdas visitadas', result.celdas_visitadas) + metric('Movimientos', result.movimientos) + metric('Replanificaciones', result.replanificaciones);
  }
  if (result.longitud_ruta) html += metric('Longitud de la ruta', result.longitud_ruta);
  ui.metrics.innerHTML = html;
}

function pause() {
  playing = false; transitionStart = null;
  if (frameRequest) cancelAnimationFrame(frameRequest);
  frameRequest = null; updateUI(); draw(currentPosition());
}

function play() {
  if (events.length < 2) return;
  if (index >= events.length - 1) { index = 0; rebuildState(0); }
  playing = true; transitionStart = null; updateUI();
  frameRequest = requestAnimationFrame(animate);
}

function seek(target) {
  pause(); index = clamp(Number(target), 0, Math.max(0, events.length - 1));
  rebuildState(index); updateUI(); draw(currentPosition());
}

function animate(timestamp) {
  if (!playing) return;
  if (index >= events.length - 1) { pause(); return; }
  if (transitionStart === null) transitionStart = timestamp;
  const duration = 1000 / speed;
  const progress = clamp((timestamp - transitionStart) / duration, 0, 1);
  const fromEvent = events[index], toEvent = events[index + 1];
  let agentPoint = fromEvent.p ? position(fromEvent.p) : null;
  if (fromEvent.p && toEvent.p) {
    const from = position(fromEvent.p), to = position(toEvent.p), amount = ease(progress);
    agentPoint = {x: from.x + (to.x - from.x) * amount, y: from.y + (to.y - from.y) * amount};
  }
  draw(agentPoint);
  if (progress >= 1) {
    index += 1; applyEvent(events[index]); transitionStart = null; updateUI();
    if (index >= events.length - 1) { pause(); return; }
  }
  frameRequest = requestAnimationFrame(animate);
}

ui.play.addEventListener('click', () => playing ? pause() : play());
ui.restart.addEventListener('click', () => seek(0));
ui.prev.addEventListener('click', () => seek(index - 1));
ui.next.addEventListener('click', () => seek(index + 1));
ui.seek.addEventListener('input', event => seek(event.target.value));
ui.speed.addEventListener('input', event => { speed = Number(event.target.value); ui.speedValue.textContent = `${speed}×`; });
new ResizeObserver(resizeCanvas).observe(wrap);
if (events.length) rebuildState(0);
updateUI(); resizeCanvas();
if (playing) frameRequest = requestAnimationFrame(animate);
</script>
</body>
</html>"""
