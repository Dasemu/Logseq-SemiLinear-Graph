#!/usr/bin/env python3
import json, sys, html

DATA_PATH = "graph_data.json"
D3_PATH = "vendor/d3.min.js"
OUT_PATH = "graph_view.html"

with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

with open(D3_PATH, encoding="utf-8") as f:
    d3_src = f.read()

data_json = json.dumps(data, ensure_ascii=False)

TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Linea temporal del grafo</title>
<style>
  :root {
    --bg: #0b0d12;
    --line: #3a4050;
    --journal: #6c7688;
    --journal-active: #ffd166;
    --page: #4fb0ff;
    --page-dim: #2a3a4a;
    --edge: rgba(120,140,170,0.18);
    --edge-active: rgba(255,209,102,0.85);
    --text: #e8ecf3;
    --text-dim: #8993a6;
    --panel-bg: rgba(15,18,26,0.92);
    --accent: #ff6b6b;
  }
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; width:100%; height:100%; background:var(--bg); color:var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; overflow:hidden; }
  svg { width:100%; height:100%; display:block; cursor:grab; }
  svg:active { cursor:grabbing; }

  .hud {
    position:fixed; top:12px; left:12px; z-index:10;
    background:var(--panel-bg); border:1px solid #262c3a; border-radius:10px;
    padding:12px 14px; max-width:340px; backdrop-filter: blur(6px);
  }
  .hud h1 { font-size:14px; margin:0 0 6px; font-weight:600; letter-spacing:.2px; }
  .hud .stats { font-size:11px; color:var(--text-dim); margin-bottom:10px; }
  .hud input[type=text] {
    width:100%; background:#141824; border:1px solid #2a3040; border-radius:6px;
    color:var(--text); padding:6px 8px; font-size:12px; outline:none;
  }
  .hud input[type=text]:focus { border-color:var(--page); }
  .hud .row { display:flex; gap:8px; align-items:center; margin-top:8px; font-size:11px; color:var(--text-dim); }
  .hud .row label { display:flex; gap:5px; align-items:center; cursor:pointer; }
  .hud button {
    background:#1a2030; border:1px solid #2a3040; color:var(--text-dim); font-size:11px;
    padding:4px 8px; border-radius:6px; cursor:pointer; margin-top:8px;
  }
  .hud button:hover { color:var(--text); border-color:var(--page); }

  .hud .controls { margin-top:10px; border-top:1px solid #232838; padding-top:8px; }
  .hud .ctrl { margin-top:8px; }
  .hud .ctrl-label { display:flex; justify-content:space-between; font-size:11px; color:var(--text-dim); margin-bottom:3px; }
  .hud .ctrl-label span.val { color:var(--text); font-variant-numeric:tabular-nums; }
  .hud input[type=range] {
    width:100%; -webkit-appearance:none; appearance:none; height:4px; border-radius:2px;
    background:#232838; outline:none;
  }
  .hud input[type=range]::-webkit-slider-thumb {
    -webkit-appearance:none; appearance:none; width:12px; height:12px; border-radius:50%;
    background:var(--page); cursor:pointer; border:2px solid #0b0d12;
  }
  .hud input[type=range]::-moz-range-thumb {
    width:12px; height:12px; border-radius:50%; background:var(--page); cursor:pointer; border:2px solid #0b0d12;
  }
  .hud .ctrl-buttons { display:flex; gap:8px; }
  .hud .ctrl-buttons button { flex:1; margin-top:8px; }
  .hud summary { cursor:pointer; font-size:12px; color:var(--text-dim); user-select:none; }
  .hud summary:hover { color:var(--text); }

  .tooltip {
    position:fixed; pointer-events:none; z-index:20;
    background:var(--panel-bg); border:1px solid #2a3040; border-radius:8px;
    padding:8px 10px; font-size:12px; max-width:280px; display:none;
    box-shadow:0 6px 24px rgba(0,0,0,0.5);
  }
  .tooltip .t-name { font-weight:600; margin-bottom:2px; }
  .tooltip .t-meta { color:var(--text-dim); font-size:11px; }

  .legend {
    position:fixed; bottom:12px; left:12px; z-index:10; font-size:11px; color:var(--text-dim);
    background:var(--panel-bg); border:1px solid #262c3a; border-radius:10px; padding:10px 12px;
    display:flex; gap:16px; align-items:center;
  }
  .legend .dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px; vertical-align:middle; }

  .node-label { fill: var(--text-dim); font-size:10px; pointer-events:none; user-select:none; }
  .journal-label { fill: var(--text-dim); font-size:9px; pointer-events:none; user-select:none; }
