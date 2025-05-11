# Web Images Converter

A simple utility to convert images into web-optimized formats (PNG, JPEG, WebP, AVIF, and SVG) and bundle them into a ZIP file. Also generates website assets like favicons.

## Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Place your images in the 'images' folder

# 3. Convert your images (basic usage)
python3 convert-image.py images/*.jpg
```

All converted files will be available in the `dist/` directory.

## Common Use Cases

| Task | Command |
|------|---------|
| Convert to all formats | `python3 convert-image.py images/logo.png` |
| Generate website assets | `python3 convert-image.py images/logo.png --website --public` |
| Create favicons | `python3 convert-image.py images/logo.png --favicon --public` |
| Convert multiple images | `python3 convert-image.py images/*.jpg` |

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
│   └── YYYYMMDD-HHMMSS/  # Timestamped directories for each conversion
│       ├── standard files...
│       └── web/  # Web-optimized files when using --website
├── public/       # Website assets including favicons
│   └── YYYYMMDD-HHMMSS/  # Timestamped directories (when using --public)
├── convert-image.py  # Main script
└── README.md
```

## Requirements

- Python 3.6+
- Pillow (PIL Fork)
- pillow-avif-plugin (for AVIF support)

```bash
pip3 install -r requirements.txt
```

### AVIF Support

To enable AVIF export with the `--website` flag:

```bash
pip3 install pillow-avif-plugin
```

Without the AVIF plugin, the script will still run but will skip AVIF conversion.

For testing with AVIF support without modifying your system Python:

```bash
# Create a virtual environment
python3 -m venv temp_venv
source temp_venv/bin/activate  # On Windows: temp_venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt

# Run the script
python3 convert-image.py images/* --website --public

# Exit virtual environment when done
deactivate
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

### Disable timestamped directories:

By default, output files are organized in timestamped directories. To disable this:

```bash
python3 convert-image.py images/logo.png --no-timestamp
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
- `.avif` - AVIF format (85% quality) - requires pillow-avif-plugin

### Favicon variants (with `--favicon`):
- `favicon.ico` - Standard favicon (16x16, 32x32, 48x48)
- `apple-touch-icon.png` - Apple touch icon (180x180)
- `favicon-192x192.png` - Android/Chrome icon
- `favicon-512x512.png` - Android/Chrome icon

### ZIP Archive Organization
Each ZIP file now contains a structured organization:
- `/{image-name}/` - Root directory named after the source image
  - `/standard/` - Basic formats (PNG, JPEG, SVG)
  - `/web/` - Web-optimized formats (WebP, AVIF)
  - `/favicon/` - Favicon files (when using --favicon)
  - `README.txt` - Information about the converted files