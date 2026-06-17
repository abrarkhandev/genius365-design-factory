#!/usr/bin/env python3
"""Deterministic anti-slop scanner for the Hermes Design Factory QA gate.

This is the shared, client-agnostic core of the "gate of record". It performs a
purely regex/string based scan of rendered HTML/CSS against a client's local
source-truth text and returns structured findings. There is intentionally no
network access, no model call and no heuristic scoring: the same input always
produces the same findings so the gate is reproducible.

The scanner detects the 7 deterministic "sins":

1. Default AI indigo/purple palette (an exact hex blocklist).
2. Generic two-stop purple/blue/cyan hero gradients.
3. Emoji / symbol-only feature icons in visible content.
4. Rounded cards with a thick coloured left-border accent.
5. Filler / lorem / placeholder copy.
6. Placeholder image CDNs (placehold.co, picsum.photos, ...).
7. Unverified proof / metric / certification claims that are not present in the
   local source-truth text (ISO 27001, "\\d+x", "\\d+%", "$...ARR", client counts).

Severities follow the original pilot script: every sin above is ``P0`` except
placeholder asset CDNs which are ``P1``. A finding is a plain ``dict`` so it
serialises straight to JSON for ``export-results.json``.

Public API
----------
``scan_text(html_text, source_truth_text, *, surface="surface") -> list[Finding]``
    Scan a single in-memory HTML/CSS string. This is the primitive the export
    scripts call on the *rendered* DOM.

``scan_surfaces(surfaces, source_truth_text) -> AntiSlopReport``
    Scan a mapping of ``{surface_name: html_text}`` and roll the findings up
    into a report dict (``ok``, ``p0_count``, ``p1_count``, ``findings``)
    matching the structure the original script wrote.

``load_source_truth_text(paths) -> tuple[str, list[str]]``
    Read and normalise the source-truth corpus from one or more files/dirs.

``render_markdown_report(report, *, title, source_truth_files) -> str``
    Render the human-readable ``anti-slop-report.md`` body.

``CHECKS`` / ``CHECK_DESCRIPTIONS``
    Machine- and human-readable catalogue of every check, so callers (and tests)
    can introspect the gate without re-deriving it.
"""
from __future__ import annotations

import html as html_lib
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

# A finding is intentionally a plain dict so it round-trips through JSON unchanged.
Finding = Dict[str, Any]

# ---------------------------------------------------------------------------
# Blocklists and patterns (ported verbatim from export_inspra_ai_pilot.py).
# ---------------------------------------------------------------------------

#: Exact default "AI" indigo/purple hexes. Kept verbatim and case-insensitive;
#: a hex is only flagged when it does NOT also appear in the source-truth text
#: (i.e. it was not an explicitly brand-approved colour).
DEFAULT_PURPLE_HEX = {
    "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#8b5cf6", "#7c3aed",
    "#6d28d9", "#a855f7", "#9333ea", "#c084fc", "#818cf8",
}

#: Terms that mark the "purple" stop of a generic gradient.
GRADIENT_PURPLE_TERMS = (
    "purple", "indigo", "violet", "magenta", "pink",
    "#6366f1", "#4f46e5", "#8b5cf6", "#7c3aed", "#6d28d9", "#a855f7",
)
#: Terms that mark the "blue/cyan" stop of a generic gradient.
GRADIENT_BLUE_TERMS = (
    "blue", "cyan", "sky", "teal",
    "#2563eb", "#3b82f6", "#0ea5e9", "#06b6d4", "#22d3ee",
)

EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF]")
SYMBOL_ICON_RE = re.compile(r'class=["\']icon["\'][^>]*>\s*([^<]{1,4})\s*<', re.I)
FILLER_RE = re.compile(
    r"\b(lorem ipsum|feature one|feature two|coming soon|replace this|"
    r"insert logo|todo:|tbd|placeholder copy)\b",
    re.I,
)
PLACEHOLDER_ASSET_RE = re.compile(
    r"(placehold\.co|placeholder\.com|picsum\.photos|dummyimage\.com|"
    r"placekitten\.com|loremflickr\.com|via\.placeholder)",
    re.I,
)

#: Proof / metric / certification claims. Each match is verified against the
#: source-truth corpus and only flagged when the exact phrase is absent.
PROOF_PATTERNS = [
    re.compile(r"\bISO\s*27001\s*certified\b", re.I),
    re.compile(r"\bISO\s*27001\s*certification\b", re.I),
    re.compile(r"\b\d[\d,.]*\s*\+\s*(?:SME\s*)?(?:clients|customers|businesses)\b", re.I),
    re.compile(r"\b\d+(?:\.\d+)?\s*x\s*(?:faster|more|better|ROI|return|growth)?\b", re.I),
    re.compile(
        r"\b\d+(?:\.\d+)?\s*%\s*(?:faster|less|more|increase|decrease|uplift|ROI|"
        r"saved|reduction|success|accuracy|conversion|response)\b",
        re.I,
    ),
    re.compile(r"\b\$?\d[\d,.]*\s*(?:ARR|revenue|ROI)\b", re.I),
]