</style>
</head>
<body>

<div class="hud">
  <h1>Linea temporal del grafo &mdash; ~/Notas</h1>
  <div class="stats" id="stats"></div>
  <input type="text" id="search" placeholder="Buscar nota por nombre...">
  <div class="row">
    <label><input type="checkbox" id="toggle-labels" checked> Etiquetas de notas</label>
  </div>
  <div class="row">
    <label><input type="checkbox" id="toggle-jlabels"> Fechas de journals</label>
  </div>
  <button id="reset-view">Reset vista</button>

  <details class="controls" open>
    <summary>Fuerzas del layout</summary>

    <div class="ctrl">
      <div class="ctrl-label"><span>Separaci&oacute;n vertical</span><span class="val" id="val-spread"></span></div>
      <input type="range" id="ctl-spread" min="150" max="1600" step="10">
    </div>
    <div class="ctrl">
      <div class="ctrl-label"><span>Repulsi&oacute;n entre notas</span><span class="val" id="val-charge"></span></div>
      <input type="range" id="ctl-charge" min="0" max="500" step="5">
    </div>
    <div class="ctrl">
      <div class="ctrl-label"><span>Atracci&oacute;n a journals</span><span class="val" id="val-jstrength"></span></div>
      <input type="range" id="ctl-jstrength" min="5" max="200" step="5">
    </div>
    <div class="ctrl">
      <div class="ctrl-label"><span>Cohesi&oacute;n entre notas relacionadas</span><span class="val" id="val-pstrength"></span></div>
      <input type="range" id="ctl-pstrength" min="0" max="100" step="2">
    </div>
    <div class="ctrl">
      <div class="ctrl-label"><span>Distancia a journal</span><span class="val" id="val-jdist"></span></div>
      <input type="range" id="ctl-jdist" min="20" max="250" step="5">
    </div>
    <div class="ctrl">
      <div class="ctrl-label"><span>Margen anticolisi&oacute;n</span><span class="val" id="val-collide"></span></div>
      <input type="range" id="ctl-collide" min="0" max="30" step="1">
    </div>
    <div class="ctrl-buttons">
      <button id="reheat">Reorganizar</button>
      <button id="reset-forces">Restaurar</button>
    </div>
  </details>
</div>

<div class="legend">
  <span><span class="dot" style="background:var(--journal)"></span>Journal</span>
  <span><span class="dot" style="background:var(--page)"></span>Nota</span>
  <span>Tama&ntilde;o = num. de enlaces &middot; Rueda = zoom &middot; Arrastra = pan &middot; Arrastra un nodo = fijarlo</span>
</div>

<div class="tooltip" id="tooltip"></div>

<svg id="svg"></svg>

<script>__D3_SOURCE__</script>
<script>
const GRAPH = __DATA_JSON__;

const journals = GRAPH.journals.slice().sort((a,b) => a.date.localeCompare(b.date));
const pages = GRAPH.pages;
const edges = GRAPH.edges;

document.getElementById('stats').textContent =
  `${journals.length} journals · ${pages.length} notas · ${edges.length} enlaces`;

// ---- Layout constants ----
const JOURNAL_SPACING = 46;      // px between consecutive journals (uniform, order-based)
const MARGIN_X = 200;
const LINE_Y = 1500;              // baseline y for the journal line (lots of room above for vertical spread)
const TOP_MARGIN = 30;            // notes must stay at least this far from the top edge
const width = MARGIN_X * 2 + (journals.length - 1) * JOURNAL_SPACING;
const height = LINE_Y + 120;

const journalById = new Map();
journals.forEach((j, i) => {
  j.x = MARGIN_X + i * JOURNAL_SPACING;
  j.y = LINE_Y;
  j.fx = j.x;
  j.fy = j.y;
  journalById.set(j.id, j);
});

const degMaxEarly = Math.max(1, ...pages.map(p => p.degree));
const pageById = new Map();
pages.forEach((p, i) => {
  // seed position near the horizontal middle, spread out, above the line;
  // give each note a stable per-node jitter so the vertical spread reads as organic, not banded
  p.jitter = (Math.random() - 0.5) * 2;
  const norm = 1 - p.degree / degMaxEarly; // 0 = very connected (near line), 1 = barely connected (far)
  p.x = MARGIN_X + (journals.length / 2) * JOURNAL_SPACING + (Math.random() - 0.5) * 200;
  p.y = LINE_Y - 80 - norm * 500 - Math.random() * 150;
  pageById.set(p.id, p);
});

