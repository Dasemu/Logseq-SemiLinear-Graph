# CLAUDE.md

## Overview

Two standalone Python 3 scripts that turn a Logseq graph into a static, interactive
timeline visualization: `parse_graph.py` extracts the graph into `graph_data.json`,
`build_html.py` renders it into a self-contained `graph_view.html` (D3.js vendored,
no network dependencies, no external Python packages).

## Commands

- Run the generator: `python3 parse_graph.py /path/to/graph_data.json`
- Build the viewer: `python3 build_html.py`
- Syntax check (stand-in for lint/test, no linter or test suite in this repo):
  `python3 -m py_compile build_html.py parse_graph.py`

## Architecture

See [docs/architecture.md](docs/architecture.md) for the parse → build pipeline and
viewer controls.

## Conventions

- No external dependencies (stdlib only). Don't add any without discussing it first.
- Both scripts default to `~/Notas`; path constants live at the top of each file
  (`NOTAS`, `DATA_PATH`, `D3_PATH`, `OUT_PATH`).

## Workflow quirks

- `graph_data.json` and `graph_view.html` are generated, personal, and gitignored —
  never commit them.
- No `development` branch exists yet; until it is created, treat `main` as the base
  for PRs.

## Deployment

None — this produces a static HTML file to open locally or serve with
`python3 -m http.server`.

## Gotchas

- There is no linter, formatter, or test suite installed in this repo; CI and hooks
  only run a `py_compile` syntax check.
