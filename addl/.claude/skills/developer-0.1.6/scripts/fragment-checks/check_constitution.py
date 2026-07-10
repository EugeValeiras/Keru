#!/usr/bin/env python3
"""check_constitution.py -- the deterministic subset of the RDAG Constitution Check.

Runtime expression of D-01 Architecture Supremacy (see ../shared/constitution.md).
Run at D3 (and re-run at D5 for drift) over a Developer artifact (`plan.md`,
`tasks.md`, or implemented code surfaced as text) against the landed, pinned
release `architecture/arch-X.Y.Z/`:

    check_constitution.py specs/NNN-<slug>/plan.md architecture/arch-1.0.0/

It mechanically verifies all six questions, including Q3 (call-chain layering) as a
deterministic directed-graph check:

    Q1  catalog membership   -- every service the artifact names is in the catalog
    Q2  category-suffix       -- every catalog service name ends *Manager/*Engine/*Access
    Q3  call-chain layering   -- parse the call graph (mermaid or arrow notation) and
                                 reject illegal layer transitions (Manager->Manager sync,
                                 Engine->Manager, Client->ResourceAccess, ...)
    Q4  structural lineage    -- every artifact-used service lists >=1 structural S-NN
    Q5  NFR coupling lineage   -- every NFR in the register cites a coupling C-NN in Source
    Q6  binding-ADR conformance -- every binding ADR (Binding: Yes) is referenced by the artifact

Q1/Q4/Q6 hold the *artifact* to the binding architecture; Q2/Q5 verify the
integrity of the binding inputs themselves. All are NON-WAIVABLE (Q1-Q4 excluded
from any Complexity-Tracking waiver, Q5-Q6 per RDAG): a "No" is reported as a
finding so the gate cannot pass. The legal resolution is a back-channel request
(catalog-amendment / ADR / residue-analysis), never an inline edit.

Limitation (honest, by design): services are detected by the *Manager/*Engine/
*Access naming pattern and IDs by their RDAG id scheme. A service that violates
naming entirely (no suffix) or an unwritten reference is out of scope for the
deterministic check and must be caught by the heuristic review / the operator.

Exit codes:  0 all checked questions pass / 1 one or more findings (gate blocked)
             2 usage error / required input missing / unparseable binding input

Stdlib-only. Self-test:  check_constitution.py --self-test
"""

import argparse
import glob
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

