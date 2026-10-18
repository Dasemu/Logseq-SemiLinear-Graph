# Architecture

## How it works

1. **`parse_graph.py`** walks the `journals/` and `pages/` folders of a Logseq graph,
   extracts `[[...]]` links and `#tags`, resolves journal-date links (format
   `[[Apr 27th, 2026]]`) against the `yyyy_MM_dd.md` files, and dumps everything to
   `graph_data.json` (nodes, edges, and each node's degree).
2. **`build_html.py`** takes `graph_data.json` and generates `graph_view.html`: a
   self-contained page (D3.js vendored in `vendor/d3.min.js`, no network dependencies)
   with the interactive visualizer.

Both scripts default to reading the graph from `~/Notas`; edit the `NOTAS`,
`DATA_PATH`/`OUT_PATH` constants at the top of each script to point elsewhere.

## Viewer

- **Zoom / pan**: mouse wheel and drag on the background.
- **Drag a node**: pins it at that position.
- **Search box**: highlights notes by name.
- **"Layout forces" panel**: live controls for the simulation — vertical spread,
  repulsion between notes, attraction to journals, cohesion between related notes,
  distance to journal, and anti-collision padding. Buttons to reheat the simulation or
  restore the defaults.

## Generated artifacts

`graph_data.json` and `graph_view.html` contain the actual content of a personal
Logseq graph (page names, dates, note titles) and are excluded via `.gitignore` —
they are never committed. Only the generator code is versioned.
