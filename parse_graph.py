#!/usr/bin/env python3
import os, re, json, datetime, sys

NOTAS = os.path.expanduser("~/Notas")
JOURNALS_DIR = os.path.join(NOTAS, "journals")
PAGES_DIR = os.path.join(NOTAS, "pages")

MONTHS = {m: i+1 for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}

LINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
JOURNAL_LINK_RE = re.compile(
    r"^([A-Za-z]{3,9}) (\d{1,2})(?:st|nd|rd|th), (\d{4})$")
TAG_RE = re.compile(r"(?<!\S)#([A-Za-z0-9_/\-]+)")

def journal_filename_to_date(fname):
    # yyyy_MM_dd.md
    m = re.match(r"(\d{4})_(\d{2})_(\d{2})\.md$", fname)
    if not m:
        return None
    y, mo, d = map(int, m.groups())
    try:
        return datetime.date(y, mo, d)
    except ValueError:
        return None

def journal_link_to_date(text):
    m = JOURNAL_LINK_RE.match(text.strip())
    if not m:
        return None
    mon, day, year = m.groups()
    mon3 = mon[:3]
    if mon3 not in MONTHS:
        return None
    try:
        return datetime.date(int(year), MONTHS[mon3], int(day))
    except ValueError:
        return None

def strip_code_blocks(text):
    # remove fenced code blocks to avoid false-positive links inside code
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    return text

def extract_links(text):
    text = strip_code_blocks(text)
    links = LINK_RE.findall(text)
    tags = TAG_RE.findall(text)
    return links, tags

# ---- Journals ----
journal_by_date = {}   # date -> node id
journals = []          # list of {id, date}

for fname in sorted(os.listdir(JOURNALS_DIR)):
    if not fname.endswith(".md"):
        continue
    date = journal_filename_to_date(fname)
    if date is None:
        continue
    node_id = f"journal:{date.isoformat()}"
    journal_by_date[date] = node_id
    path = os.path.join(JOURNALS_DIR, fname)
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    links, tags = extract_links(text)
    journals.append({
        "id": node_id,
        "date": date.isoformat(),
        "raw_links": links,
        "raw_tags": tags,
        "file": fname,
    })

journals.sort(key=lambda j: j["date"])

# ---- Pages ----
pages = []
page_name_set = set()

for fname in sorted(os.listdir(PAGES_DIR)):
    if not fname.endswith(".md"):
        continue
    name = fname[:-3]
    # logseq encodes some path separators; leave as-is, decode %2F etc if present
    name = name.replace("%2F", "/").replace("___", "/")
    page_name_set.add(name)

for fname in sorted(os.listdir(PAGES_DIR)):
    if not fname.endswith(".md"):
        continue
    name = fname[:-3].replace("%2F", "/").replace("___", "/")
    path = os.path.join(PAGES_DIR, fname)
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    links, tags = extract_links(text)
    pages.append({
        "id": f"page:{name}",
        "name": name,
        "raw_links": links,
        "raw_tags": tags,
        "file": fname,
    })

page_ids_by_name = {p["name"]: p["id"] for p in pages}

# ---- Build edges ----
# journal -> page (journal content links to a page)
# journal -> journal (rare, via date link)
# page -> journal (page links to a specific journal date, e.g. source:: [[Apr 27th, 2026]])
# page -> page

edges = []  # {source, target, kind}
edge_seen = set()

def add_edge(src, tgt, kind):
    if src == tgt:
        return
    key = (src, tgt)
    if key in edge_seen:
        return
    edge_seen.add(key)
    edges.append({"source": src, "target": tgt, "kind": kind})

def resolve_link(raw):
    raw = raw.strip()
    # could be a block ref ((uuid)) - skip
    if raw.startswith("(("):
        return None
    # strip block/alias parts after '::' or '|' just in case
    date = journal_link_to_date(raw)
    if date is not None:
        return journal_by_date.get(date)
    return page_ids_by_name.get(raw)

for j in journals:
    for raw in j["raw_links"]:
        tgt = resolve_link(raw)
        if tgt:
            add_edge(j["id"], tgt, "journal-link")
    for tag in j["raw_tags"]:
        tgt = page_ids_by_name.get(tag)
        if tgt:
            add_edge(j["id"], tgt, "journal-tag")

for p in pages:
    for raw in p["raw_links"]:
        tgt = resolve_link(raw)
        if tgt:
            add_edge(p["id"], tgt, "page-link")
    for tag in p["raw_tags"]:
        tgt = page_ids_by_name.get(tag)
        if tgt:
            add_edge(p["id"], tgt, "page-tag")

# ---- Degree counts ----
degree = {}
for e in edges:
    degree[e["source"]] = degree.get(e["source"], 0) + 1
    degree[e["target"]] = degree.get(e["target"], 0) + 1

out_journals = [{
    "id": j["id"], "date": j["date"], "file": j["file"],
    "degree": degree.get(j["id"], 0),
} for j in journals]

out_pages = [{
    "id": p["id"], "name": p["name"], "file": p["file"],
    "degree": degree.get(p["id"], 0),
} for p in pages if degree.get(p["id"], 0) > 0]  # only pages that connect to something

# keep pages with 0 degree too? Include them but they'll float unattached.
out_pages_all = [{
    "id": p["id"], "name": p["name"], "file": p["file"],
    "degree": degree.get(p["id"], 0),
} for p in pages]

out_edges = [e for e in edges]

result = {
    "journals": out_journals,
    "pages": out_pages_all,
    "edges": out_edges,
    "stats": {
        "n_journals": len(out_journals),
        "n_pages": len(out_pages_all),
        "n_pages_connected": len(out_pages),
        "n_edges": len(out_edges),
    }
}

outpath = sys.argv[1] if len(sys.argv) > 1 else "graph_data.json"
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print(json.dumps(result["stats"], indent=2))
