"""Test script to find method and referee."""
import sys
sys.path.insert(0, '/home/etnseca/ufc_scraper')

from scrapers.base import BaseScraper

scraper = BaseScraper()
soup = scraper.fetch_page("http://ufcstats.com/fight-details/8d740c844353ae0e")

# Find all i tags with style
all_i = soup.find_all('i')
print(f"Total i tags: {len(all_i)}\n")

for i, tag in enumerate(all_i[:20]):
    text = tag.get_text(strip=True)
    if text and len(text) < 100:
        print(f"{i}: class='{tag.get('class')}' text='{text}'")
