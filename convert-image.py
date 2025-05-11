#!/usr/bin/env python3
"""
convert-image.py  –  Export a single source image to PNG, JPEG, WEBP and an
SVG wrapper, then bundle everything into a ZIP.

Usage
-----
    python3 convert-image.py path/to/source.jpg
    python3 convert-image.py path/to/source.png --out-dir ./dist
    python3 convert-image.py src/*.jpg --out-dir ./dist

Dependencies
------------
    pip install pillow

Project Structure
----------------
    src/     - Place source images here
    dist/    - Converted images are saved here by default
"""

from __future__ import annotations
import argparse
import base64
import os
import sys
import zipfile
from pathlib import Path

from PIL import Image


def export_images(src: Path, out_dir: Path) -> list[Path]:
    """Convert *src* into multiple web-ready formats, return the output paths."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Pillow converts everything internally to RGB; keep alpha if present
    img = Image.open(src)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

    stem = src.stem  # filename without extension

    png_path  = out_dir / f"{stem}.png"
    jpg_path  = out_dir / f"{stem}.jpg"
    webp_path = out_dir / f"{stem}.webp"
    svg_path  = out_dir / f"{stem}.svg"
    zip_path  = out_dir / f"{stem}_web_images.zip"

    # --- PNG --------------------------------------------------------------
    img.save(png_path, format="PNG", optimize=True)

    # --- JPEG -------------------------------------------------------------
    img_no_alpha = img.convert("RGB")  # JPEG can’t handle alpha
    img_no_alpha.save(jpg_path, format="JPEG", quality=85, optimize=True)

    # --- WEBP -------------------------------------------------------------
    try:
        img.save(webp_path, format="WEBP", quality=90, method=6)
    except ValueError:
        # Older Pillow builds may lack WebP support
        print("[warn] Pillow was built without WebP; skipping image.webp", file=sys.stderr)
        webp_path = None

    # --- SVG --------------------------------------------------------------
    with open(png_path, "rb") as fp:
        b64_png = base64.b64encode(fp.read()).decode("ascii")

    w, h = img.size
    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w}" height="{h}">\n'
        f'  <image href="data:image/png;base64,{b64_png}" '
        f'width="{w}" height="{h}" />\n'
        f'</svg>\n'
    )
    svg_path.write_text(svg_content, encoding="utf-8")

    # --- ZIP bundle -------------------------------------------------------
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(png_path,  arcname=png_path.name)
        zf.write(jpg_path,  arcname=jpg_path.name)
        if webp_path:
            zf.write(webp_path, arcname=webp_path.name)
        zf.writestr(svg_path.name, svg_content)  # write from memory

    return [p for p in (png_path, jpg_path, webp_path, svg_path, zip_path) if p]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a PNG/JPG into multiple web-optimized formats."
    )
    parser.add_argument(
        "source",
        type=str,
        nargs='+',
        help="Path(s) to the source image(s) (PNG, JPG, etc.)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist"),
        help="Directory to place the converted files (defaults to 'dist/')",
    )

    args = parser.parse_args()
    out_dir = args.out_dir.expanduser().resolve()

    # Handle shell glob expansion or single file
    all_outputs = []
    for src_path in args.source:
        src = Path(src_path).expanduser().resolve()
        if not src.is_file():
            parser.error(f"Source file not found: {src}")

        print(f"Converting: {src}")
        outputs = export_images(src, out_dir)
        all_outputs.extend(outputs)

    print("\n✓ Export complete:")
    for p in all_outputs:
        print("  ", p.relative_to(Path.cwd()))


if __name__ == "__main__":
    main()
