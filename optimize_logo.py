from PIL import Image
from pathlib import Path
import sys

def optimize_logo(input_path, output_dir="static/img", size=160):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open + convert to RGBA for transparency
    img = Image.open(input_path).convert("RGBA")

    # Resize maintaining aspect ratio. 160px max for navbar
    img.thumbnail((size, size), Image.LANCZOS)

    # Save as WebP - 80 quality = tiny + sharp
    webp_path = output_dir / "logo.webp"
    img.save(webp_path, "WEBP", quality=80, method=6)

    # Also save PNG fallback for old browsers
    png_path = output_dir / "logo.png"
    img.save(png_path, "PNG", optimize=True)

    print(f"Done! Created:")
    print(f" {webp_path} - {webp_path.stat().st_size / 1024:.1f}KB")
    print(f" {png_path} - {png_path.stat().st_size / 1024:.1f}KB")
    print(f"\nUse logo.webp in your template for fastest load")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python optimize_logo.py path/to/your/image.jpg")
        sys.exit(1)
    optimize_logo(sys.argv[1])
