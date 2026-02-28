#!/usr/bin/env python3
"""Demo script to test UFC scraper functionality."""
import sys
import json
sys.path.insert(0, '/home/etnseca/ufc_scraper')

from scrapers.events import EventScraper
from scrapers.fights import FightScraper
from scrapers.fighters import FighterScraper
from storage.json_store import JSONStore

print("=== UFC Scraper Demo ===\n")

store = JSONStore()

# Test 1: Scrape a single fighter
print("1. Scraping fighter: Sean Strickland")
fighter_scraper = FighterScraper()
fighter = fighter_scraper.scrape_fighter('0d8011111be000b2')
store.save_fighter(fighter)
print(f"   ✓ Saved: {fighter['fname']} {fighter['sname']}")
print(f"   Record: {fighter['record']['wins']}-{fighter['record']['losses']}-{fighter['record']['draws']}")
print(f"   Height: {fighter['height_cm']} cm, Reach: {fighter['reach_cm']} cm\n")

# Test 2: Scrape a single fight
print("2. Scraping fight: Strickland vs Hernandez")
fight_scraper = FightScraper()
fight = fight_scraper.scrape_fight('8d740c844353ae0e')
store.save_fight(fight)
print(f"   ✓ Saved fight {fight['ufcstats_fight_id']}")
print(f"   Method: {fight['method']} - {fight.get('method_details', 'N/A')}")
print(f"   Round {fight['round']} at {fight['time']}")
print(f"   Red corner strikes: {fight['fighter_red_stats']['sig_strikes']['landed']}/{fight['fighter_red_stats']['sig_strikes']['attempted']}")
print(f"   Blue corner strikes: {fight['fighter_blue_stats']['sig_strikes']['landed']}/{fight['fighter_blue_stats']['sig_strikes']['attempted']}\n")

# Test 3: Scrape upcoming events
print("3. Scraping upcoming events")
event_scraper = EventScraper()
events = event_scraper._scrape_event_list('/statistics/events/upcoming')
store.save_events(events)
print(f"   ✓ Saved {len(events)} upcoming events")
if events:
    print(f"   Next event: {events[0]['name']} on {events[0]['date']}\n")

print("=== Demo Complete ===")
print(f"\nData saved to:")
print(f"  - data/events.json")
print(f"  - data/fights/8d740c844353ae0e.json")
print(f"  - data/fighters/0d8011111be000b2_sean_strickland.json")
