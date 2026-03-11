"""Generate sample invoice PNG images for testing."""

from PIL import Image, ImageDraw, ImageFont
import os

# Try to use a clean font, fallback to default
try:
    font_large = ImageFont.truetype("arial.ttf", 28)
    font_medium = ImageFont.truetype("arial.ttf", 16)
    font_small = ImageFont.truetype("arial.ttf", 14)
    font_bold = ImageFont.truetype("arialbd.ttf", 16)
    font_header = ImageFont.truetype("arialbd.ttf", 14)
except Exception:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_header = ImageFont.load_default()


def create_invoice(filename, vendor, address, inv_number, date, line_items, total):
    img = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(img)

    # Vendor name
    draw.text((40, 30), vendor, fill="black", font=font_large)
    # Address
    draw.text((40, 65), address, fill="gray", font=font_small)
    # Horizontal line
    draw.line([(40, 90), (760, 90)], fill="black", width=2)

    # Invoice label
    draw.text((50, 110), "INVOICE", fill="black", font=font_bold)
    # Invoice number
    if inv_number:
        draw.text((50, 135), f"Invoice #: {inv_number}", fill="black", font=font_medium)
    else:
        draw.text((50, 135), "Invoice #: N/A", fill="gray", font=font_medium)
    # Date
    draw.text((50, 158), f"Date: {date}", fill="black", font=font_medium)

    # Table header line
    draw.line([(50, 195), (750, 195)], fill="black", width=1)
    draw.text((50, 200), "Description", fill="black", font=font_header)
    draw.text((550, 200), "Amount", fill="black", font=font_header)
    draw.line([(50, 220), (750, 220)], fill="black", width=1)

    # Line items
    y = 230
    for desc, amount in line_items:
        draw.text((50, y), desc, fill="black", font=font_medium)
        draw.text((550, y), f"${amount:,.2f}", fill="black", font=font_medium)
        y += 28

    # Total line
    y += 15
    draw.line([(430, y), (700, y)], fill="black", width=1)
    y += 8
    draw.text((430, y), "TOTAL:", fill="black", font=font_bold)
    draw.text((550, y), f"${total:,.2f}", fill="black", font=font_bold)

    path = os.path.join("sample_invoices", filename)
    img.save(path)
    print(f"  Created {filename}")


