# Web Images Converter

A simple utility to convert images into web-optimized formats (PNG, JPEG, WebP, AVIF, and SVG) and bundle them into a ZIP file. Also generates website assets like favicons.

## Features

- Converts images to multiple web-friendly formats
- Creates an SVG wrapper with a base64-encoded PNG
- Bundles all output files into a ZIP archive
- Preserves alpha channel when present
- Handles multiple images in a single command
- Generates favicon variants (ICO, PNG) in various sizes
- Creates website-optimized images including AVIF format
- Supports output to a `/public` directory for websites

## Project Structure

```
web-images/
├── images/       # Place source images here (ignored by git)
├── dist/         # Converted images go here by default
├── public/       # Website assets including favicons
├── convert-image.py  # Main script
└── README.md
```

## Requirements

- Python 3.6+
- Pillow (PIL Fork)

```bash
pip install pillow
```

## Usage

### Single image:

```bash
python3 convert-image.py images/image.jpg
```

### Multiple images:

```bash
python3 convert-image.py images/*.jpg
```

### Custom output directory:

```bash
python3 convert-image.py images/image.png --out-dir ./custom-output
```

### Generate favicon variants:

```bash
python3 convert-image.py images/logo.png --favicon --public
```

### Optimize for website usage:

```bash
python3 convert-image.py images/header.jpg --website --public
```

## Output

For each source image, the script creates:

### Standard formats:
- `.png` - Optimized PNG
- `.jpg` - Optimized JPEG (85% quality)
- `.webp` - WebP format (90% quality)
- `.svg` - SVG wrapper with embedded PNG
- `_web_images.zip` - ZIP archive containing all generated files

### Website optimized formats (with `--website`):
- `.avif` - AVIF format (85% quality)

### Favicon variants (with `--favicon`):
- `favicon.ico` - Standard favicon (16x16, 32x32, 48x48)
- `apple-touch-icon.png` - Apple touch icon (180x180)
- `favicon-192x192.png` - Android/Chrome icon
- `favicon-512x512.png` - Android/Chrome icon