#: Equivalent phrasings treated as source-truth backing for one another.
_PROOF_VARIANTS: Dict[str, List[str]] = {
    "iso 27001 certified": ["iso 27001 certification", "iso 27001 certified"],
    "iso 27001 certification": ["iso 27001 certification", "iso 27001 certified"],
}

#: Machine-readable catalogue of every check id and its severity.
CHECKS: Dict[str, str] = {
    "default_indigo_purple_palette": "P0",
    "generic_purple_blue_gradient": "P0",
    "emoji_feature_icons": "P0",
    "symbol_only_feature_icon": "P0",
    "rounded_cards_coloured_left_border": "P0",
    "filler_or_placeholder_copy": "P0",
    "unverified_metric_or_proof_claim": "P0",
    "placeholder_asset_service": "P1",
    "missing_surface_for_scan": "P0",
}

#: Human-readable one-liners, surfaced in the markdown report's "Checks
#: implemented" section.
CHECK_DESCRIPTIONS: List[str] = [
    "Default indigo/purple palette detection (exact hex blocklist).",
    "Generic purple/blue/cyan two-stop gradient detection.",
    "Emoji feature icon detection in visible content.",
    "Symbol-only feature icon detection (icon class with a non-alphanumeric glyph).",
    "Rounded card plus thick coloured left-border cliche detection.",
    "Filler / lorem / placeholder copy detection.",
    "Placeholder asset CDN detection (placehold.co, picsum.photos, ...).",
    "Unverified metrics/certification/proof claims checked against local source-truth.",
]


# ---------------------------------------------------------------------------
# Text helpers.
# ---------------------------------------------------------------------------

def normalise_text(value: str) -> str:
    """Collapse whitespace and lowercase for stable substring comparisons."""
    return re.sub(r"\s+", " ", value).strip().lower()


