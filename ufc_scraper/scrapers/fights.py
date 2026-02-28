"""Fight scraper for UFC fights."""
import logging
from scrapers.base import BaseScraper
from parsers.fight_parser import FightParser

logger = logging.getLogger(__name__)


class FightScraper(BaseScraper):
    """Scraper for UFC fight details."""
    
    def __init__(self):
        super().__init__()
        self.parser = FightParser()
    
    def scrape_fight(self, fight_id, event_id=None):
        """Scrape detailed statistics for a specific fight."""
        soup = self.fetch_page(self.build_url(f"/fight-details/{fight_id}"))
        
        # Extract event_id from page if not provided
        if not event_id:
            event_links = soup.find_all('a', class_='b-link')
            for link in event_links:
                href = link.get('href', '')
                if '/event-details/' in href:
                    event_id = href.split('/')[-1]
                    break
        
        fight_data = self.parser.parse_fight(soup, fight_id, event_id)
        logger.info(f"Scraped fight {fight_id}")
        return fight_data
