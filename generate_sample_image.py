"""
Run this script once to generate sample_data/sample_invoice.png
Usage: python generate_sample_image.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

def generate_invoice():
    W, H = 800, 600
    img = Image.new("RGB", (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try to use a system font; fall back to default
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    # Header bar
    draw.rectangle([(0, 0), (W, 80)], fill=(26, 26, 46))
    draw.text((30, 20), "TechCorp Solutions", fill=(255, 255, 255), font=font_large)
    draw.text((580, 30), "INVOICE", fill=(76, 155, 232), font=font_large)

    # Company info
    draw.text((30, 100), "123 Business Park, Tech City, CA 90210", fill=(80, 80, 80), font=font_small)
    draw.text((30, 120), "Email: billing@techcorp.com  |  Tel: +1-555-0123", fill=(80, 80, 80), font=font_small)

    # Invoice details
    draw.text((30, 160), "Invoice #:", fill=(40, 40, 40), font=font_medium)
    draw.text((160, 160), "INV-2024-0892", fill=(26, 26, 46), font=font_medium)
    draw.text((30, 185), "Date:", fill=(40, 40, 40), font=font_medium)
    draw.text((160, 185), "March 5, 2024", fill=(26, 26, 46), font=font_medium)
    draw.text((30, 210), "Due Date:", fill=(40, 40, 40), font=font_medium)
    draw.text((160, 210), "April 4, 2024", fill=(26, 26, 46), font=font_medium)

    draw.text((450, 160), "Bill To:", fill=(40, 40, 40), font=font_medium)
    draw.text((450, 185), "Acme Corp Ltd.", fill=(26, 26, 46), font=font_medium)
    draw.text((450, 205), "456 Client Ave, New York, NY 10001", fill=(80, 80, 80), font=font_small)

    # Divider
    draw.rectangle([(30, 248), (770, 250)], fill=(200, 200, 200))

    # Table header
    draw.rectangle([(30, 255), (770, 285)], fill=(26, 26, 46))
    headers = ["Description", "Qty", "Unit Price", "Total"]
    x_positions = [40, 420, 510, 650]
    for h, x in zip(headers, x_positions):
        draw.text((x, 263), h, fill=(255, 255, 255), font=font_medium)

    # Line items
    items = [
        ("Laptop Pro 15\" (i9, 32GB RAM)", "2", "$1,850.00", "$3,700.00"),
        ("Wireless Mouse & Keyboard Set", "5", "$89.99", "$449.95"),
        ("USB-C Docking Station", "3", "$249.00", "$747.00"),
        ("SSD External Drive 2TB", "4", "$129.99", "$519.96"),
    ]
    row_colors = [(255, 255, 255), (240, 248, 255)]
    for i, (desc, qty, unit, total) in enumerate(items):
        y = 295 + i * 35
        draw.rectangle([(30, y), (770, y + 34)], fill=row_colors[i % 2])
        draw.text((40, y + 9), desc, fill=(40, 40, 40), font=font_small)
        draw.text((420, y + 9), qty, fill=(40, 40, 40), font=font_small)
        draw.text((510, y + 9), unit, fill=(40, 40, 40), font=font_small)
        draw.text((650, y + 9), total, fill=(40, 40, 40), font=font_small)

    # Totals
    y_total = 440
    draw.rectangle([(30, y_total), (770, y_total + 1)], fill=(200, 200, 200))
    draw.text((500, y_total + 10), "Subtotal:", fill=(40, 40, 40), font=font_medium)
    draw.text((650, y_total + 10), "$5,416.91", fill=(40, 40, 40), font=font_medium)
    draw.text((500, y_total + 35), "Tax (8.5%):", fill=(40, 40, 40), font=font_medium)
    draw.text((650, y_total + 35), "$460.44", fill=(40, 40, 40), font=font_medium)
    draw.rectangle([(490, y_total + 65), (770, y_total + 95)], fill=(26, 26, 46))
    draw.text((500, y_total + 72), "TOTAL DUE:", fill=(255, 255, 255), font=font_medium)
    draw.text((650, y_total + 72), "$5,877.35", fill=(76, 155, 232), font=font_medium)

    # Footer
    draw.rectangle([(0, 555), (W, H)], fill=(240, 240, 240))
    draw.text((30, 565), "Payment due within 30 days. Thank you for your business!", fill=(80, 80, 80), font=font_small)

    # Border
    draw.rectangle([(0, 0), (W - 1, H - 1)], outline=(200, 200, 200), width=2)

    out_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_invoice.png")
    img.save(out_path)
    print(f"Generated: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_invoice()
