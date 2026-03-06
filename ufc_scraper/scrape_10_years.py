"""Scrape all fights for events from last 10 years."""
from storage.json_store import JSONStore
from scrapers.events import EventScraper
from scrapers.fights import FightScraper
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

store = JSONStore()
event_scraper = EventScraper()
fight_scraper = FightScraper()

# Load events
events = store.load_events()

# Filter events from last 10 years
cutoff = datetime(2016, 3, 3)
recent_events = [e for e in events if datetime.strptime(e['date'], '%Y-%m-%d') >= cutoff]

logger.info(f"Scraping fights for {len(recent_events)} events from last 10 years")

for i, event in enumerate(recent_events, 1):
    event_id = event['ufcstats_event_id']
    logger.info(f"[{i}/{len(recent_events)}] Scraping event: {event['name']} ({event['date']})")
    
    try:
        # Scrape event details and fights
        event_data = event_scraper.scrape_event(event_id)
        store.save_event(event_data)
        
        # Scrape each fight with position
        fights = event_scraper.scrape_event_fights(event_id)
        logger.info(f"  Found {len(fights)} fights")
        
        for fight_info in fights:
            try:
                fight_data = fight_scraper.scrape_fight(
                    fight_info['fight_id'], 
                    event_id,
                    card_position=fight_info['card_position']
                )
                store.save_fight(fight_data)
            except Exception as e:
                logger.error(f"  Failed to scrape fight {fight_info['fight_id']}: {e}")
        
    except Exception as e:
        logger.error(f"Failed to scrape event {event_id}: {e}")

logger.info("Scraping complete!")