def strip_html(raw: str) -> str:
    """Return the normalised visible text of an HTML fragment.

    Scripts, styles, SVG, and comments are removed before tags are stripped so
    that copy-level checks only look at content a reader would actually see.
    """
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<svg[^>]*>.*?</svg>", " ", raw)
    raw = re.sub(r"(?is)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return normalise_text(html_lib.unescape(raw))


def phrase_allowed_by_source(phrase: str, source_text: str) -> bool:
    """True when a proof phrase is backed by the source-truth corpus.

    A trailing period is ignored and a small set of equivalent phrasings (e.g.
    "ISO 27001 certified" vs "ISO 27001 certification") count as backing.
    """
    phrase_n = normalise_text(phrase).rstrip(".")
    if not phrase_n:
        return True
    if phrase_n in source_text:
        return True
    return any(v in source_text for v in _PROOF_VARIANTS.get(phrase_n, []))


def _add_finding(
    findings: List[Finding],
    *,
    severity: str,
    check: str,
    surface: str,
    line: int | None,
    evidence: str,
    fix: str,
) -> None:
    """Append a normalised finding (evidence collapsed and truncated to 260 chars)."""
    findings.append(
        {
            "severity": severity,
            "check": check,
            "surface": surface,
            "line": line,
            "evidence": re.sub(r"\s+", " ", evidence).strip()[:260],
            "fix": fix,
        }
    )


# ---------------------------------------------------------------------------
# Source-truth loading.
# ---------------------------------------------------------------------------

def load_source_truth_text(
    paths: str | Path | List[str | Path],
) -> Tuple[str, List[str]]:
    """Read and normalise the source-truth corpus.

    ``paths`` may be a single file, a single directory, or a list mixing both.
    Directories are walked recursively for ``.md``/``.txt``/``.json`` files
    (matching the original pilot behaviour). Returns ``(normalised_text,
    relative_or_absolute_file_labels)``.

    The returned text is whitespace-normalised and lowercased so the proof and
    palette checks can do plain substring containment against it.
    """
    if isinstance(paths, (str, Path)):
        path_list: List[Path] = [Path(paths)]
    else:
        path_list = [Path(p) for p in paths]

    chunks: List[str] = []
    labels: List[str] = []
    seen: set[Path] = set()

    def _ingest(file_path: Path, label_root: Path | None) -> None:
        if file_path in seen or not file_path.is_file():
            return
        if file_path.suffix.lower() not in {".md", ".txt", ".json"}:
            return
        seen.add(file_path)
        text = file_path.read_text(errors="replace")
        try:
            label = str(file_path.relative_to(label_root)) if label_root else str(file_path)
        except ValueError:
            label = str(file_path)
        chunks.append(f"\n# SOURCE: {label}\n{text}")
        labels.append(label)

    for path in path_list:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                _ingest(child, path.parent)
        else:
            _ingest(path, path.parent)

    return normalise_text("\n".join(chunks)), labels


# ---------------------------------------------------------------------------
# The scanner.
# ---------------------------------------------------------------------------

def scan_text(
    html_text: str,
    source_truth_text: str,
    *,
    surface: str = "surface",
) -> List[Finding]:
    """Run every deterministic anti-slop check against one HTML/CSS string.

    Parameters
    ----------
    html_text:
        The HTML/CSS to scan. The export scripts pass the *rendered* DOM
        (``page.content()``) so any client-side templating is already resolved.
    source_truth_text:
        Normalised source-truth corpus from :func:`load_source_truth_text`. Used
        to whitelist brand-approved hexes and verify proof/metric claims.
    surface:
        Label recorded on each finding (e.g. ``"landing"`` / ``"bip"``).

    Returns
    -------
    list[Finding]
        Zero or more findings. Order mirrors the original script: palette,
        gradient, emoji, symbol icon, rounded-card, filler, proof, placeholder.
    """
    raw = html_text
    raw_lower = raw.lower()
    lines = raw.splitlines()
    findings: List[Finding] = []

    # 1. P0: default AI purple/indigo palette unless explicitly brand-approved.
    for hex_value in sorted(DEFAULT_PURPLE_HEX):
        if hex_value not in raw_lower:
            continue
        if hex_value in source_truth_text:
            continue
        for idx, line in enumerate(lines, 1):
            if hex_value in line.lower():
                _add_finding(
                    findings,
                    severity="P0",
                    check="default_indigo_purple_palette",
                    surface=surface,
                    line=idx,
                    evidence=line,
                    fix="Replace default AI purple/indigo with verified brand tokens from DESIGN.md.",
                )

    # 2. P0: generic purple/blue/cyan gradients (two-stop).
    for idx, line in enumerate(lines, 1):
        lower = line.lower()
        if "gradient" not in lower:
            continue
        has_purple = any(term in lower for term in GRADIENT_PURPLE_TERMS)
        has_blue = any(term in lower for term in GRADIENT_BLUE_TERMS)
        if has_purple and has_blue:
            _add_finding(
                findings,
                severity="P0",
                check="generic_purple_blue_gradient",
                surface=surface,
                line=idx,
                evidence=line,
                fix="Recompose the gradient using verified brand colours or remove the generic AI gradient.",
            )

    # 3. P0: emoji feature icons in visible content.
    for idx, line in enumerate(lines, 1):
        visible = strip_html(line)
        if visible and EMOJI_RE.search(visible):
            _add_finding(
                findings,
                severity="P0",
                check="emoji_feature_icons",
                surface=surface,
                line=idx,
                evidence=visible,
                fix="Replace emoji icons with a consistent SVG/icon-library style.",
            )

    # 3b. P0: symbol-only feature icons (icon class wrapping a non-alphanumeric glyph).
    for match in SYMBOL_ICON_RE.finditer(raw):
        token = match.group(1).strip()
        if token and not re.fullmatch(r"[A-Za-z0-9]{1,4}", token):
            line_no = raw[: match.start()].count("\n") + 1
            _add_finding(
                findings,
                severity="P0",
                check="symbol_only_feature_icon",
                surface=surface,
                line=line_no,
                evidence=token,
                fix="Replace symbol/emoji-style feature icons with SVG icons or short text glyphs from the approved icon system.",
            )

    # 4. P0: rounded cards with thick coloured left-border accents.
    for match in re.finditer(r"(?s)([^{}]+)\{([^{}]+)\}", raw):
        selector = normalise_text(match.group(1))
        body = match.group(2)
        body_lower = body.lower()
        if "border-left" not in body_lower or "border-radius" not in body_lower:
            continue
        if not re.search(r"border-left\s*:\s*(?:[2-9]|\d{2,})px", body_lower):
            continue
        if not (
            re.search(r"#[0-9a-f]{3,8}", body_lower)
            or "var(--accent" in body_lower
            or "currentcolor" in body_lower
        ):
            continue
        line_no = raw[: match.start()].count("\n") + 1
        _add_finding(
            findings,
            severity="P0",
            check="rounded_cards_coloured_left_border",
            surface=surface,
            line=line_no,
            evidence=f"{selector} {{ {body[:180]} }}",
            fix="Use a less cliched card treatment: subtle border, tonal fill, icon rail, grid line, or brand-specific motif.",
        )

    # 5. P0: visible filler / placeholder copy.
    if FILLER_RE.search(strip_html(raw)):
        for idx, line in enumerate(lines, 1):
            visible = strip_html(line)
            if FILLER_RE.search(visible):
                _add_finding(
                    findings,
                    severity="P0",
                    check="filler_or_placeholder_copy",
                    surface=surface,
                    line=idx,
                    evidence=visible,
                    fix="Replace filler with source-truth-backed client copy.",
                )

    # 6. P0: invented proof/metric/certification claims absent from source truth.
    for idx, line in enumerate(lines, 1):
        visible = strip_html(line)
        if not visible:
            continue
        for pattern in PROOF_PATTERNS:
            for match in pattern.finditer(visible):
                phrase = match.group(0)
                if phrase_allowed_by_source(phrase, source_truth_text):
                    continue
                _add_finding(
                    findings,
                    severity="P0",
                    check="unverified_metric_or_proof_claim",
                    surface=surface,
                    line=idx,
                    evidence=phrase,
                    fix="Remove the claim or add exact source-truth proof before client delivery.",
                )

    # 7. P1: placeholder/stock asset services in deliverables.
    for idx, line in enumerate(lines, 1):
        if PLACEHOLDER_ASSET_RE.search(line):
            _add_finding(
                findings,
                severity="P1",
                check="placeholder_asset_service",
                surface=surface,
                line=idx,
                evidence=line,
                fix="Replace placeholder asset URLs with approved owned/licensed assets.",
            )

    return findings


def scan_surfaces(
    surfaces: Dict[str, str],
    source_truth_text: str,
) -> Dict[str, Any]:
    """Scan a mapping of ``{surface_name: html_text}`` and roll up a report.

    Returns a dict shaped like the original pilot's report::

        {"ok": bool, "p0_count": int, "p1_count": int, "findings": [...]}

    ``ok`` is True only when there are zero ``P0`` findings. ``P1`` findings are
    reported but do not fail the gate (matching the original).
    """
    findings: List[Finding] = []
    for surface_name, text in surfaces.items():
        findings.extend(scan_text(text, source_truth_text, surface=surface_name))

    p0_count = sum(1 for f in findings if f["severity"] == "P0")
    p1_count = sum(1 for f in findings if f["severity"] == "P1")
    return {
        "ok": p0_count == 0,
        "p0_count": p0_count,
        "p1_count": p1_count,
        "findings": findings,
    }


def missing_surface_finding(surface: str, expected_path: str | Path) -> Finding:
    """Build the P0 finding used when a deliverable surface is absent."""
    return {
        "severity": "P0",
        "check": "missing_surface_for_scan",
        "surface": surface,
        "line": None,
        "evidence": str(expected_path),
        "fix": "Create the expected deliverable before QA.",
    }


# ---------------------------------------------------------------------------
# Markdown report rendering.
# ---------------------------------------------------------------------------

def render_markdown_report(
    report: Dict[str, Any],
    *,
    title: str,
    source_truth_files: List[str],
) -> str:
    """Render the human-readable ``anti-slop-report.md`` body.

    Mirrors the original layout: verdict, P0/P1 counts, source-truth file list,
    a findings table, and the catalogue of checks implemented.
    """
    lines = [
        f"# Deterministic Anti-Slop QA - {title}",
        "",
        f"Overall verdict: **{'PASS' if report['ok'] else 'REWORK'}**",
        "",
        f"- P0 findings: {report['p0_count']}",
        f"- P1 findings: {report['p1_count']}",
        "",
        "## Source-truth files checked",
        "",
    ]
    for file in source_truth_files:
        lines.append(f"- `{file}`")
    if not source_truth_files:
        lines.append("- (none found)")

    lines.extend(["", "## Findings", ""])
    if not report["findings"]:
        lines.append("No deterministic anti-slop findings.")
    else:
        lines.append("| Severity | Check | Surface | Line | Evidence | Fix |")
        lines.append("|---|---|---|---:|---|---|")
        for f in report["findings"]:
            evidence = str(f["evidence"]).replace("|", "\\|")
            fix = str(f["fix"]).replace("|", "\\|")
            line = "" if f["line"] is None else str(f["line"])
            lines.append(
                f"| {f['severity']} | `{f['check']}` | `{f['surface']}` | {line} | {evidence} | {fix} |"
            )

    lines.extend(["", "## Checks implemented", ""])
    lines.extend(f"- {desc}" for desc in CHECK_DESCRIPTIONS)
    lines.append("")
    return "\n".join(lines) + "\n"


__all__ = [
    "Finding",
    "DEFAULT_PURPLE_HEX",
    "GRADIENT_PURPLE_TERMS",
    "GRADIENT_BLUE_TERMS",
    "PROOF_PATTERNS",
    "PLACEHOLDER_ASSET_RE",
    "CHECKS",
    "CHECK_DESCRIPTIONS",
    "normalise_text",
    "strip_html",
    "phrase_allowed_by_source",
    "load_source_truth_text",
    "scan_text",
    "scan_surfaces",
    "missing_surface_finding",
    "render_markdown_report",
]