# --- RDAG id-scheme / naming patterns (the only things with a fixed shape) -----
SERVICE_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:Manager|Engine|Access)\b")
SUFFIX_RE = re.compile(r"(?:Manager|Engine|Access)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
# a per-service catalog entry heading is a bare service name (possibly backticked); the
# category groupings ('### Managers', '### ResourceAccess') are excluded by requiring a
# level-4+ heading AND a full-string Manager/Engine/Access name (so 'ResourceAccess' /
# plural 'Managers' never read as services).
SERVICE_NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(?:Manager|Engine|Access)$")
CATALOG_CATEGORY_WORDS = {"ResourceAccess", "Managers", "Engines", "Resources", "Clients"}
IDENT_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")
S_RE = re.compile(r"\bS-\d{2,}\b")          # structural stressor
C_RE = re.compile(r"\bC-\d{2,}\b")          # coupling / topology
NFR_RE = re.compile(r"\bNFR-\d{2,}\b")
ADR_RE = re.compile(r"\bADR-\d{2,}\b")
# a binding ADR declares "Binding: Yes" -- either as a colon line ("Binding: Yes") or as a
# `## Binding scope` table row ("| **Binding** | Yes |"). The real handoff uses ONLY the
# table form, so accept both (the colon-only pattern made Q6 pass vacuously against it).
BINDING_YES_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?\|?\s*\**\s*binding\**\s*(?::|\|)\s*\**\s*yes\b")


class FormatError(Exception):
    """A required binding input is missing or cannot be parsed."""


class QResult:
    """One Constitution-Check question outcome. ok is True/False, or None for SKIP."""

    def __init__(self, q, name, ok, findings=None):
        self.q = q
        self.name = name
        self.ok = ok
        self.findings = findings or []

    @property
    def status(self):
        if self.ok is None:
            return "SKIP"
        return "PASS" if self.ok else "FAIL"


# --- markdown table parsing ----------------------------------------------------
def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def _is_separator(line):
    line = line.strip()
    if not line.startswith("|"):
        return False
    cells = [c.strip() for c in _split_row(line)]
    cells = [c for c in cells if c]
    return bool(cells) and all(re.fullmatch(r":?-{1,}:?", c) for c in cells)


def parse_tables(text):
    """Return [{'header': [...], 'rows': [[...], ...]}] for every GFM pipe table."""
    tables = []
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < n and _is_separator(lines[i + 1]):
            header = _split_row(line)
            rows, j = [], i + 2
            while j < n and lines[j].strip().startswith("|"):
                rows.append(_split_row(lines[j]))
                j += 1
            tables.append({"header": header, "rows": rows})
            i = j
        else:
            i += 1
    return tables


def find_table(tables, keyword):
    for t in tables:
        if any(keyword in h.lower() for h in t["header"]):
            return t
    return None


def col_index(header, *keywords):
    for kw in keywords:
        for idx, h in enumerate(header):
            if kw in h.lower():
                return idx
    return None


def _first_ident(cell):
    m = IDENT_RE.search(re.sub(r"[`*_]", "", cell))
    return m.group(0) if m else ""


# --- loaders for the landed release -------------------------------------------
def load_catalog(text):
    """service name -> Stressors-absorbed cell text. Supports two real shapes:
    (1) a single wide table with Service + Stressors-absorbed columns, and (2) the landed
    handoff's per-service sections -- '#### `Name`' followed by a Field/Value table with a
    'Stressors absorbed' row (the actual ev-charging catalog format)."""
    # (1) single wide table
    t = find_table(parse_tables(text), "stressor")
    if t and col_index(t["header"], "service") is not None:
        si = col_index(t["header"], "service")
        ti = col_index(t["header"], "stressor")
        catalog = {}
        for row in t["rows"]:
            if si >= len(row):
                continue
            name = _first_ident(row[si])
            if name:
                catalog[name] = row[ti] if (ti is not None and ti < len(row)) else ""
        if catalog:
            return catalog

    # (2) per-service sections ('#### `Name`' + Field/Value table)
    catalog = {}
    cur = None
    for ln in text.splitlines():
        m = HEADING_RE.match(ln)
        if m:
            if len(m.group(1)) >= 4:
                title = re.sub(r"[`*]", "", m.group(2)).strip()
                cur = title if (SERVICE_NAME_RE.match(title) and title not in CATALOG_CATEGORY_WORDS) else None
                if cur:
                    catalog.setdefault(cur, "")
            else:
                cur = None  # a category grouping ('### Managers') ends any service entry
            continue
        s = ln.strip()
        if cur and s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 2 and re.sub(r"[`*]", "", cells[0]).strip().lower() in (
                    "stressors absorbed", "stressors-absorbed", "stressors"):
                catalog[cur] = cells[1]
    if not catalog:
        raise FormatError("service-catalog: no wide table with a 'Stressors-absorbed' column "
                          "and no per-service '#### `Name`' sections found")
    return catalog


def load_nfrs(text):
    """[(NFR-id, Source cell text)] from the nfr-register table."""
    t = find_table(parse_tables(text), "source")
    if not t:
        raise FormatError("nfr-register: no table with a 'Source' column")
    src_i = col_index(t["header"], "source")
    nfrs = []
    for row in t["rows"]:
        m = NFR_RE.search(" ".join(row))
        if not m:
            continue
        src = row[src_i] if (src_i is not None and src_i < len(row)) else ""
        nfrs.append((m.group(0), src))
    return nfrs


def load_binding_adrs(decisions_dir):
    """Set of ADR ids whose file declares Binding: Yes. Empty if the dir is absent."""
    binding = set()
    if not os.path.isdir(decisions_dir):
        return binding
    for path in sorted(glob.glob(os.path.join(decisions_dir, "*.md"))):
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        if not BINDING_YES_RE.search(body):
            continue
        m = ADR_RE.search(os.path.basename(path)) or ADR_RE.search(body)
        if m:
            binding.add(m.group(0))
    return binding


# --- the checks ----------------------------------------------------------------
def check_q1(artifact_services, catalog_names):
    bad = [s for s in sorted(artifact_services) if s not in catalog_names]
    return QResult("Q1", "catalog membership", not bad,
                   ["service '%s' is referenced but not in the service-catalog" % s for s in bad])


def check_q2(catalog):
    bad = [n for n in sorted(catalog) if not SUFFIX_RE.search(n)]
    return QResult("Q2", "category-suffix naming", not bad,
                   ["catalog service '%s' lacks a *Manager/*Engine/*Access suffix" % n for n in bad])


def check_q4(artifact_services, catalog):
    bad = [s for s in sorted(artifact_services)
           if s in catalog and not S_RE.search(catalog[s])]
    return QResult("Q4", "structural-stressor lineage", not bad,
                   ["service '%s' lists no structural S-NN in Stressors-absorbed" % s for s in bad])


def check_q5(nfrs):
    bad = [nid for nid, src in nfrs if not C_RE.search(src)]
    return QResult("Q5", "NFR coupling lineage", not bad,
                   ["%s records no coupling C-NN in its Source" % nid for nid in bad])


# Q6 = CONFORMANCE, not citation. Each binding ADR carries a "Conformance check" field
# (the `## Binding scope` table). Where that condition is a call-graph / transport rule
# we EVALUATE it against the plan; where it is not, we fall back to citation + mechanism
# presence (the documented ceiling -- full semantic evaluation is undecidable).
LAYER_WORD = {"manager": "Manager", "engine": "Engine", "access": "Access",
              "resourceaccess": "Access", "client": "Client", "resource": "Resource"}
# runtime mechanisms a conformance condition may mandate (async/transport family). Bare
# "event" is intentionally excluded -- it matches "eventually" and friends.
MECH_RE = re.compile(r"pub[\s/_-]?sub|pubsub|dapr|asynchronous|\basync\b|message\s*(?:bus|broker|queue)"
                     r"|messaging|message\s+queue|\bqueue\b|broker|\btopic\b", re.IGNORECASE)
NEG_SYNC_RE = re.compile(r"\b(?:no|not|never|without|forbid\w*|must\s+not|avoid)\b[^.]{0,60}synchronous"
                         r"|synchronous[^.]{0,60}\b(?:forbidden|not\s+allowed|prohibited|disallowed)\b",
                         re.IGNORECASE)


def _conformance_cell(body):
    """The 'Conformance check' value from an ADR's `## Binding scope` table ('' if none)."""
    for t in parse_tables(body):
        for row in t["rows"]:
            if row and "conformance" in row[0].lower():
                val = row[1] if len(row) > 1 else ""
                return re.sub(r"[`*]", "", val).strip()
    return ""


def load_binding_adr_conformance(decisions_dir):
    """{ADR-id: conformance-condition-text} for every Binding: Yes ADR (text '' if absent)."""
    out = {}
    if not os.path.isdir(decisions_dir):
        return out
    for path in sorted(glob.glob(os.path.join(decisions_dir, "*.md"))):
        with open(path, encoding="utf-8") as fh:
            body = fh.read()
        if not BINDING_YES_RE.search(body):
            continue
        m = ADR_RE.search(os.path.basename(path)) or ADR_RE.search(body)
        if m:
            out[m.group(0)] = _conformance_cell(body)
    return out


def evaluate_conformance(adr, cond, artifact_text, plan_graph_text):
    """Evaluate ONE binding ADR's conformance condition against the plan.
    Returns a list of findings (empty == conforms)."""
    findings = []
    if adr not in set(ADR_RE.findall(artifact_text)):
        return ["binding %s is not referenced anywhere in the artifact" % adr]
    if not cond:
        return []  # no machine-checkable condition -- citation is the bar (documented ceiling)

    low = cond.lower()

    # (a) sync-prohibition: "no synchronous Manager call" / "Managers must not call ... sync"
    if NEG_SYNC_RE.search(cond):
        tedges, cats, labels, found = _scan_call_graph(plan_graph_text)
        if not found:
            findings.append("%s conformance names a call-graph rule (no synchronous call) but the "
                            "plan carries no call chain to evaluate it against" % adr)
        else:
            layers = [LAYER_WORD[w] for w in re.findall(r"resourceaccess|manager|engine|access|client|resource", low)
                      if w in LAYER_WORD]
            target = layers[0] if layers else "Manager"
            for a, b, is_async in tedges:
                sc, dc = _classify(a, cats, labels), _classify(b, cats, labels)
                if sc == target and dc == target and not is_async:
                    findings.append("%s conformance VIOLATED: a synchronous %s->%s call %r -> %r "
                                    "appears in the plan (the condition forbids it)"
                                    % (adr, sc, dc, labels.get(a, a), labels.get(b, b)))

    # (b) mechanism-presence: the condition mandates a runtime mechanism; the plan must
    #     actually NAME it (citing the ADR id is not adoption).
    if MECH_RE.search(cond) and not MECH_RE.search(artifact_text):
        findings.append("%s conformance requires an async/transport mechanism (e.g. %s) but the "
                        "plan names none -- citing the ADR is not adopting it"
                        % (adr, MECH_RE.search(cond).group(0).strip()))
    return findings


def check_q6(binding_adrs, conformance, artifact_text, plan_graph_text):
    findings = []
    for adr in sorted(binding_adrs):
        findings.extend(evaluate_conformance(adr, conformance.get(adr, ""), artifact_text, plan_graph_text))
    return QResult("Q6", "binding-ADR conformance", not findings, findings)


# --- Q3 call-chain layering (deterministic directed-graph check) ---------------
# The call chain is the use-case Architectural Context, preserved verbatim in the
# spec; it is a mermaid graph (subgraph Managers/Engines/ResourceAccess/...) or an
# arrow-notation chain ("Client -> XManager -> YEngine -> ZAccess"). Q3 is
# NON-WAIVABLE: parse the graph, classify each node by layer, and reject any edge
# that is not a legal downward synchronous transition.
ARROW_RE = re.compile(r"-+\.?-*>")
SUBGRAPH_CAT = {
    "managers": "Manager", "manager": "Manager",
    "engines": "Engine", "engine": "Engine",
    "resourceaccess": "Access", "resource access": "Access", "resourceaccesses": "Access",
    "resources": "Resource", "resource": "Resource",
    "clients": "Client", "client": "Client",
}
# legal SYNCHRONOUS downward edges (a cross-Manager / cross-Engine call must instead
# go through a queue / pub-sub, which is modelled as an edge to a Resource, not a
# direct Manager->Manager / Engine->Engine edge).
LEGAL_EDGES = {
    ("Client", "Manager"),
    ("Manager", "Engine"), ("Manager", "Access"),
    ("Engine", "Access"),
    ("Access", "Resource"),
}
_NODE_DECL_RE = re.compile(r'([A-Za-z][\w-]*)\s*[\[({]+\s*"?\(?([^"\])}]*?)\)?"?\s*[\])}]+')


def _classify(nid, cats, labels):
    if nid in cats:
        return cats[nid]
    lab = labels.get(nid, nid)
    for suf, cat in (("Manager", "Manager"), ("Engine", "Engine"), ("Access", "Access")):
        if lab.endswith(suf) or nid.endswith(suf):
            return cat
    if "client" in lab.lower():
        return "Client"
    return "Unknown"


def _scan_call_graph(text):
    """Core scan: return (typed_edges[(src,dst,is_async)], cats, labels, found).
    is_async is True for a dashed mermaid arrow (-.->), the pub/sub modelling -- Q3
    ignores the flag; Q6 conformance uses it to tell a synchronous call from an
    async one."""
    cats, labels, edges = {}, {}, []
    found = False

    def edges_in(line):
        seg = re.sub(r"\|[^|]*\|", " ", line)          # drop mermaid edge labels |x|
        parts = re.split(r"(%s)" % ARROW_RE.pattern, seg)
        segs, arrows = parts[0::2], parts[1::2]
        nodes = []
        for i, sg in enumerate(segs):
            ids = re.findall(r"[A-Za-z][\w-]*", sg)
            nodes.append((ids[-1] if i == 0 else ids[0]) if ids else None)
        out = []
        for i, arr in enumerate(arrows):
            a, b = nodes[i], nodes[i + 1]
            if a and b:
                out.append((a, b, "." in arr))         # dashed arrow -> async
        return out

    for mm in re.finditer(r"```mermaid\s*(.*?)```", text, re.DOTALL | re.IGNORECASE):
        found = True
        cur = None
        for ln in mm.group(1).splitlines():
            s = ln.strip()
            if not s:
                continue
            sg = re.match(r"subgraph\s+(.+)$", s, re.I)
            if sg:
                cur = SUBGRAPH_CAT.get(sg.group(1).strip().strip('"').lower())
                continue
            if s.lower() == "end":
                cur = None
                continue
            if not ARROW_RE.search(s):
                for nid, lab in _NODE_DECL_RE.findall(s):
                    labels[nid] = lab.strip()
                    if cur:
                        cats[nid] = cur
            else:
                edges.extend(edges_in(s))

    # arrow-notation chains outside any mermaid block ("Call Chain: A -> B -> C").
    # Keep a prose edge ONLY if both endpoints classify to a known layer -- otherwise a
    # stray "->" in prose would emit spurious findings. (Mermaid edges, above, are an
    # explicit call graph and are kept unconditionally.)
    no_mm = re.sub(r"```mermaid.*?```", "", text, flags=re.DOTALL | re.IGNORECASE)
    for ln in no_mm.splitlines():
        if not ARROW_RE.search(ln):
            continue
        for a, b, asy in edges_in(ln):
            if _classify(a, cats, labels) != "Unknown" and _classify(b, cats, labels) != "Unknown":
                edges.append((a, b, asy))
                found = True
    return edges, cats, labels, found


def parse_call_graph(text):
    """Return (edges[(src_id,dst_id)], cats{id->cat}, labels{id->label}, found)."""
    tedges, cats, labels, found = _scan_call_graph(text)
    return [(a, b) for a, b, _ in tedges], cats, labels, found


def _why(sc, dc):
    if sc == "Manager" and dc == "Manager":
        return " (Managers must not call Managers synchronously -- use a queue / pub-sub)"
    if sc == "Engine" and dc == "Manager":
        return " (Engines must not call Managers)"
    if sc == "Engine" and dc == "Engine":
        return " (cross-Engine calls must go through a queue)"
    if sc == "Client":
        return " (Clients call only Managers)"
    if sc == "Access" and dc != "Resource":
        return " (a ResourceAccess may call only its Resource)"
    return ""


def check_q3(call_text):
    edges, cats, labels, found = parse_call_graph(call_text)
    if not found:
        return QResult("Q3", "call-chain layering", False,
                       ["no call chain found to check -- provide the use-case Architectural "
                        "Context Call Chain (Q3 is NON-WAIVABLE and cannot be skipped)"])
    findings, seen = [], set()
    for a, b in edges:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        sc, dc = _classify(a, cats, labels), _classify(b, cats, labels)
        an, bn = labels.get(a, a), labels.get(b, b)
        if sc == "Unknown" or dc == "Unknown":
            findings.append("cannot classify call edge %r -> %r by layer "
                            "(name services by *Manager/*Engine/*Access)" % (an, bn))
        elif (sc, dc) not in LEGAL_EDGES:
            findings.append("illegal layer transition %s->%s: %r -> %r%s"
                            % (sc, dc, an, bn, _why(sc, dc)))
    if found and not edges:
        findings.append("the call chain declares nodes but no edges -- cannot verify layering")
    return QResult("Q3", "call-chain layering", not findings, findings)


def _call_chain_text(artifact_text, artifact_path):
    """The call chain lives in the UC Architectural Context, preserved in the spec.
    Prefer the artifact; if it carries no call chain, fall back to a sibling spec.md."""
    _, _, _, found = parse_call_graph(artifact_text)
    if found:
        return artifact_text
    sib = os.path.join(os.path.dirname(os.path.abspath(artifact_path)), "spec.md")
    if os.path.isfile(sib) and os.path.abspath(sib) != os.path.abspath(artifact_path):
        with open(sib, encoding="utf-8") as fh:
            return fh.read()
    return artifact_text


def run_checks(artifact_path, arch_dir):
    """Load the release + artifact and return the ordered list of QResults."""
    with open(artifact_path, encoding="utf-8") as fh:
        artifact = fh.read()

    catalog_path = os.path.join(arch_dir, "system-design", "service-catalog.md")
    nfr_path = os.path.join(arch_dir, "system-design", "nfr-register.md")
    decisions_dir = os.path.join(arch_dir, "decisions")

    for required in (catalog_path, nfr_path):
        if not os.path.isfile(required):
            raise FormatError("required binding input not found: %s" % required)

    with open(catalog_path, encoding="utf-8") as fh:
        catalog = load_catalog(fh.read())
    with open(nfr_path, encoding="utf-8") as fh:
        nfrs = load_nfrs(fh.read())
    binding_adrs = load_binding_adrs(decisions_dir)
    conformance = load_binding_adr_conformance(decisions_dir)

    # exclude the category word 'ResourceAccess' (SERVICE_RE matches it, but it is the
    # subgraph/Category label in the verbatim Architectural Context, never a service name)
    artifact_services = set(SERVICE_RE.findall(artifact)) - CATALOG_CATEGORY_WORDS
    call_text = _call_chain_text(artifact, artifact_path)

    return [
        check_q1(artifact_services, set(catalog)),
        check_q2(catalog),
        check_q3(call_text),
        check_q4(artifact_services, catalog),
        check_q5(nfrs),
        check_q6(binding_adrs, conformance, artifact, call_text),
    ]


def report(results, artifact_path, arch_dir, as_json=False):
    if as_json:
        import json
        payload = {
            "artifact": artifact_path,
            "arch": arch_dir,
            "passed": not any(r.ok is False for r in results),
            "results": [{"q": r.q, "name": r.name, "status": r.status,
                         "findings": r.findings} for r in results],
        }
        print(json.dumps(payload, indent=2))
        return

    print("Constitution Check (Q1-Q6) -- deterministic subset")
    print("  artifact: %s" % artifact_path)
    print("  release:  %s" % arch_dir)
    print()
    for r in results:
        n = len(r.findings)
        suffix = ""
        if r.ok is False:
            suffix = "  (%d finding%s)" % (n, "" if n == 1 else "s")
        print("  %-3s %-28s %s%s" % (r.q, r.name, r.status, suffix))
    findings = [(r, f) for r in results if r.ok is False for f in r.findings]
    if findings:
        print()
        print("Findings (back-channel request, never an inline fix -- D-01):")
        for r, f in findings:
            print("  - [%s] %s" % (r.q, f))
    print()
    if any(r.ok is False for r in results):
        print("VERDICT: BLOCKED -- resolve the findings by amending the architecture "
              "or raising an ADR; the gate cannot pass.")
    else:
        print("VERDICT: Q1-Q6 all PASS (deterministic).")


# --- self-test -----------------------------------------------------------------
_BASE = {
    "system-design/service-catalog.md": (
        "# Service catalog -- arch-1.0.0\n\n"
        "| Service | Category | Stressors-absorbed |\n"
        "|---|---|---|\n"
        "| OrderManager | Manager | S-01, S-03 |\n"
        "| PricingEngine | Engine | S-02 |\n"
        "| LedgerAccess | Access | S-04 |\n"
    ),
    "system-design/nfr-register.md": (
        "# NFR register -- arch-1.0.0\n\n"
        "| NFR | Statement | Source |\n"
        "|---|---|---|\n"
        "| NFR-01 | p99 latency < 200ms | C-01 (topology) |\n"
        "| NFR-02 | 99.95% availability | C-02 (coupling) |\n"
    ),
    "decisions/ADR-001.md": "# ADR-001 -- gRPC for inter-service calls\n\nStatus: Accepted\nBinding: Yes\n",
    "decisions/ADR-002.md": "# ADR-002 -- PostgreSQL for the ledger\n\nStatus: Accepted\nBinding: Yes\n",
    "decisions/ADR-003.md": "# ADR-003 -- Structured JSON logging\n\nStatus: Accepted\nBinding: No\n",
    "plan.md": (
        "# Implementation plan -- 001-order-capture (UC-001)\n\n"
        "## Architectural Context\n"
        "Call Chain: Client -> OrderManager -> PricingEngine -> LedgerAccess\n\n"
        "## Approach\n"
        "The OrderManager coordinates capture, calls the PricingEngine to price\n"
        "the basket, and persists through the LedgerAccess.\n\n"
        "## Constitution Check\n"
        "- Q6: transport conforms to ADR-001 (gRPC); persistence conforms to ADR-002.\n"
    ),
}

# a binding ADR carrying a real machine-checkable Conformance check (Dapr pub/sub for
# Manager-to-Manager; no synchronous Manager call) -- shape of the real ev-charging ADR-001.
_ADR1_DAPR = (
    "# ADR-001 -- Adopt Dapr for inter-service invocation and pub/sub\n\n"
    "Status: Accepted\nBinding: Yes\n\n"
    "## Binding scope\n\n"
    "| Field | Value |\n|---|---|\n"
    "| **Binding** | Yes |\n"
    "| **Conformance check** | The plan's Manager -> Manager paths go through Dapr pub/sub; "
    "no synchronous Manager call appears. |\n"
)

_CASES = [
    ("baseline -- all checked questions pass", {}, None),
    ("Q1 -- artifact names a service absent from the catalog",
     {"plan.md": _BASE["plan.md"] + "\nLater the BillingManager issues an invoice.\n"}, "Q1"),
    ("Q2 -- catalog service lacks a category suffix",
     {"system-design/service-catalog.md": _BASE["system-design/service-catalog.md"]
      + "| PaymentService | Service | S-05 |\n"}, "Q2"),
    ("Q3 -- call chain has an illegal layer transition (Engine->Manager)",
     {"plan.md": _BASE["plan.md"].replace(
         "Call Chain: Client -> OrderManager -> PricingEngine -> LedgerAccess",
         "Call Chain: Client -> OrderManager -> PricingEngine -> OrderManager")}, "Q3"),
    ("Q4 -- a used service has no structural S-NN",
     {"system-design/service-catalog.md": _BASE["system-design/service-catalog.md"].replace(
         "| LedgerAccess | Access | S-04 |", "| LedgerAccess | Access | -- |")}, "Q4"),
    ("Q5 -- an NFR cites no coupling C-NN",
     {"system-design/nfr-register.md": _BASE["system-design/nfr-register.md"].replace(
         "| NFR-02 | 99.95% availability | C-02 (coupling) |",
         "| NFR-02 | 99.95% availability | (pending) |")}, "Q5"),
    ("Q6 -- a binding ADR is never referenced by the artifact",
     {"plan.md": _BASE["plan.md"].replace("and persistence conforms to ADR-002.",
                                          "and persistence uses PostgreSQL.").replace(
         "; persistence conforms to ADR-002.", "; persistence uses PostgreSQL.")}, "Q6"),
    # Q6 CONFORMANCE (C1): ADR-001 mandates Dapr pub/sub but the plan cites the ADR yet
    # names only gRPC -- citation is satisfied, conformance is not.
    ("Q6 -- binding ADR cited but its conformance (Dapr pub/sub) is not adopted by the plan",
     {"decisions/ADR-001.md": _ADR1_DAPR}, "Q6"),
    # a verbatim Architectural Context carries the 'ResourceAccess' category word (subgraph +
    # Category column); Q1 must NOT read it as an off-catalog service. (Regression: it did.)
    ("baseline + verbatim AC with the 'ResourceAccess' category word still passes (no Q1 false positive)",
     {"plan.md": _BASE["plan.md"]
      + "\n## Architectural Context\n```mermaid\ngraph LR\n    subgraph ResourceAccess\n        LedgerAccess\n    end\n    OrderManager --> LedgerAccess\n```\n\n"
      + "| Service | Category | Role |\n|---|---|---|\n| `LedgerAccess` | ResourceAccess | persists |\n"}, None),
]


def _build(tmp, overrides):
    files = dict(_BASE)
    files.update(overrides)
    for rel, content in files.items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    return os.path.join(tmp, "plan.md"), tmp


def self_test():
    import tempfile

    passed = 0
    failed = 0
    for label, overrides, expect_fail in _CASES:
        with tempfile.TemporaryDirectory() as tmp:
            artifact, arch = _build(tmp, overrides)
            results = run_checks(artifact, arch)
            by_q = {r.q: r for r in results}
            try:
                for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"):
                    if q == expect_fail:
                        assert by_q[q].ok is False, "%s should FAIL but passed" % q
                        assert by_q[q].findings, "%s failed without a finding message" % q
                    else:
                        assert by_q[q].ok is True, (
                            "%s should PASS but failed: %r" % (q, by_q[q].findings))
            except AssertionError as exc:
                failed += 1
                print("  FAIL  %-55s %s" % (label, exc))
                continue
            passed += 1
            print("  ok    %s" % label)

    # --- Q6 conformance: direct unit tests of evaluate_conformance ----------------
    def uexpect(label, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  ok    %s" % label)
        else:
            failed += 1
            print("  FAIL  %s" % label)

    _COND = "The plan's Manager -> Manager paths go through Dapr pub/sub; no synchronous Manager call appears."
    # SEEDED: a synchronous Manager->Manager edge in the plan (a solid arrow) violates it
    sync_plan = ("cite ADR-001. We adopt Dapr pub/sub.\n```mermaid\ngraph LR\n"
                 "  subgraph Managers\n  OrderManager\n  BillingManager\n  end\n"
                 "  OrderManager --> BillingManager\n```\n")
    uexpect("Q6 conformance: solid Manager->Manager call is caught",
            any("synchronous Manager->Manager" in f for f in
                evaluate_conformance("ADR-001", _COND, sync_plan, sync_plan)))
    # an ASYNC (dashed) Manager->Manager edge is the conformant pub/sub path -> no sync finding
    async_plan = sync_plan.replace("OrderManager --> BillingManager", "OrderManager -.-> BillingManager")
    uexpect("Q6 conformance: dashed (async) Manager->Manager edge is not a sync violation",
            not any("synchronous Manager->Manager" in f for f in
                    evaluate_conformance("ADR-001", _COND, async_plan, async_plan)))
    # mechanism-presence: ADR cited, no Manager->Manager edge, but the plan never names pub/sub
    no_mech = "We cite ADR-001 and call PricingEngine.\nCall Chain: Client -> OrderManager -> PricingEngine\n"
    uexpect("Q6 conformance: plan that never names the mandated mechanism is caught",
            any("requires an async/transport mechanism" in f for f in
                evaluate_conformance("ADR-001", _COND, no_mech, no_mech)))
    # conformant plan: names Dapr pub/sub, no synchronous Manager->Manager -> conforms
    ok_plan = "We cite ADR-001 and route Manager events over Dapr pub/sub.\nCall Chain: Client -> OrderManager -> PricingEngine\n"
    uexpect("Q6 conformance: a conformant plan (names pub/sub, no sync MM) passes",
            not evaluate_conformance("ADR-001", _COND, ok_plan, ok_plan))
    # non-call-graph condition: citation is the bar (documented ceiling)
    uexpect("Q6 conformance: non-call-graph condition passes on citation alone",
            not evaluate_conformance("ADR-009", "Persistence uses the ledger schema.",
                                     "we cite ADR-009 here", ""))
    uexpect("Q6 conformance: an uncited binding ADR still fails",
            bool(evaluate_conformance("ADR-009", "", "nothing cited", "")))

    # load_catalog handles the real per-service-section format (not just a wide table)
    _SECTION_CATALOG = (
        "# Service Catalog\n## Catalog Entries\n"
        "### Managers\n#### `OrderManager`\n| Field | Value |\n|---|---|\n"
        "| Category | Manager |\n| Stressors absorbed | S-01, S-03 |\n\n"
        "### Engines\n#### `PricingEngine`\n| Field | Value |\n|---|---|\n"
        "| Category | Engine |\n| Stressors absorbed | S-02 |\n\n"
        "### ResourceAccess\n#### `LedgerAccess`\n| Field | Value |\n|---|---|\n"
        "| Category | Access |\n| Stressors absorbed | S-04 |\n")
    cat = load_catalog(_SECTION_CATALOG)
    uexpect("load_catalog parses the per-service-section format (the real handoff)",
            set(cat) == {"OrderManager", "PricingEngine", "LedgerAccess"} and "S-01" in cat["OrderManager"])
    uexpect("load_catalog does NOT read the 'ResourceAccess' category heading as a service",
            "ResourceAccess" not in cat)

    # exit-code contract
    with tempfile.TemporaryDirectory() as tmp:
        artifact, arch = _build(tmp, {})
        code_pass = OK if not any(r.ok is False for r in run_checks(artifact, arch)) else FINDINGS
        artifact, arch = _build(tmp, dict(_CASES[1][1]))
        code_fail = FINDINGS if any(r.ok is False for r in run_checks(artifact, arch)) else OK
    try:
        assert code_pass == OK, "clean run must yield exit 0"
        assert code_fail == FINDINGS, "run with findings must yield exit 1"
        print("  ok    exit-code contract (0 clean / 1 findings)")
        passed += 1
    except AssertionError as exc:
        print("  FAIL  exit-code contract: %s" % exc)
        failed += 1

    print()
    print("self-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


# --- cli -----------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_constitution.py",
        description="Deterministic subset (Q1-Q6, incl. Q3 call-chain layering) of the RDAG Constitution Check.")
    parser.add_argument("artifact", nargs="?",
                        help="the Developer artifact to check (plan.md / tasks.md / code as text)")
    parser.add_argument("arch_dir", nargs="?",
                        help="the landed, pinned release dir, e.g. architecture/arch-1.0.0/")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--self-test", action="store_true",
                        help="run the built-in fixtures and exit")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.artifact or not args.arch_dir:
        parser.error("artifact and arch_dir are required (or pass --self-test)")
    if not os.path.isfile(args.artifact):
        print("error: artifact not found: %s" % args.artifact, file=sys.stderr)
        return ERROR
    if not os.path.isdir(args.arch_dir):
        print("error: release dir not found: %s" % args.arch_dir, file=sys.stderr)
        return ERROR

    try:
        results = run_checks(args.artifact, args.arch_dir)
    except FormatError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return ERROR

    report(results, args.artifact, args.arch_dir, as_json=args.json)
    return FINDINGS if any(r.ok is False for r in results) else OK


if __name__ == "__main__":
    sys.exit(main())