const nodeById = new Map([...journalById, ...pageById]);

const degMax = Math.max(1, ...pages.map(p => p.degree));
const radiusScale = d3.scaleSqrt().domain([0, degMax]).range([2.5, 22]);
const journalDegMax = Math.max(1, ...journals.map(j => j.degree));
const journalRadiusScale = d3.scaleSqrt().domain([0, journalDegMax]).range([3, 9]);

const linkData = edges.map(e => ({
  source: e.source, target: e.target, kind: e.kind
})).filter(e => nodeById.has(e.source) && nodeById.has(e.target));

// ---- SVG setup ----
const svg = d3.select('#svg');
const root = svg.append('g');

const zoom = d3.zoom()
  .scaleExtent([0.05, 8])
  .on('zoom', (event) => root.attr('transform', event.transform));
svg.call(zoom);

// initial view: fit the note cloud's width, anchor the baseline near the bottom of the viewport
// so the vertical spread above it is visible. Coordinates are raw SVG pixels (no viewBox scaling).
const initialScale = Math.min(1, (window.innerWidth - 60) / width);
const initialTransform = () => d3.zoomIdentity
  .translate(20, window.innerHeight - 80)
  .scale(Math.max(initialScale, 0.06))
  .translate(0, -LINE_Y);

svg.call(zoom.transform, initialTransform());

document.getElementById('reset-view').addEventListener('click', () => {
  svg.transition().duration(400).call(zoom.transform, initialTransform());
});

// ---- Baseline ----
root.append('line')
  .attr('x1', journals[0].x).attr('y1', LINE_Y)
  .attr('x2', journals[journals.length - 1].x).attr('y2', LINE_Y)
  .attr('stroke', 'var(--line)').attr('stroke-width', 2);

// year/month tick marks along the line (based on order, labeled with real date of first journal in run)
let lastLabel = null;
journals.forEach(j => {
  const label = j.date.slice(0, 7); // yyyy-mm
  if (label !== lastLabel) {
    lastLabel = label;
    root.append('text')
      .attr('x', j.x).attr('y', LINE_Y + 22)
      .attr('text-anchor', 'middle')
      .attr('class', 'journal-label')
      .style('display', 'none')
      .attr('data-monthmark', '1')
      .text(label);
    root.append('line')
      .attr('x1', j.x).attr('x2', j.x)
      .attr('y1', LINE_Y - 4).attr('y2', LINE_Y + 4)
      .attr('stroke', '#556').attr('stroke-width', 1)
      .attr('data-monthtick', '1');
  }
});

// ---- Edges ----
const linkSel = root.append('g').attr('stroke-linecap', 'round')
  .selectAll('line')
  .data(linkData)
  .join('line')
  .attr('stroke', 'var(--edge)')
  .attr('stroke-width', 1);

// ---- Journal nodes ----
const journalSel = root.append('g')
  .selectAll('circle.journal')
  .data(journals)
  .join('circle')
  .attr('class', 'journal')
  .attr('r', j => journalRadiusScale(j.degree))
  .attr('fill', 'var(--journal)')
  .attr('cx', j => j.x).attr('cy', j => j.y)
  .style('cursor', 'pointer')
  .on('mouseenter', (event, d) => showTooltip(event, d, true))
  .on('mousemove', moveTooltip)
  .on('mouseleave', hideTooltip)
  .on('click', (event, d) => focusNode(d));

const journalLabelSel = root.append('g')
  .selectAll('text.jlabel')
  .data(journals)
  .join('text')
  .attr('class', 'journal-label jlabel')
  .attr('x', j => j.x).attr('y', j => j.y + 26)
  .attr('text-anchor', 'middle')
  .style('display', 'none')
  .text(j => j.date);

// ---- Page (note) nodes ----
const pageSel = root.append('g')
  .selectAll('circle.page')
  .data(pages)
  .join('circle')
  .attr('class', 'page')
  .attr('r', p => radiusScale(p.degree))
  .attr('fill', 'var(--page)')
  .attr('fill-opacity', 0.85)
  .style('cursor', 'pointer')
  .call(drag());

const pageLabelSel = root.append('g')
  .selectAll('text.plabel')
  .data(pages)
  .join('text')
  .attr('class', 'node-label plabel')
  .attr('text-anchor', 'middle')
  .attr('dy', p => -(radiusScale(p.degree) + 4))
  .text(p => p.name);

pageSel
  .on('mouseenter', (event, d) => showTooltip(event, d, false))
  .on('mousemove', moveTooltip)
  .on('mouseleave', hideTooltip)
  .on('click', (event, d) => focusNode(d));

