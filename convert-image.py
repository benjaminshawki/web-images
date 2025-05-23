#!/usr/bin/env python3
"""
convert-image.py  –  Export a single source image to PNG, JPEG, WEBP and an
SVG wrapper, then bundle everything into a ZIP. Also generates website assets
like favicons and optimized images for web use.

Usage
-----
    python3 convert-image.py path/to/source.jpg
    python3 convert-image.py path/to/source.png --out-dir ./dist
    python3 convert-image.py images/*.jpg --out-dir ./dist
    python3 convert-image.py path/to/logo.png --favicon --out-dir ./public

Dependencies
------------
    pip install pillow

Project Structure
----------------
    images/  - Place source images here (ignored by git)
    dist/    - Converted images are saved here by default
    public/  - Website assets including favicons and optimized images
"""

from __future__ import annotations
import argparse
import base64
import datetime
import os
import sys
import zipfile
from pathlib import Path

from PIL import Image

# Try to import AVIF plugin
try:
    import pillow_avif
    AVIF_SUPPORTED = True
except ImportError:
    AVIF_SUPPORTED = False


def export_images(src: Path, out_dir: Path, favicon: bool = False, website: bool = False) -> list[Path]:
    """Convert *src* into multiple web-ready formats, return the output paths.

    Args:
        src: Source image path
        out_dir: Output directory path
        favicon: If True, generate favicon variants
        website: If True, optimize for website usage
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # Pillow converts everything internally to RGB; keep alpha if present
    img = Image.open(src)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

    stem = src.stem  # filename without extension

    png_path  = out_dir / f"{stem}.png"
    jpg_path  = out_dir / f"{stem}.jpg"
    webp_path = out_dir / f"{stem}.webp"
    avif_path = out_dir / f"{stem}.avif" if website else None
    svg_path  = out_dir / f"{stem}.svg"
    zip_path  = out_dir / f"{stem}_web_images.zip"

    # For favicons
    ico_path = out_dir / "favicon.ico" if favicon else None
    favicon_paths = []

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

    # --- AVIF (for website) ------------------------------------------------
    if website and avif_path:
        if AVIF_SUPPORTED:
            try:
                img.save(avif_path, format="AVIF", quality=85)
            except (ValueError, AttributeError, KeyError) as e:
                print(f"[error] AVIF save failed: {e}; skipping image.avif", file=sys.stderr)
                avif_path = None
        else:
            print("[warn] AVIF format not supported (pillow_avif not installed); skipping image.avif", file=sys.stderr)
            avif_path = None

    # --- Favicon generation ------------------------------------------------
    if favicon:
        # Standard favicon.ico (16x16, 32x32, 48x48)
        favicon_sizes = [(16, 16), (32, 32), (48, 48)]
        favicon_images = [img.resize(size, Image.Resampling.LANCZOS) for size in favicon_sizes]

        # Save as ICO file
        favicon_images[0].save(
            ico_path,
            format="ICO",
            sizes=[(16, 16), (32, 32), (48, 48)],
            append_images=favicon_images[1:]
        )

        # Create apple-touch-icon (180x180)
        apple_icon_path = out_dir / "apple-touch-icon.png"
        apple_icon = img.resize((180, 180), Image.Resampling.LANCZOS)
        apple_icon.save(apple_icon_path, format="PNG", optimize=True)

        # Create various sized png favicons for different devices
        favicon_png_sizes = [(192, 192), (512, 512)]
        android_icons = []

        for size in favicon_png_sizes:
            size_str = f"{size[0]}x{size[1]}"
            favicon_png_path = out_dir / f"favicon-{size_str}.png"
            favicon_img = img.resize(size, Image.Resampling.LANCZOS)
            favicon_img.save(favicon_png_path, format="PNG", optimize=True)
            android_icons.append(favicon_png_path)

        favicon_paths = [ico_path, apple_icon_path] + android_icons

    # --- ZIP bundle -------------------------------------------------------
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add a top-level directory in the ZIP with stem name
        zip_dir = stem

        # Create a "standard" subdirectory for basic formats
        zf.write(png_path, arcname=f"{zip_dir}/standard/{png_path.name}")
        zf.write(jpg_path, arcname=f"{zip_dir}/standard/{jpg_path.name}")
        zf.writestr(f"{zip_dir}/standard/{svg_path.name}", svg_content)  # write from memory

        # Create a "web" subdirectory for web formats
        if webp_path:
            zf.write(webp_path, arcname=f"{zip_dir}/web/{webp_path.name}")
        if avif_path:
            zf.write(avif_path, arcname=f"{zip_dir}/web/{avif_path.name}")

        # Add favicon files to a "favicon" subdirectory if generated
        if favicon_paths:
            for fav_path in favicon_paths:
                if fav_path and fav_path.exists():
                    zf.write(fav_path, arcname=f"{zip_dir}/favicon/{fav_path.name}")

        # Add a README.txt with info about the conversions
        readme_content = f"""Web Images Export for {stem}

Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Contents:
- standard/ - Basic image formats (PNG, JPEG, SVG)
- web/ - Web-optimized formats (WebP, AVIF)
- favicon/ - Favicon variants (if requested)

Original file: {src.name}
"""
        zf.writestr(f"{zip_dir}/README.txt", readme_content)

    all_paths = [p for p in (png_path, jpg_path, webp_path, avif_path, svg_path, zip_path) if p]
    all_paths.extend([p for p in favicon_paths if p])

    return all_paths


def create_timestamped_directory(base_dir: Path) -> Path:
    """Create a timestamped directory for this conversion run."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    timestamped_dir = base_dir / timestamp
    timestamped_dir.mkdir(parents=True, exist_ok=True)
    return timestamped_dir


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
    parser.add_argument(
        "--favicon",
        action="store_true",
        help="Generate favicon variants (ico, png in various sizes)",
    )
    parser.add_argument(
        "--website",
        action="store_true",
        help="Optimize for website usage (attempts AVIF if supported)",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Output to public/ directory instead of dist/ (for website assets)",
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Disable timestamp subdirectory creation",
    )

    args = parser.parse_args()

    # Determine base output directory
    if args.public:
        base_dir = Path("public")
    else:
        base_dir = args.out_dir

    base_dir = base_dir.expanduser().resolve()

    # Create timestamped directory unless --no-timestamp is specified
    if args.no_timestamp:
        out_dir = base_dir
    else:
        out_dir = create_timestamped_directory(base_dir)
        print(f"Creating output directory: {out_dir}")

    # Create website-specific subdirectory if using website mode
    if args.website and not args.no_timestamp:
        # For website optimized images, create a web/ subdirectory
        web_dir = out_dir / "web"
        web_dir.mkdir(exist_ok=True)
        out_dir = web_dir

    # Handle shell glob expansion or single file
    all_outputs = []
    for src_path in args.source:
        src = Path(src_path).expanduser().resolve()
        if not src.is_file():
            parser.error(f"Source file not found: {src}")

        print(f"Converting: {src}")
        outputs = export_images(src, out_dir, favicon=args.favicon, website=args.website)
        all_outputs.extend(outputs)

    print("\n✓ Export complete:")
    for p in all_outputs:
        print("  ", p.relative_to(Path.cwd()))


if __name__ == "__main__":
    main()
