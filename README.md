# Logseq SemiLinear Graph

Visualización experimental para grafos de [Logseq](https://logseq.com/): los *journals*
(notas diarias) se colocan en una única línea horizontal ordenada cronológicamente, y el
resto de páginas ("notas") flotan por encima, posicionadas mediante una simulación de
fuerzas (`d3-force`) según cuántos enlaces tienen y a qué journals/páginas están conectadas.

El resultado es una especie de línea de tiempo: cuanto más conectada está una nota, más
cerca se queda de la línea; las notas más periféricas se dispersan hacia arriba.

## Cómo funciona

1. **`parse_graph.py`** recorre las carpetas `journals/` y `pages/` de un grafo de Logseq,
   extrae los enlaces `[[...]]` y `#tags`, resuelve los enlaces a fechas de journal
   (formato `[[Apr 27th, 2026]]`) contra los archivos `yyyy_MM_dd.md`, y vuelca todo a
   `graph_data.json` (nodos, aristas y grado de cada nodo).
2. **`build_html.py`** toma `graph_data.json` y genera `graph_view.html`: una página
   autocontenida (D3.js vendorizado en `vendor/d3.min.js`, sin dependencias de red) con
   el visualizador interactivo.

## Uso

```bash
python3 parse_graph.py /ruta/a/tu/graph_data.json
python3 build_html.py
```

Por defecto ambos scripts leen el grafo desde `~/Notas` (editar las constantes `NOTAS`,
`DATA_PATH`/`OUT_PATH` al principio de cada script para apuntar a otra ruta). Abre
`graph_view.html` en el navegador (o sírvelo con `python3 -m http.server`).

## Visualizador

- **Zoom / pan**: rueda del ratón y arrastre sobre el fondo.
- **Arrastrar un nodo**: lo fija en esa posición.
- **Buscador**: resalta notas por nombre.
- **Panel "Fuerzas del layout"**: controles en vivo para ajustar la simulación —
  separación vertical, repulsión entre notas, atracción a journals, cohesión entre notas
  relacionadas, distancia a journal y margen anticolisión. Botones para reorganizar o
  restaurar los valores por defecto.

## Privacidad

`graph_data.json` y `graph_view.html` son artefactos generados que contienen el
contenido real de tu grafo (nombres de páginas, fechas, títulos de notas) y están
excluidos vía `.gitignore` — nunca se commitean. Solo el código generador se versiona.

## Requisitos

- Python 3 (sin dependencias externas).
- Un navegador moderno para abrir el HTML resultante.

D3.js (`vendor/d3.min.js`, v7.9.0) está vendorizado bajo su licencia ISC —
ver [d3js.org](https://d3js.org/).