// ---- Force simulation ----
const degMax2 = degMaxEarly;

const DEFAULT_PARAMS = {
  spread: 500,      // vertical spread range for notes, by degree (px above the "close to line" offset)
  charge: 60,       // base repulsion magnitude between notes
  jstrength: 90,    // attraction strength to linked journals (x100 of forceLink strength, for a nicer slider range)
  pstrength: 15,    // cohesion strength between related notes (x100 of forceLink strength)
  jdist: 70,        // rest distance to linked journal
  collide: 3        // extra padding added to collision radius
};
const params = Object.assign({}, DEFAULT_PARAMS);

const linkForce = d3.forceLink(linkData)
  .id(d => d.id)
  .distance(d => {
    if (d.kind === 'journal-link' || d.kind === 'journal-tag') return params.jdist;
    return params.jdist + 20;
  })
  .strength(d => {
    if (d.kind === 'journal-link' || d.kind === 'journal-tag') return params.jstrength / 100;
    return params.pstrength / 100;
  });

const chargeForce = d3.forceManyBody()
  .strength(d => d.date ? 0 : -(params.charge + radiusScale(d.degree) * 4));

const collideForce = d3.forceCollide()
  .radius(d => (d.date ? journalRadiusScale(d.degree) : radiusScale(d.degree)) + params.collide)
  .iterations(2);

// The vertical spread slider controls both how far weakly-linked notes drift from the line
// AND how strongly they're pulled there, since forceLink pulls in straight-line (x+y) distance
// and would otherwise overpower a fixed, weak y-force and flatten everything back near the line.
function ySpreadStrength() { return 0.03 + (params.spread / 1600) * 0.5; }

const yForce = d3.forceY(d => {
  if (d.date) return LINE_Y;
  const norm = 1 - d.degree / degMax2; // 0 = very connected, 1 = barely connected
  return LINE_Y - 80 - norm * params.spread + d.jitter * 30;
}).strength(d => d.date ? 1 : ySpreadStrength());

const xForce = d3.forceX(d => d.x).strength(d => d.date ? 1 : 0.01);

const simulation = d3.forceSimulation([...journals, ...pages])
  .force('link', linkForce)
  .force('charge', chargeForce)
  .force('collide', collideForce)
  .force('y', yForce)
  .force('x', xForce)
  .alpha(1)
  .alphaDecay(0.02)
  .on('tick', ticked);

// re-apply every force's accessor so d3 recomputes its cached per-node values from the current `params`
function applyForces() {
  linkForce
    .distance(d => (d.kind === 'journal-link' || d.kind === 'journal-tag') ? params.jdist : params.jdist + 20)
    .strength(d => (d.kind === 'journal-link' || d.kind === 'journal-tag') ? params.jstrength / 100 : params.pstrength / 100);
  chargeForce.strength(d => d.date ? 0 : -(params.charge + radiusScale(d.degree) * 4));
  collideForce.radius(d => (d.date ? journalRadiusScale(d.degree) : radiusScale(d.degree)) + params.collide);
  yForce
    .y(d => {
      if (d.date) return LINE_Y;
      const norm = 1 - d.degree / degMax2;
      return LINE_Y - 80 - norm * params.spread + d.jitter * 30;
    })
    .strength(d => d.date ? 1 : ySpreadStrength());
  simulation.alpha(0.6).restart();
}

function ticked() {
  pages.forEach(p => {
    const r = radiusScale(p.degree);
    if (p.y > LINE_Y - TOP_MARGIN / 3) p.y = LINE_Y - TOP_MARGIN / 3; // keep above the line
    if (p.y < r + TOP_MARGIN) p.y = r + TOP_MARGIN;
  });

  linkSel
    .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);

  journalSel.attr('cx', d => d.x).attr('cy', d => d.y);
  journalLabelSel.attr('x', d => d.x).attr('y', d => d.y + 26);

  pageSel.attr('cx', d => d.x).attr('cy', d => d.y);
  pageLabelSel.attr('x', d => d.x).attr('y', d => d.y);
}

function drag() {
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.1).restart();
    d.fx = d.x; d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x; d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    // keep it pinned where the user left it
  }
  return d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended);
}

