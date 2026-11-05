"""
generate_sample.py - Creates a sample number plate image for testing.
Run once: python generate_sample.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "assets", "sample_plate.png")

def make_plate(text="MH12AB1234", width=520, height=130):
    """Draw a realistic-looking white number plate on a white background."""
    # Outer image (vehicle-like context)
    img = Image.new("RGB", (800, 500), color=(50, 55, 65))
    draw = ImageDraw.Draw(img)

    # Plate background (white rectangle)
    px, py = 140, 185
    pw, ph = 520, 130
    draw.rectangle([px-4, py-4, px+pw+4, py+ph+4], fill=(80,80,80))  # shadow
    draw.rectangle([px, py, px+pw, py+ph], fill=(255, 255, 240))
    draw.rectangle([px+2, py+2, px+pw-2, py+ph-2], outline=(0,0,0), width=3)

    # Blue strip (Indian plate style)
    draw.rectangle([px+2, py+2, px+44, py+ph-2], fill=(0, 0, 180))

    # IND text on blue strip
    try:
        font_small = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font_small = ImageFont.load_default()
    draw.text((px+10, py+50), "IND", fill="white", font=font_small)

    # Plate text
    try:
        font_plate = ImageFont.truetype("arialbd.ttf", 62)
    except Exception:
        try:
            font_plate = ImageFont.truetype("arial.ttf", 62)
        except Exception:
            font_plate = ImageFont.load_default()

    # Center the text on the plate (accounting for blue strip)
    text_area_start = px + 50
    text_area_width = pw - 50
    try:
        bbox = draw.textbbox((0, 0), text, font=font_plate)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except Exception:
        tw, th = len(text) * 35, 60

    tx = text_area_start + (text_area_width - tw) // 2
    ty = py + (ph - th) // 2

    draw.text((tx+2, ty+2), text, fill=(80,80,80), font=font_plate)  # shadow
    draw.text((tx, ty), text, fill=(10, 10, 10), font=font_plate)

    # Some car body context
    draw.ellipse([50, 380, 220, 480], fill=(40,40,50))   # left wheel
    draw.ellipse([580, 380, 750, 480], fill=(40,40,50))  # right wheel
    draw.rectangle([30, 250, 770, 400], fill=(60,65,75)) # bumper area

    return img

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plate_img = make_plate("MH12AB1234")
    plate_img.save(OUTPUT_PATH)
    print(f"Sample plate image saved to: {OUTPUT_PATH}")
