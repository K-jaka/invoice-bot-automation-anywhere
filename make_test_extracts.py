"""Build test extraction CSVs in exactly the format Automation Anywhere Document Automation produced for INV-2026-0101
(12 columns, one row per line item, header fields repeated, thousands commas on amounts). Used only to develop the bot
while the Community Edition extraction limit was reached; replace with real extractions when available."""
import csv, os
from decimal import Decimal, ROUND_HALF_UP
import generate_invoices as g  # reuses the same invoice definitions (regenerates the PDFs too, identical content)

D = lambda x: Decimal(str(x)).quantize(Decimal('0.01'), ROUND_HALF_UP)
fmt = lambda d: f'{d:,.2f}'
os.makedirs('test_extracts', exist_ok=True)
HEAD = ['invoice_number','invoice_date','po_number','total_amount','due_date','subtotal','tax_amount','vendor_name','description','quantity','unit_price','total_price']
for num, date, due, po, vendor, addr, lines, override in g.INVOICES:
    sub = sum(D(Decimal(str(q)) * D(u)) for _, q, u in lines)
    tax = D(sub * g.VAT); total = D(override) if override is not None else D(sub + tax)
    with open(f'test_extracts/TEST_{num}.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(HEAD)
        for desc, q, u in lines:
            w.writerow([num, date, po, fmt(total), due, fmt(sub), f'{tax:.2f}', vendor, desc, str(q), fmt(D(u)), fmt(D(Decimal(str(q)) * D(u)))])
print('ok')