invoices = [
    # 006-008: Travel
    (
        "invoice_006_united_airlines.png",
        "United Airlines",
        "233 S Wacker Dr, Chicago, IL 60606",
        "UA-2024-55219",
        "December 15, 2024",
        [
            ("One-way flight LAX-ORD", 389.00),
            ("Checked bag fee", 35.00),
            ("Travel insurance", 29.99),
        ],
        453.99,
    ),
    (
        "invoice_007_hilton_hotels.png",
        "Hilton Hotels",
        "7930 Jones Branch Dr, McLean, VA 22102",
        "HLT-990341",
        "December 18, 2024",
        [
            ("3 nights - Executive Room", 597.00),
            ("Breakfast buffet (3x)", 89.85),
            ("Valet parking (3 nights)", 75.00),
        ],
        761.85,
    ),
    (
        "invoice_008_hertz_rental.png",
        "Hertz Car Rental",
        "8501 Williams Rd, Estero, FL 33928",
        "HZ-2024-44781",
        "December 20, 2024",
        [
            ("Compact sedan - 4 day rental", 196.00),
            ("GPS navigation add-on", 39.96),
            ("Fuel service option", 52.40),
        ],
        288.36,
    ),
    # 009-010: Meals & Entertainment
    (
        "invoice_009_doordash.png",
        "DoorDash Inc.",
        "303 2nd St, Suite 800, San Francisco, CA 94107",
        "DD-7823441",
        "December 12, 2024",
        [
            ("Team lunch order (8 meals)", 156.40),
            ("Delivery fee", 5.99),
            ("Service fee", 12.50),
            ("Tip", 25.00),
        ],
        199.89,
    ),
    (
        "invoice_010_ruth_chris.png",
        "Ruth's Chris Steak House",
        "500 International Dr, Winter Park, FL 32789",
        None,
        "December 22, 2024",
        [
            ("Dinner for 6 - prix fixe menu", 480.00),
            ("Wine pairing (6x)", 210.00),
            ("Gratuity (20%)", 138.00),
        ],
        828.00,
    ),
    # 011-013: Software / Subscriptions
    (
        "invoice_011_aws.png",
        "Amazon Web Services",
        "410 Terry Ave N, Seattle, WA 98109",
        "AWS-2024-12-9981",
        "December 1, 2024",
        [
            ("EC2 instances (m5.xlarge x3)", 312.48),
            ("S3 storage (2.1 TB)", 48.30),
            ("CloudFront bandwidth", 23.17),
            ("Route 53 DNS queries", 4.50),
        ],
        388.45,
    ),
    (
        "invoice_012_figma.png",
        "Figma, Inc.",
        "760 Market St, Suite 1000, San Francisco, CA 94102",
        "FIG-2024-8820",
        "December 1, 2024",
        [
            ("Figma Professional - 8 seats", 96.00),
            ("FigJam add-on - 8 seats", 40.00),
        ],
        136.00,
    ),
    (
        "invoice_013_slack.png",
        "Slack Technologies",
        "500 Howard St, San Francisco, CA 94105",
        "SLK-PRO-2024-1201",
        "December 1, 2024",
        [
            ("Slack Pro plan - 25 seats", 187.50),
            ("Slack Connect add-on", 25.00),
        ],
        212.50,
    ),
    # 014-015: Professional Services
    (
        "invoice_014_deloitte.png",
        "Deloitte Consulting LLP",
        "30 Rockefeller Plaza, New York, NY 10112",
        "DLT-2024-003871",
        "November 30, 2024",
        [
            ("Cloud migration assessment (40 hrs)", 8000.00),
            ("Architecture review (16 hrs)", 3200.00),
            ("Travel expenses", 1450.00),
        ],
        12650.00,
    ),
    (
        "invoice_015_outside_counsel.png",
        "Baker McKenzie LLP",
        "300 E Randolph St, Suite 5000, Chicago, IL 60601",
        "BM-INV-2024-7742",
        "December 10, 2024",
        [
            ("Contract review - SaaS agreement", 2500.00),
            ("IP consultation (4 hrs)", 1800.00),
            ("Filing fees", 350.00),
        ],
        4650.00,
    ),
    # 016-017: Office Supplies
    (
        "invoice_016_amazon_business.png",
        "Amazon Business",
        "410 Terry Ave N, Seattle, WA 98109",
        "AMZ-BIZ-114-9920341",
        "December 8, 2024",
        [
            ("Standing desk converter (x2)", 459.98),
            ("Ergonomic keyboard (x2)", 179.98),
            ("Monitor arm mount (x2)", 89.98),
            ("Cable management kit", 24.99),
        ],
        754.93,
    ),
    (
        "invoice_017_office_depot.png",
        "Office Depot",
        "6600 N Military Trail, Boca Raton, FL 33496",
        "OD-55129844",
        "December 14, 2024",
        [
            ("Copy paper - 10 ream case", 54.99),
            ("Whiteboard markers (24 pk)", 18.49),
            ("Sticky notes (12 pk)", 11.99),
            ("Folders and binders", 32.47),
        ],
        117.94,
    ),
    # 018-019: Shipping / Postage
    (
        "invoice_018_fedex.png",
        "FedEx Corporation",
        "942 S Shady Grove Rd, Memphis, TN 38120",
        "FX-8829104477",
        "December 16, 2024",
        [
            ("Overnight Priority - 3 packages", 127.50),
            ("Declared value coverage", 9.75),
            ("Residential surcharge", 13.80),
        ],
        151.05,
    ),
    (
        "invoice_019_ups.png",
        "UPS (United Parcel Service)",
        "55 Glenlake Pkwy NE, Atlanta, GA 30328",
        "UPS-1Z999AA10123456784",
        "December 19, 2024",
        [
            ("2-Day Air - server equipment", 89.50),
            ("Saturday delivery surcharge", 16.00),
            ("Insurance (declared $2000)", 24.00),
        ],
        129.50,
    ),
    # 020-021: Utilities
    (
        "invoice_020_comcast_business.png",
        "Comcast Business",
        "1701 JFK Blvd, Philadelphia, PA 19103",
        "CB-2024-12-4481990",
        "December 1, 2024",
        [
            ("Business Internet 300 Mbps", 149.99),
            ("Static IP block (/29)", 29.99),
            ("Business phone line", 39.99),
            ("Equipment rental", 15.00),
        ],
        234.97,
    ),
    (
        "invoice_021_duke_energy.png",
        "Duke Energy",
        "550 S Tryon St, Charlotte, NC 28202",
        "DE-ACCT-88201-DEC24",
        "December 5, 2024",
        [
            ("Electric service - office suite", 287.43),
            ("Demand charge", 45.00),
            ("Fuel adjustment", 12.18),
        ],
        344.61,
    ),
    # 022-025: Mixed / Other / Edge cases
    (
        "invoice_022_wework.png",
        "WeWork",
        "115 W 18th St, New York, NY 10011",
        "WW-2024-MEM-8841",
        "December 1, 2024",
        [
            ("Hot desk membership - 2 persons", 600.00),
            ("Meeting room credits (20 hrs)", 200.00),
            ("Printing credits", 25.00),
        ],
        825.00,
    ),
    (
        "invoice_023_coursera.png",
        "Coursera for Business",
        "381 E Evelyn Ave, Mountain View, CA 94041",
        "CRS-TEAM-2024-1155",
        "December 1, 2024",
        [
            ("Team plan - 10 licenses", 399.00),
            ("Professional certificates (3x)", 147.00),
        ],
        546.00,
    ),
    (
        "invoice_024_catering_co.png",
        "Corporate Catering Co.",
        "1200 Main St, Suite 100, Dallas, TX 75201",
        "CC-EVT-2024-882",
        "December 20, 2024",
        [
            ("Holiday party catering - 50 ppl", 1250.00),
            ("Bar service (open bar 3 hrs)", 750.00),
            ("Setup and cleanup", 200.00),
            ("Linens and decor rental", 150.00),
        ],
        2350.00,
    ),
    (
        "invoice_025_misc_vendor.png",
        "Green Planet Sustainability",
        "42 Eco Way, Portland, OR 97201",
        None,
        "December 11, 2024",
        [
            ("Carbon offset credits (Q4)", 500.00),
            ("Sustainability audit report", 1200.00),
            ("Employee green commute program", 300.00),
        ],
        2000.00,
    ),
]


if __name__ == "__main__":
    print(f"Generating {len(invoices)} invoice images...")
    for args in invoices:
        create_invoice(*args)
    print(f"\nDone! {len(invoices)} invoices created in sample_invoices/")
