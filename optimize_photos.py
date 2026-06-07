from PIL import Image
from pathlib import Path
import sys

def optimize_photo(input_path, output_dir="static/images/products", max_width=1200):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open + convert to RGB. Photos don't need transparency
    img = Image.open(input_path).convert("RGB")
    
    # Resize if wider than 1200px. Good for mobile + desktop
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    name = input_path.stem

    # Save WebP - 75 quality = best size/quality balance for photos
    webp_path = output_dir / f"{name}.webp"
    img.save(webp_path, "WEBP", quality=75, method=6, optimize=True)

    # JPEG fallback for Safari <14 
    jpeg_path = output_dir / f"{name}.jpg"
    img.save(jpeg_path, "JPEG", quality=75, optimize=True, progressive=True)

    print(f"Done! Created:")
    print(f" {webp_path} - {webp_path.stat().st_size / 1024:.1f}KB")
    print(f" {jpeg_path} - {jpeg_path.stat().st_size / 1024:.1f}KB")
    print(f" Saved ~{100 - webp_path.stat().st_size / input_path.stat().st_size * 100:.0f}% vs original")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python optimize_photos.py path/to/image.jpg")
        sys.exit(1)
    for path in sys.argv[1:]:
        optimize_photo(path)
