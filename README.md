# Logseq SemiLinear Graph

An experimental visualization for [Logseq](https://logseq.com/) graphs: *journals*
(daily notes) are placed on a single horizontal line ordered chronologically, and the
rest of the pages ("notes") float above it, positioned by a force simulation
(`d3-force`) based on how many links they have and which journals/pages they connect to.

The result is a kind of timeline: the more connected a note is, the closer it stays to
the line; more peripheral notes drift further up.

See [docs/architecture.md](docs/architecture.md) for how the generator and viewer work.

## Usage

```bash
python3 parse_graph.py /path/to/your/graph_data.json
python3 build_html.py
```

By default both scripts read the graph from `~/Notas` (edit the `NOTAS`,
`DATA_PATH`/`OUT_PATH` constants at the top of each script to point elsewhere). Open
`graph_view.html` in a browser (or serve it with `python3 -m http.server`).

## Privacy

`graph_data.json` and `graph_view.html` are generated artifacts that contain the actual
content of your graph (page names, dates, note titles) and are excluded via
`.gitignore` — they are never committed. Only the generator code is versioned.

## Requirements

- Python 3 (no external dependencies).
- A modern browser to open the resulting HTML.

D3.js (`vendor/d3.min.js`, v7.9.0) is vendored under its ISC license — see
[d3js.org](https://d3js.org/).

## License

Licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE).
