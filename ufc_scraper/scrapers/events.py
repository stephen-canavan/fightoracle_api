"""Event scraper for UFC events."""
import re
import logging
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class EventScraper(BaseScraper):
    """Scraper for UFC events."""
    
    def scrape_all_events(self, include_upcoming=True):
        """Scrape all completed and optionally upcoming events."""
        events = []
        events.extend(self._scrape_event_list("/statistics/events/completed?page=all"))
        if include_upcoming:
            events.extend(self._scrape_event_list("/statistics/events/upcoming"))
        logger.info(f"Scraped {len(events)} total events")
        return events
    
    def _scrape_event_list(self, path):
        """Scrape event listing page."""
        soup = self.fetch_page(self.build_url(path))
        events = []
        
        table = soup.find('table')
        if not table:
            return events
        
        rows = table.find('tbody').find_all('tr', class_='b-statistics__table-row')
        for row in rows:
            event = self._parse_event_row(row)
            if event:
                events.append(event)
        
        return events
    
    def _parse_event_row(self, row):
        """Parse a single event row."""
        cols = row.find_all('td', class_='b-statistics__table-col')
        if len(cols) < 2:
            return None
        
        # Extract event link and ID
        link = cols[0].find('a')
        if not link:
            return None
        
        event_url = link.get('href', '')
        event_id = event_url.split('/')[-1] if event_url else None
        if not event_id:
            return None
        
        # Extract name and date
        name_text = link.get_text(strip=True)
        date_text = cols[0].find('span', class_='b-statistics__date')
        date = date_text.get_text(strip=True) if date_text else ""
        
        # Extract location
        location = cols[1].get_text(strip=True)
        country, city, venue = self._parse_location(location)
        
        # Parse date to ISO format
        iso_date = self._parse_date(date)
        
        return {
            "ufcstats_event_id": event_id,
            "name": name_text,
            "date": iso_date,
            "location": location,
            "country": country,
            "city": city,
            "venue": venue
        }
    
    def _parse_location(self, location):
        """Parse location string into country, city, venue."""
        parts = [p.strip() for p in location.split(',')]
        if len(parts) >= 2:
            city = parts[0]
            country = parts[-1]
            venue = None
        else:
            city = location
            country = None
            venue = None
        return country, city, venue
    
    def _parse_date(self, date_str):
        """Parse date string to ISO format."""
        from datetime import datetime
        try:
            # Format: "February 21, 2026"
            dt = datetime.strptime(date_str, "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except:
            return date_str
    
    def scrape_event_fights(self, event_id):
        """Scrape all fight IDs for a specific event."""
        soup = self.fetch_page(self.build_url(f"/event-details/{event_id}"))
        fight_ids = []
        
        table = soup.find('table')
        if not table:
            return fight_ids
        
        rows = table.find('tbody').find_all('tr', class_='b-fight-details__table-row')
        for row in rows:
            link = row.get('data-link')
            if link:
                fight_id = link.split('/')[-1]
                fight_ids.append(fight_id)
        
        logger.info(f"Found {len(fight_ids)} fights for event {event_id}")
        return fight_ids