// ---- Tooltip ----
const tooltip = document.getElementById('tooltip');
function showTooltip(event, d, isJournal) {
  tooltip.style.display = 'block';
  if (isJournal) {
    tooltip.innerHTML = `<div class="t-name">${d.date}</div><div class="t-meta">${d.degree} enlaces &middot; ${d.file}</div>`;
  } else {
    tooltip.innerHTML = `<div class="t-name">${escapeHtml(d.name)}</div><div class="t-meta">${d.degree} enlaces &middot; ${d.file}</div>`;
  }
  moveTooltip(event);
  highlightConnections(d.id);
}
function moveTooltip(event) {
  tooltip.style.left = (event.clientX + 16) + 'px';
  tooltip.style.top = (event.clientY + 12) + 'px';
}
function hideTooltip() {
  tooltip.style.display = 'none';
  clearHighlight();
}
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

const neighborIndex = new Map();
linkData.forEach(e => {
  const s = typeof e.source === 'object' ? e.source.id : e.source;
  const t = typeof e.target === 'object' ? e.target.id : e.target;
  if (!neighborIndex.has(s)) neighborIndex.set(s, new Set());
  if (!neighborIndex.has(t)) neighborIndex.set(t, new Set());
  neighborIndex.get(s).add(t);
  neighborIndex.get(t).add(s);
});

function highlightConnections(nodeId) {
  const neigh = neighborIndex.get(nodeId) || new Set();
  linkSel.attr('stroke', d => {
    const s = d.source.id, t = d.target.id;
    return (s === nodeId || t === nodeId) ? 'var(--edge-active)' : 'var(--edge)';
  }).attr('stroke-width', d => (d.source.id === nodeId || d.target.id === nodeId) ? 2 : 1);

  pageSel.attr('fill-opacity', p => (p.id === nodeId || neigh.has(p.id)) ? 1 : 0.15);
  journalSel.attr('fill', j => (j.id === nodeId || neigh.has(j.id)) ? 'var(--journal-active)' : 'var(--journal)');
}
function clearHighlight() {
  linkSel.attr('stroke', 'var(--edge)').attr('stroke-width', 1);
  pageSel.attr('fill-opacity', 0.85);
  journalSel.attr('fill', 'var(--journal)');
}

function focusNode(d) {
  const scale = 2.2;
  const transform = d3.zoomIdentity
    .translate(window.innerWidth / 2 - d.x * scale, window.innerHeight / 2 - d.y * scale)
    .scale(scale);
  svg.transition().duration(500).call(zoom.transform, transform);
}

// ---- Search ----
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) { clearHighlight(); return; }
  const matches = pages.filter(p => p.name.toLowerCase().includes(q));
  pageSel.attr('fill-opacity', p => matches.includes(p) ? 1 : 0.08);
  pageSel.attr('fill', p => matches.includes(p) ? 'var(--accent)' : 'var(--page)');
  if (matches.length === 1) focusNode(matches[0]);
});
searchInput.addEventListener('blur', () => {
  if (!searchInput.value.trim()) {
    pageSel.attr('fill', 'var(--page)');
  }
});

// ---- Toggles ----
document.getElementById('toggle-labels').addEventListener('change', (e) => {
  pageLabelSel.style('display', e.target.checked ? null : 'none');
});
document.getElementById('toggle-jlabels').addEventListener('change', (e) => {
  journalLabelSel.style('display', e.target.checked ? null : 'none');
  root.selectAll('[data-monthmark]').style('display', e.target.checked ? null : 'none');
});

// ---- Force controls ----
const SLIDER_IDS = {
  spread: 'ctl-spread', charge: 'ctl-charge', jstrength: 'ctl-jstrength',
  pstrength: 'ctl-pstrength', jdist: 'ctl-jdist', collide: 'ctl-collide'
};
function syncSlidersFromParams() {
  Object.keys(SLIDER_IDS).forEach(key => {
    document.getElementById(SLIDER_IDS[key]).value = params[key];
    document.getElementById('val-' + key).textContent = params[key];
  });
}
Object.keys(SLIDER_IDS).forEach(key => {
  const input = document.getElementById(SLIDER_IDS[key]);
  input.addEventListener('input', () => {
    params[key] = +input.value;
    document.getElementById('val-' + key).textContent = params[key];
    applyForces();
  });
});
syncSlidersFromParams();

document.getElementById('reheat').addEventListener('click', () => {
  simulation.alpha(1).restart();
});
document.getElementById('reset-forces').addEventListener('click', () => {
  Object.assign(params, DEFAULT_PARAMS);
  syncSlidersFromParams();
  applyForces();
});

// hide dense page labels by default zoom-based (optional simple heuristic): nothing extra needed now.
</script>
</body>
</html>
"""

html_out = TEMPLATE.replace("__D3_SOURCE__", d3_src).replace("__DATA_JSON__", data_json)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_out)

print("wrote", OUT_PATH, len(html_out), "bytes")
