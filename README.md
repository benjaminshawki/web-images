# Web Images Converter

A simple utility to convert images into web-optimized formats (PNG, JPEG, WebP, and SVG) and bundle them into a ZIP file.

## Features

- Converts images to multiple web-friendly formats
- Creates an SVG wrapper with a base64-encoded PNG
- Bundles all output files into a ZIP archive
- Preserves alpha channel when present
- Handles multiple images in a single command

## Project Structure

```
web-images/
├── images/       # Place source images here (ignored by git)
├── dist/         # Converted images go here
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

## Output

For each source image, the script creates:
- `.png` - Optimized PNG
- `.jpg` - Optimized JPEG (85% quality)
- `.webp` - WebP format (90% quality)
- `.svg` - SVG wrapper with embedded PNG
- `_web_images.zip` - ZIP archive containing all the above files