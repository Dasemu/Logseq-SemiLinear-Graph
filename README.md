# Logseq SemiLinear Graph

An experimental visualization for [Logseq](https://logseq.com/) graphs: *journals*
(daily notes) are placed on a single horizontal line ordered chronologically, and the
rest of the pages ("notes") float above it, positioned by a force simulation
(`d3-force`) based on how many links they have and which journals/pages they connect to.

The result is a kind of timeline: the more connected a note is, the closer it stays to
the line; more peripheral notes drift further up.

## How it works

1. **`parse_graph.py`** walks the `journals/` and `pages/` folders of a Logseq graph,
   extracts `[[...]]` links and `#tags`, resolves journal-date links (format
   `[[Apr 27th, 2026]]`) against the `yyyy_MM_dd.md` files, and dumps everything to
   `graph_data.json` (nodes, edges, and each node's degree).
2. **`build_html.py`** takes `graph_data.json` and generates `graph_view.html`: a
   self-contained page (D3.js vendored in `vendor/d3.min.js`, no network dependencies)
   with the interactive visualizer.

## Usage

```bash
python3 parse_graph.py /path/to/your/graph_data.json
python3 build_html.py
```

By default both scripts read the graph from `~/Notas` (edit the `NOTAS`,
`DATA_PATH`/`OUT_PATH` constants at the top of each script to point elsewhere). Open
`graph_view.html` in a browser (or serve it with `python3 -m http.server`).

## Viewer

- **Zoom / pan**: mouse wheel and drag on the background.
- **Drag a node**: pins it at that position.
- **Search box**: highlights notes by name.
- **"Layout forces" panel**: live controls for the simulation — vertical spread,
  repulsion between notes, attraction to journals, cohesion between related notes,
  distance to journal, and anti-collision padding. Buttons to reheat the simulation or
  restore the defaults.

## Privacy

`graph_data.json` and `graph_view.html` are generated artifacts that contain the actual
content of your graph (page names, dates, note titles) and are excluded via
`.gitignore` — they are never committed. Only the generator code is versioned.

## Requirements

- Python 3 (no external dependencies).
- A modern browser to open the resulting HTML.

D3.js (`vendor/d3.min.js`, v7.9.0) is vendored under its ISC license — see
[d3js.org](https://d3js.org/).
