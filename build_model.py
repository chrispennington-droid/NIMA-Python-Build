"""
NIMA Phase II — first-pass build entrypoint.

Runs the full pipeline:
  Phase 1  config load + validation
  Phase 2  high-bay shell + stair-opening polygon
  Phase 3  walls, doors, windows/facade proxies, materials
  Phase 4  JSON scene + GLB/glTF export
  Phase 5  validation report

All outputs land in ./output/.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from nima_build.config import load_config
from nima_build.geometry import (
    INFERRED_F2_FLOOR_FT,
    build_highbay_shell,
    build_stair_opening,
)
from nima_build.gltf import export_glb
from nima_build.openings import build_openings
from nima_build.report import write_reports
from nima_build.scene import SceneBuild, write_scene_json
from nima_build.validation import validate_config


def run_build(package_root: Path, output_dir: Path, pass_label: str) -> SceneBuild:
    print(f"[Phase 1] Loading config from {package_root} ...")
    cfg = load_config(package_root)
    validation = validate_config(cfg)
    print(
        f"[Phase 1] locked_applied={len(validation.locked_applied)} "
        f"warnings={len(validation.warnings)} "
        f"errors={len(validation.errors)} "
        f"proxy_flags={len(validation.proxy_flags)}"
    )
    if validation.errors:
        for e in validation.errors:
            print(f"  ERROR: {e}")

    print("[Phase 2] Building high-bay shell + stair opening polygon ...")
    highbay = build_highbay_shell(cfg)
    stair = build_stair_opening(cfg, f2_floor_ft=INFERRED_F2_FLOOR_FT)
    print(
        f"[Phase 2] high-bay perim={highbay.perimeter_ft:.2f} ft, "
        f"footprint={highbay.footprint_sf:.0f} sf, "
        f"roof_top={highbay.roof_top_ft:.4f} ft; "
        f"stair area={stair.area_sf:.1f} sf"
    )

    print("[Phase 3] Placing doors, windows, facade proxies ...")
    openings = build_openings(cfg)
    rendered = sum(1 for p in openings.placed if p.metadata.get("render_emitted"))
    print(
        f"[Phase 3] placed={len(openings.placed)} "
        f"(rendered={rendered}, coordination_refs={len(openings.placed) - rendered}); "
        f"unplaced_pending_envelope={len(openings.unplaced)}"
    )

    inferred = [
        {
            "key": "f2_floor_ft",
            "value": INFERRED_F2_FLOOR_FT,
            "reason": (
                "Inferred from facade window sill data: F1 windows head ~14 ft, "
                "F2 lower windows sill = 14 ft, F2 project-room windows sill = 14 ft. "
                "Not explicitly locked in the package."
            ),
        },
        {
            "key": "non_highbay_envelope",
            "value": "not_built",
            "reason": (
                "Package gives wall_schedule parent rows but no endpoint coordinates "
                "for the new non-high-bay portion. First pass intentionally skips "
                "fabricating coordinates; needs vector extraction from SVG plans."
            ),
        },
        {
            "key": "roof_pitch",
            "value": "flat_cap",
            "reason": (
                "GEO-003 locks roof top elevation only. No pitch/parapet detail "
                "in the package; first pass uses a flat cap."
            ),
        },
        {
            "key": "openings_centerpoints",
            "value": "centered_on_parent_wall_or_evenly_spaced",
            "reason": (
                "STD-018: use centerpoints or visual evidence. Package does not "
                "give per-element centerpoints. First pass centers on parent wall, "
                "and evenly distributes the 3 covered-loading overhead doors."
            ),
        },
    ]

    scene = SceneBuild(
        config=cfg,
        highbay=highbay,
        stair=stair,
        openings=openings,
        validation=validation,
        inferred_assumptions=inferred,
        f2_floor_ft=INFERRED_F2_FLOOR_FT,
        pass_label=pass_label,
    )

    print("[Phase 4] Writing JSON scene + GLB ...")
    json_path = write_scene_json(scene, output_dir / "nima_scene.json")
    glb_path = export_glb(scene, output_dir / "nima_model.glb")
    print(f"[Phase 4] wrote {json_path} ({json_path.stat().st_size:,} bytes)")
    print(f"[Phase 4] wrote {glb_path} ({glb_path.stat().st_size:,} bytes)")

    print("[Phase 5] Writing validation report ...")
    rep_json, rep_md = write_reports(scene, output_dir)
    print(f"[Phase 5] wrote {rep_json}")
    print(f"[Phase 5] wrote {rep_md}")

    return scene


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NIMA Phase II first-pass build.")
    parser.add_argument(
        "--package-root",
        type=Path,
        default=Path("."),
        help="Path to the package root (default: cwd).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output"),
        help="Output directory (default: ./output).",
    )
    parser.add_argument(
        "--pass-label",
        type=str,
        default="minimal_first_pass",
        help="Label written into the scene JSON.",
    )
    args = parser.parse_args()

    run_build(args.package_root, args.output_dir, args.pass_label)


if __name__ == "__main__":
    main()
