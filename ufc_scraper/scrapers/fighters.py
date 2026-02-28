"""Fighter scraper for UFC fighters."""
import logging
from scrapers.base import BaseScraper
from parsers.fighter_parser import FighterParser

logger = logging.getLogger(__name__)


class FighterScraper(BaseScraper):
    """Scraper for UFC fighter details."""
    
    def __init__(self):
        super().__init__()
        self.parser = FighterParser()
    
    def scrape_all_fighters(self):
        """Scrape all fighters from A-Z."""
        all_fighters = []
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            fighters = self._scrape_fighters_by_letter(letter)
            all_fighters.extend(fighters)
            logger.info(f"Scraped {len(fighters)} fighters for letter '{letter}'")
        
        logger.info(f"Total fighters scraped: {len(all_fighters)}")
        return all_fighters
    
    def _scrape_fighters_by_letter(self, letter):
        """Scrape all fighters for a specific letter."""
        soup = self.fetch_page(self.build_url(f"/statistics/fighters?char={letter}&page=all"))
        fighters = []
        
        table = soup.find('table', class_='b-statistics__table')
        if not table:
            return fighters
        
        rows = table.find('tbody').find_all('tr', class_='b-statistics__table-row')
        for row in rows:
            fighter_id = self._extract_fighter_id(row)
            if fighter_id:
                fighters.append(fighter_id)
        
        return fighters
    
    def _extract_fighter_id(self, row):
        """Extract fighter ID from table row."""
        link = row.find('a', class_='b-link b-link_style_black')
        if link:
            url = link.get('href', '')
            return url.split('/')[-1] if url else None
        return None
    
    def scrape_fighter(self, fighter_id):
        """Scrape detailed profile for a specific fighter."""
        soup = self.fetch_page(self.build_url(f"/fighter-details/{fighter_id}"))
        fighter_data = self.parser.parse_fighter(soup, fighter_id)
        logger.info(f"Scraped fighter {fighter_id}: {fighter_data.get('fname')} {fighter_data.get('sname')}")
        return fighter_data
