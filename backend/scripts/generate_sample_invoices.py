"""Generate 5 synthetic invoice images (PNG) for testing."""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).parent.parent / "sample_invoices"

INVOICES = [
    {
        "filename": "invoice_001_delta_airlines.png",
        "vendor": "Delta Airlines",
        "address": "1030 Delta Blvd, Atlanta, GA 30354",
        "invoice_number": "DL-2024-78432",
        "date": "November 15, 2024",
        "items": [
            ("Round-trip flight SFO-JFK", "$1,100.00"),
            ("Seat upgrade (Economy Comfort)", "$150.00"),
        ],
        "total": "$1,250.00",
    },
    {
        "filename": "invoice_002_marriott.png",
        "vendor": "Marriott Hotels",
        "address": "10400 Fernwood Rd, Bethesda, MD 20817",
        "invoice_number": "MH-889012",
        "date": "November 20, 2024",
        "items": [
            ("2 nights - King Suite", "$399.00"),
            ("Room service", "$62.50"),
            ("Parking (2 nights)", "$28.00"),
        ],
        "total": "$489.50",
    },
    {
        "filename": "invoice_003_github.png",
        "vendor": "GitHub, Inc.",
        "address": "88 Colin P Kelly Jr St, San Francisco, CA 94107",
        "invoice_number": "GH-ENT-2024-1201",
        "date": "December 1, 2024",
        "items": [
            ("GitHub Enterprise Cloud - 11 seats", "$210.00"),
            ("Actions minutes overage", "$21.00"),
        ],
        "total": "$231.00",
    },
    {
        "filename": "invoice_004_capital_grille.png",
        "vendor": "The Capital Grille",
        "address": "155 E 42nd St, New York, NY 10017",
        "invoice_number": "",
        "date": "December 5, 2024",
        "items": [
            ("Dinner for 4", "$245.00"),
            ("Wine selection", "$89.00"),
            ("Gratuity (18%)", "$53.25"),
        ],
        "total": "$387.25",
    },
    {
        "filename": "invoice_005_staples.png",
        "vendor": "Staples",
        "address": "500 Staples Dr, Framingham, MA 01702",
        "invoice_number": "STP-99201",
        "date": "December 10, 2024",
        "items": [
            ("Printer paper (5 reams)", "$42.50"),
            ("Ink cartridges (2-pack)", "$67.80"),
            ("Binder clips (box of 100)", "$12.00"),
            ("Shipping", "$20.00"),
        ],
        "total": "$142.30",
    },
]


def _try_load_font(size: int):
    """Try to load a TTF font, fall back to default."""
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_invoice(inv: dict) -> Image.Image:
    width, height = 800, 600
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_title = _try_load_font(28)
    font_normal = _try_load_font(16)
    font_small = _try_load_font(13)
    font_bold = _try_load_font(18)

    y = 30

    # Header
    draw.text((40, y), inv["vendor"], fill="black", font=font_title)
    y += 40
    draw.text((40, y), inv["address"], fill="gray", font=font_small)
    y += 30

    # Line
    draw.line([(40, y), (width - 40, y)], fill="black", width=2)
    y += 20

    # Invoice info
    draw.text((40, y), "INVOICE", fill="black", font=font_bold)
    y += 30
    if inv["invoice_number"]:
        draw.text((40, y), f"Invoice #: {inv['invoice_number']}", fill="black", font=font_normal)
        y += 25
    draw.text((40, y), f"Date: {inv['date']}", fill="black", font=font_normal)
    y += 40

    # Column headers
    draw.text((40, y), "Description", fill="black", font=font_bold)
    draw.text((550, y), "Amount", fill="black", font=font_bold)
    y += 5
    draw.line([(40, y + 20), (width - 40, y + 20)], fill="lightgray", width=1)
    y += 30

    # Line items
    for desc, amount in inv["items"]:
        draw.text((40, y), desc, fill="black", font=font_normal)
        draw.text((570, y), amount, fill="black", font=font_normal)
        y += 28

    # Total line
    y += 10
    draw.line([(400, y), (width - 40, y)], fill="black", width=2)
    y += 10
    draw.text((400, y), "TOTAL:", fill="black", font=font_bold)
    draw.text((570, y), inv["total"], fill="black", font=font_bold)

    return img


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for inv in INVOICES:
        img = generate_invoice(inv)
        path = OUTPUT_DIR / inv["filename"]
        img.save(str(path))
        print(f"Generated: {path}")
    print(f"\nDone. {len(INVOICES)} invoices in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
