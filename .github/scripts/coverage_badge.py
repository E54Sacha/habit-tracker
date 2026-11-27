"""Writes a shields-style SVG badge from coverage.json (made by `coverage json`). No dependencies.

Usage: python coverage_badge.py coverage.json badge.svg
"""

import json
import sys

total = json.load(open(sys.argv[1]))["totals"]["percent_covered"]
label, value = "coverage", f"{total:.0f}%"
color = "#2f9e44" if total >= 90 else "#74b816" if total >= 80 else "#f59f00" if total >= 60 else "#e03131"
lw, vw = 63, 9 * len(value) + 10  # approximate text widths (Verdana 11px)
w = lw + vw
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}: {value}">
<title>{label}: {value}</title>
<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<clipPath id="r"><rect width="{w}" height="20" rx="3" fill="#fff"/></clipPath>
<g clip-path="url(#r)"><rect width="{lw}" height="20" fill="#555"/><rect x="{lw}" width="{vw}" height="20" fill="{color}"/><rect width="{w}" height="20" fill="url(#s)"/></g>
<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
<text x="{lw / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text><text x="{lw / 2}" y="14">{label}</text>
<text x="{lw + vw / 2}" y="15" fill="#010101" fill-opacity=".3">{value}</text><text x="{lw + vw / 2}" y="14">{value}</text>
</g></svg>
"""
open(sys.argv[2], "w").write(svg)
print(f"{label}: {value}")
