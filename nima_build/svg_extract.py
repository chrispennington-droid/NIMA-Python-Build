"""
SVG calibration + line-segment extraction for the NIMA F1/F2 schematics.

Parses the grid-label text on each SVG to derive a deterministic SVG-to-feet
transform, then exposes utilities to:
  * convert between SVG and feet coordinates
  * pull all <line> segments transformed into feet
  * find segments that lie close to a proposed wall (validation only)

The transforms are derived from the printed grid labels, which use 1 grid = 8 ft
per the package master config (STD-002).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

NS = "{http://www.w3.org/2000/svg}"
GRID_TO_FT = 8.0  # STD-002

_TRANSLATE_RE = re.compile(r"translate\(([-0-9.]+)[\s,]+([-0-9.]+)\)")


@dataclass
class GridCalibration:
    svg_x_at_grid_zero: float
    svg_y_at_grid_zero: float
    svg_per_grid_x: float
    svg_per_grid_y: float  # positive (SVG y increases down)

    @property
    def svg_per_ft_x(self) -> float:
        return self.svg_per_grid_x / GRID_TO_FT

    @property
    def svg_per_ft_y(self) -> float:
        return self.svg_per_grid_y / GRID_TO_FT

    def svg_to_ft(self, sx: float, sy: float) -> tuple[float, float]:
        fx = (sx - self.svg_x_at_grid_zero) / self.svg_per_ft_x
        fy = (self.svg_y_at_grid_zero - sy) / self.svg_per_ft_y
        return fx, fy

    def ft_to_svg(self, fx: float, fy: float) -> tuple[float, float]:
        sx = self.svg_x_at_grid_zero + fx * self.svg_per_ft_x
        sy = self.svg_y_at_grid_zero - fy * self.svg_per_ft_y
        return sx, sy

    def to_dict(self) -> dict:
        return {
            "svg_x_at_grid_zero": self.svg_x_at_grid_zero,
            "svg_y_at_grid_zero": self.svg_y_at_grid_zero,
            "svg_per_grid_x": self.svg_per_grid_x,
            "svg_per_grid_y": self.svg_per_grid_y,
            "svg_per_ft_x": self.svg_per_ft_x,
            "svg_per_ft_y": self.svg_per_ft_y,
            "grid_to_ft": GRID_TO_FT,
        }


@dataclass
class SVGSource:
    path: Path
    calibration: GridCalibration
    label_count: int
    line_count: int
    polygon_count: int
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "calibration": self.calibration.to_dict(),
            "label_count": self.label_count,
            "line_count": self.line_count,
            "polygon_count": self.polygon_count,
            "notes": list(self.notes),
        }


def _iter_text_elements(root) -> Iterable[tuple[float, float, str]]:
    for t in root.iter(f"{NS}text"):
        raw = "".join(t.itertext()).strip()
        if not raw:
            continue
        tr = t.get("transform") or ""
        m = _TRANSLATE_RE.search(tr)
        if not m:
            continue
        tx, ty = float(m.group(1)), float(m.group(2))
        yield tx, ty, raw


def _is_intish(raw: str) -> bool:
    if not raw:
        return False
    s = raw.lstrip("-")
    return s.isdigit() and len(raw) <= 3


def _calibrate(root) -> GridCalibration:
    """
    Scan text labels and derive the calibration from the labelled grid axes.
    Strategy:
      * Find a row of labels (similar SVG y) with strictly increasing tx whose
        text values are integer grid indices spanning a range of >= 8 grid
        units. That row gives the X-axis calibration.
      * Find a column of labels (similar SVG x) with strictly decreasing ty
        whose text values are integer grid indices spanning a range of >= 8.
        That column gives the Y-axis calibration.
    """
    labels = list(_iter_text_elements(root))

    # Bin by row (ty) and column (tx) and prefer the bands with the widest
    # range of integer values.
    rows: dict[int, list[tuple[float, str]]] = {}
    cols: dict[int, list[tuple[float, str]]] = {}
    for tx, ty, raw in labels:
        if _is_intish(raw):
            row_key = int(round(ty))
            col_key = int(round(tx))
            rows.setdefault(row_key, []).append((tx, raw))
            cols.setdefault(col_key, []).append((ty, raw))

    def _band(d: dict[int, list[tuple[float, str]]], width: int) -> dict[int, list[tuple[float, str]]]:
        # Cluster keys within +/- (width//2) and merge their lists.
        merged: dict[int, list[tuple[float, str]]] = {}
        keys_sorted = sorted(d.keys())
        used = set()
        for k in keys_sorted:
            if k in used:
                continue
            cluster = [k]
            for k2 in keys_sorted:
                if k2 != k and abs(k2 - k) <= width and k2 not in used:
                    cluster.append(k2)
            for k2 in cluster:
                used.add(k2)
            merged[cluster[0]] = sum((d[k2] for k2 in cluster), [])
        return merged

    rows_b = _band(rows, width=8)
    cols_b = _band(cols, width=8)

    def _best_axis(group: dict[int, list[tuple[float, str]]]) -> tuple[float, float, float]:
        """Return (axis_perp_value, val_per_pos_unit, perp_at_zero) for the
        row/col with the widest integer-label spread."""
        best = None
        for perp, items in group.items():
            uniq = []
            seen = set()
            for pos, raw in items:
                try:
                    val = int(raw)
                except ValueError:
                    continue
                if val in seen:
                    continue
                seen.add(val)
                uniq.append((pos, val))
            if len(uniq) < 4:
                continue
            uniq.sort(key=lambda r: r[0])
            vals = [v for _, v in uniq]
            spread = max(vals) - min(vals)
            if best is None or spread > best[0]:
                # Linear regression val = m*pos + b
                n = len(uniq)
                sum_x = sum(p for p, _ in uniq)
                sum_y = sum(v for _, v in uniq)
                sum_xx = sum(p * p for p, _ in uniq)
                sum_xy = sum(p * v for p, v in uniq)
                m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
                b = (sum_y - m * sum_x) / n
                best = (spread, m, b, perp)
        if best is None:
            raise RuntimeError("No grid label band found")
        _, m, b, perp = best
        return perp, m, b

    perp_y, m_x, b_x = _best_axis(rows_b)  # tx axis: val = m_x*tx + b_x
    perp_x, m_y, b_y = _best_axis(cols_b)  # ty axis: val = m_y*ty + b_y

    # Solve for SVG positions where grid val = 0
    sx_at_zero_grid = -b_x / m_x  # m_x * sx + b_x = 0
    sy_at_zero_grid = -b_y / m_y

    # SVG units per grid (1 grid step in val along each axis)
    svg_per_grid_x = 1.0 / m_x  # val per svg = m_x; svg per val = 1/m_x
    svg_per_grid_y = 1.0 / m_y
    # Y is upside-down (val decreases as ty increases). Take absolute and rely on direction in transform.
    return GridCalibration(
        svg_x_at_grid_zero=sx_at_zero_grid,
        svg_y_at_grid_zero=sy_at_zero_grid,
        svg_per_grid_x=abs(svg_per_grid_x),
        svg_per_grid_y=abs(svg_per_grid_y),
    )


def load_svg_source(path: Path) -> SVGSource:
    path = Path(path)
    tree = ET.parse(path)
    root = tree.getroot()
    cal = _calibrate(root)
    n_lines = sum(1 for _ in root.iter(f"{NS}line"))
    n_polys = sum(1 for _ in root.iter(f"{NS}polygon"))
    n_labels = sum(1 for _ in _iter_text_elements(root))

    # Cross-check known high-bay corners (for note only).
    notes = []
    expected_corners = [("HB-V1", 91.0, 126.0), ("HB-V2", 151.0, 116.0),
                        ("HB-V3", 120.0, -56.0), ("HB-V4", 60.0, -46.0)]
    for vid, fx, fy in expected_corners:
        sx, sy = cal.ft_to_svg(fx, fy)
        notes.append(f"{vid} ({fx:.1f},{fy:.1f}) ft -> SVG ({sx:.1f},{sy:.1f})")
    return SVGSource(
        path=path,
        calibration=cal,
        label_count=n_labels,
        line_count=n_lines,
        polygon_count=n_polys,
        notes=notes,
    )


def iter_lines_in_ft(svg_path: Path) -> Iterable[tuple[tuple[float, float], tuple[float, float]]]:
    """Yield ((fx1, fy1), (fx2, fy2)) for every <line> element."""
    src = load_svg_source(svg_path)
    cal = src.calibration
    tree = ET.parse(svg_path)
    root = tree.getroot()
    for ln in root.iter(f"{NS}line"):
        try:
            x1, y1 = float(ln.get("x1")), float(ln.get("y1"))
            x2, y2 = float(ln.get("x2")), float(ln.get("y2"))
        except (TypeError, ValueError):
            continue
        yield cal.svg_to_ft(x1, y1), cal.svg_to_ft(x2, y2)
