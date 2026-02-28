"""Test script to inspect HTML structure."""
import sys
sys.path.insert(0, '/home/etnseca/ufc_scraper')

from scrapers.base import BaseScraper

scraper = BaseScraper()
soup = scraper.fetch_page("http://ufcstats.com/fight-details/8d740c844353ae0e")

# Find all tables
tables = soup.find_all('table')
print(f"Found {len(tables)} tables\n")

# Print first table structure
if tables:
    print("=== TABLE 1 (Totals) ===")
    rows = tables[0].find_all('tr')
    for i, row in enumerate(rows[:3]):
        cols = row.find_all(['th', 'td'])
        print(f"\nRow {i}: {len(cols)} columns")
        for j, col in enumerate(cols):
            text = col.get_text(strip=True)
            print(f"  Col {j}: '{text[:80]}'")
            # Check for nested paragraphs
            ps = col.find_all('p')
            if ps:
                print(f"    -> {len(ps)} paragraphs:")
                for p in ps:
                    print(f"       '{p.get_text(strip=True)}'")

