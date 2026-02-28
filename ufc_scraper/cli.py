"""Command-line interface for UFC scraper."""
import argparse
import logging
import sys
from datetime import datetime, timedelta
from scrapers.events import EventScraper
from scrapers.fights import FightScraper
from scrapers.fighters import FighterScraper
from storage.json_store import JSONStore

logger = logging.getLogger(__name__)


class CLI:
    """Command-line interface handler."""
    
    def __init__(self):
        self.store = JSONStore()
        self.event_scraper = EventScraper()
        self.fight_scraper = FightScraper()
        self.fighter_scraper = FighterScraper()
    
    def update_events(self, include_upcoming=True):
        """Update all events."""
        logger.info("Updating events...")
        events = self.event_scraper.scrape_all_events(include_upcoming)
        self.store.save_events(events)
        self._update_metadata("events_update")
        logger.info(f"Saved {len(events)} events")
        return events
    
    def update_fighters(self):
        """Update all fighters."""
        logger.info("Updating all fighters...")
        fighter_ids = self.fighter_scraper.scrape_all_fighters()
        
        for i, fighter_id in enumerate(fighter_ids, 1):
            try:
                fighter_data = self.fighter_scraper.scrape_fighter(fighter_id)
                self.store.save_fighter(fighter_data)
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(fighter_ids)} fighters")
            except Exception as e:
                logger.error(f"Failed to scrape fighter {fighter_id}: {e}")
        
        self._update_metadata("fighters_update")
        logger.info(f"Completed: {len(fighter_ids)} fighters")
    
    def update_fighter(self, name):
        """Update a specific fighter by name."""
        logger.info(f"Searching for fighter: {name}")
        # Search through all fighters to find matching name
        fighter_ids = self.fighter_scraper.scrape_all_fighters()
        
        for fighter_id in fighter_ids:
            try:
                fighter_data = self.fighter_scraper.scrape_fighter(fighter_id)
                full_name = f"{fighter_data.get('fname', '')} {fighter_data.get('sname', '')}".lower()
                if name.lower() in full_name:
                    self.store.save_fighter(fighter_data)
                    logger.info(f"Updated fighter: {fighter_data.get('fname')} {fighter_data.get('sname')}")
                    return fighter_data
            except Exception as e:
                logger.error(f"Error checking fighter {fighter_id}: {e}")
        
        logger.warning(f"Fighter '{name}' not found")
        return None
    
    def update_event(self, event_name):
        """Update a specific event and all its fights."""
        logger.info(f"Searching for event: {event_name}")
        events = self.store.load_events()
        
        matching_event = None
        for event in events:
            if event_name.lower() in event.get('name', '').lower():
                matching_event = event
                break
        
        if not matching_event:
            logger.warning(f"Event '{event_name}' not found. Run --update-events first.")
            return None
        
        event_id = matching_event["ufcstats_event_id"]
        logger.info(f"Found event: {matching_event['name']}")
        
        # Scrape all fights for this event
        fight_ids = self.event_scraper.scrape_event_fights(event_id)
        
        for i, fight_id in enumerate(fight_ids, 1):
            try:
                fight_data = self.fight_scraper.scrape_fight(fight_id, event_id)
                self.store.save_fight(fight_data)
                logger.info(f"Progress: {i}/{len(fight_ids)} fights")
            except Exception as e:
                logger.error(f"Failed to scrape fight {fight_id}: {e}")
        
        logger.info(f"Completed: {len(fight_ids)} fights for event")
    
    def update_fight(self, fight_id):
        """Update a specific fight by ID."""
        logger.info(f"Updating fight: {fight_id}")
        try:
            fight_data = self.fight_scraper.scrape_fight(fight_id)
            self.store.save_fight(fight_data)
            logger.info(f"Saved fight {fight_id}")
            return fight_data
        except Exception as e:
            logger.error(f"Failed to scrape fight {fight_id}: {e}")
            return None
    
    def update_recent(self, days=30):
        """Update events from the last N days."""
        logger.info(f"Updating events from last {days} days...")
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        events = self.event_scraper.scrape_all_events(include_upcoming=True)
        recent_events = [e for e in events if e.get('date', '') >= cutoff_date]
        
        logger.info(f"Found {len(recent_events)} recent events")
        
        for event in recent_events:
            event_id = event["ufcstats_event_id"]
            fight_ids = self.event_scraper.scrape_event_fights(event_id)
            
            for fight_id in fight_ids:
                try:
                    fight_data = self.fight_scraper.scrape_fight(fight_id, event_id)
                    self.store.save_fight(fight_data)
                except Exception as e:
                    logger.error(f"Failed to scrape fight {fight_id}: {e}")
        
        self.store.save_events(events)
        self._update_metadata("recent_update")
        logger.info("Recent update completed")
    
    def _update_metadata(self, operation):
        """Update metadata with timestamp."""
        metadata = self.store.load_metadata()
        metadata[operation] = datetime.now().isoformat()
        self.store.save_metadata(metadata)
    
    def show_status(self):
        """Show last update timestamps."""
        metadata = self.store.load_metadata()
        if not metadata:
            print("No scraping history found")
            return
        
        print("Last updates:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    
    def filter_by_date_range(self, date_from, date_to):
        """Filter events by date range."""
        events = self.store.load_events()
        filtered = [e for e in events if date_from <= e.get('date', '') <= date_to]
        logger.info(f"Found {len(filtered)} events between {date_from} and {date_to}")
        return filtered
    
    def filter_by_weight_class(self, weight_class):
        """Filter fighters by weight class (searches fight data)."""
        logger.info(f"Filtering by weight class: {weight_class}")
        # This would require loading all fights and filtering
        # Implementation depends on use case
        pass


def setup_logging(verbose=False, quiet=False):
    """Configure logging."""
    from config import LOG_FILE
    
    level = logging.DEBUG if verbose else logging.WARNING if quiet else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='UFC Stats Scraper')
    
    # Update commands
    parser.add_argument('--update-events', action='store_true', help='Fetch all events')
    parser.add_argument('--update-fighters', action='store_true', help='Fetch all fighters')
    parser.add_argument('--update-recent', type=int, metavar='DAYS', help='Update events from last N days')
    
    # Query commands
    parser.add_argument('--fighter', type=str, help='Fetch specific fighter by name')
    parser.add_argument('--event', type=str, help='Fetch specific event by name')
    parser.add_argument('--fight-id', type=str, help='Fetch specific fight by ID')
    
    # Filters
    parser.add_argument('--date-from', type=str, help='Filter events from date (YYYY-MM-DD)')
    parser.add_argument('--date-to', type=str, help='Filter events to date (YYYY-MM-DD)')
    parser.add_argument('--weight-class', type=str, help='Filter by weight class')
    
    # Options
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('--quiet', action='store_true', help='Minimal logging')
    parser.add_argument('--status', action='store_true', help='Show last update timestamps')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose, args.quiet)
    cli = CLI()
    
    try:
        if args.status:
            cli.show_status()
            return
        
        if args.update_events:
            cli.update_events()
        
        if args.update_fighters:
            cli.update_fighters()
        
        if args.update_recent:
            cli.update_recent(args.update_recent)
        
        if args.fighter:
            cli.update_fighter(args.fighter)
        
        if args.event:
            cli.update_event(args.event)
        
        if args.fight_id:
            cli.update_fight(args.fight_id)
        
        if args.date_from and args.date_to:
            events = cli.filter_by_date_range(args.date_from, args.date_to)
            print(f"Found {len(events)} events in date range")
        
        if not any(vars(args).values()):
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
