"""Test script to verify draw fight parsing."""
from ufc_scraper.scrapers.fights import FightScraper

# Example 1: Split draw - http://ufcstats.com/fight-details/3c3a9c1ec0604fc2
# Example 2: Unanimous draw - http://ufcstats.com/fight-details/dcf161082c849205

scraper = FightScraper()

print("=" * 80)
print("Testing Split Draw (Example 1)")
print("=" * 80)
fight1 = scraper.scrape_fight("3c3a9c1ec0604fc2")
print(f"Method: {fight1.get('method')}")
print(f"Winner ID: {fight1.get('ufcstats_winner_id')}")
print(f"Scorecards: {fight1.get('scorecards')}")
print()

print("=" * 80)
print("Testing Unanimous Draw (Example 2)")
print("=" * 80)
fight2 = scraper.scrape_fight("dcf161082c849205")
print(f"Method: {fight2.get('method')}")
print(f"Winner ID: {fight2.get('ufcstats_winner_id')}")
print(f"Scorecards: {fight2.get('scorecards')}")
