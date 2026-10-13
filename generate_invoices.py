"""Generate fictional sample invoices (digital PDFs) for the Automation Anywhere invoice-processing bot.
All companies, people and numbers are made up. Two invoices are deliberately invalid to test the bot's validation:
INV-2026-0107 (stated total does not match the line items) and INV-2026-0108 (missing PO number)."""
import csv
from decimal import Decimal, ROUND_HALF_UP
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

VAT = Decimal('0.21')
D = lambda x: Decimal(str(x)).quantize(Decimal('0.01'), ROUND_HALF_UP)

INVOICES = [
    # number, date, due, po, vendor, vendor address, lines [(desc, qty, unit)], override_total
    ('INV-2026-0101', '01-10-2026', '31-10-2026', 'PO-45001', 'Northwind Textiles B.V.', 'Kanaalweg 12, 3526 KL Utrecht',
     [('Running shirt fabric (roll)', 12, 145.00), ('Mesh lining (roll)', 6, 88.50)], None),
    ('INV-2026-0102', '02-10-2026', '01-11-2026', 'PO-45002', 'Delta Logistics Services B.V.', 'Havenstraat 4, 3011 AA Rotterdam',
     [('Pallet transport DC Venlo – Hilversum', 3, 420.00), ('Warehouse handling', 10, 35.00), ('Fuel surcharge', 1, 96.40)], None),
    ('INV-2026-0103', '03-10-2026', '02-11-2026', 'PO-45003', 'Polder Print & Packaging', 'Industrieweg 88, 1271 AB Huizen',
     [('Shoe boxes, printed (x1000)', 4, 610.00)], None),
    ('INV-2026-0104', '05-10-2026', '04-11-2026', 'PO-45004', 'Alpine Office Supplies GmbH', 'Bahnhofstraße 21, 80335 München',
     [('Ergonomic office chair', 5, 289.00), ('Monitor arm', 5, 74.90), ('Desk lamp', 5, 39.95), ('Cable kit', 10, 12.50)], None),
    ('INV-2026-0105', '06-10-2026', '05-11-2026', 'PO-45005', 'Canal City IT Consultancy', 'Prinsengracht 300, 1016 HX Amsterdam',
     [('Data integration consultancy (hours)', 16, 115.00), ('Cloud environment setup', 1, 750.00)], None),
    ('INV-2026-0106', '07-10-2026', '06-11-2026', 'PO-45006', 'Northwind Textiles B.V.', 'Kanaalweg 12, 3526 KL Utrecht',
     [('Recycled polyester yarn (kg)', 250, 6.40), ('Dyeing service (batch)', 2, 380.00)], None),
    # deliberately invalid: stated total is wrong
    ('INV-2026-0107', '08-10-2026', '07-11-2026', 'PO-45007', 'Delta Logistics Services B.V.', 'Havenstraat 4, 3011 AA Rotterdam',
     [('Express parcel shipments', 40, 14.75), ('Returns handling', 12, 9.90)], 999.99),
    # deliberately invalid: missing PO number
    ('INV-2026-0108', '09-10-2026', '08-11-2026', '', 'Polder Print & Packaging', 'Industrieweg 88, 1271 AB Huizen',
     [('Hang tags (x5000)', 2, 180.00), ('Labels (x10000)', 1, 245.00)], None),
]

styles = getSampleStyleSheet()
answer_rows = []
for num, date, due, po, vendor, addr, lines, override in INVOICES:
    rows = [['Description', 'Qty', 'Unit price (EUR)', 'Line total (EUR)']]
    subtotal = Decimal('0')
    for desc, qty, unit in lines:
        lt = D(Decimal(str(qty)) * D(unit)); subtotal += lt
        rows.append([desc, str(qty), f'{D(unit):,.2f}', f'{lt:,.2f}'])
    vat = D(subtotal * VAT); total = D(subtotal + vat)
    stated = D(override) if override is not None else total
    doc = SimpleDocTemplate(f'sample_invoices/{num}.pdf', pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=18*mm)
    head = [
        Paragraph(f'<b>{vendor}</b><br/>{addr}<br/>VAT: NL00{num[-4:]}B01', styles['Normal']), Spacer(1, 8*mm),
        Paragraph('<b>INVOICE</b>', styles['Title']),
        Table([['Invoice number:', num], ['Invoice date:', date], ['Due date:', due], ['PO number:', po],
               ['Bill to:', 'Example Retail Europe B.V., Voorbeeldstraat 1, 1200 AA Hilversum']], colWidths=[40*mm, 120*mm]),
        Spacer(1, 8*mm),
    ]
    t = Table(rows, colWidths=[80*mm, 15*mm, 35*mm, 35*mm])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dddddd')), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                           ('ALIGN', (1, 1), (-1, -1), 'RIGHT')]))
    totals = Table([['Subtotal (EUR):', f'{subtotal:,.2f}'], ['VAT 21% (EUR):', f'{vat:,.2f}'], ['Total (EUR):', f'{stated:,.2f}']],
                   colWidths=[130*mm, 35*mm])
    totals.setStyle(TableStyle([('ALIGN', (1, 0), (1, -1), 'RIGHT'), ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold')]))
    doc.build(head + [t, Spacer(1, 6*mm), totals, Spacer(1, 10*mm), Paragraph('Payment within 30 days to IBAN NL00 FAKE 0000 0000 00. Fictional sample invoice.', styles['Italic'])])
    status = 'VALID'
    if stated != total: status = 'ERROR: total does not match line items'
    elif not po: status = 'ERROR: missing PO number'
    answer_rows.append([num, date, due, po, vendor, f'{subtotal:.2f}', f'{vat:.2f}', f'{stated:.2f}', len(lines), status])

with open('expected_results.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['invoice_number', 'invoice_date', 'due_date', 'po_number', 'vendor', 'subtotal', 'vat', 'stated_total', 'line_items', 'expected_status'])
    w.writerows(answer_rows)
print('done')
