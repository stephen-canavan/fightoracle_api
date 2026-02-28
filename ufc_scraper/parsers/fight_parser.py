"""Fight parser for extracting fight statistics from HTML."""
import re
import logging

logger = logging.getLogger(__name__)


class FightParser:
    """Parser for fight detail pages."""
    
    def parse_fight(self, soup, fight_id, event_id):
        """Parse complete fight details from soup."""
        fight_data = {
            "ufcstats_fight_id": fight_id,
            "ufcstats_event_id": event_id
        }
        
        # Parse fighters and basic info
        self._parse_fighters(soup, fight_data)
        self._parse_fight_details(soup, fight_data)
        
        # Parse statistics
        self._parse_totals(soup, fight_data)
        self._parse_significant_strikes(soup, fight_data)
        
        return fight_data
    
    def _parse_fighters(self, soup, fight_data):
        """Extract fighter IDs and names."""
        fighters = soup.find_all('a', class_='b-link')
        fighter_links = [f for f in fighters if '/fighter-details/' in f.get('href', '')]
        
        if len(fighter_links) >= 2:
            fighter_1_url = fighter_links[0].get('href', '')
            fighter_2_url = fighter_links[1].get('href', '')
            
            fight_data["ufcstats_fighter_red_id"] = fighter_1_url.split('/')[-1] if fighter_1_url else None
            fight_data["ufcstats_fighter_blue_id"] = fighter_2_url.split('/')[-1] if fighter_2_url else None
    
    def _parse_fight_details(self, soup, fight_data):
        """Parse fight details (method, round, time, etc.)."""
        # Method
        method_elem = soup.find('i', class_='b-fight-details__text-item_first')
        if method_elem and 'Method:' in method_elem.get_text():
            method_text = method_elem.get_text(strip=True).replace('Method:', '')
            fight_data["method"] = method_text
        
        # Details (method details)
        details_elem = soup.find_all('i', class_='b-fight-details__text-item_first')
        for elem in details_elem:
            if 'Details:' in elem.get_text():
                # Get next sibling text
                details_text = elem.find_next_sibling(text=True)
                if details_text:
                    fight_data["method_details"] = details_text.strip()
        
        # Round, Time, Referee
        text_items = soup.find_all('i', class_='b-fight-details__text-item')
        for item in text_items:
            text = item.get_text(strip=True)
            
            if text.startswith('Round:'):
                fight_data["round"] = self._parse_int(text.replace('Round:', ''))
            elif text.startswith('Time:'):
                fight_data["time"] = text.replace('Time:', '')
            elif text.startswith('Referee:'):
                fight_data["referee"] = text.replace('Referee:', '')
        
        # Determine winner
        result_divs = soup.find_all('i', class_='b-fight-details__person-status')
        if len(result_divs) >= 2:
            if 'W' in result_divs[0].get_text():
                fight_data["ufcstats_winner_id"] = fight_data.get("ufcstats_fighter_red_id")
            elif 'W' in result_divs[1].get_text():
                fight_data["ufcstats_winner_id"] = fight_data.get("ufcstats_fighter_blue_id")
        
        # Weight class and title fight detection
        weight_elem = soup.find('i', class_='b-fight-details__fight-title')
        if weight_elem:
            weight_text = weight_elem.get_text(strip=True)
            fight_data["is_title_fight"] = "Title" in weight_text
            fight_data["weight_class"] = weight_text.replace(' Bout', '').replace('UFC ', '').replace(' Title', '')
    
    def _parse_totals(self, soup, fight_data):
        """Parse total statistics table."""
        tables = soup.find_all('table')
        if not tables:
            return
        
        totals_table = tables[0]
        rows = totals_table.find_all('tr')
        
        # Row 0 is header, Row 1 has both fighters' data in paragraphs
        if len(rows) >= 2:
            data_row = rows[1]
            cols = data_row.find_all('td')
            
            if len(cols) >= 10:
                fight_data["fighter_red_stats"] = self._parse_stats_from_paragraphs(cols, 0)
                fight_data["fighter_blue_stats"] = self._parse_stats_from_paragraphs(cols, 1)
    
    def _parse_stats_from_paragraphs(self, cols, fighter_idx):
        """Parse stats for one fighter from paragraph elements."""
        def get_p_text(col, idx):
            ps = col.find_all('p')
            return ps[idx].get_text(strip=True) if len(ps) > idx else ""
        
        kd = get_p_text(cols[1], fighter_idx)
        sig_str = get_p_text(cols[2], fighter_idx)
        sig_pct = get_p_text(cols[3], fighter_idx)
        total_str = get_p_text(cols[4], fighter_idx)
        td = get_p_text(cols[5], fighter_idx)
        td_pct = get_p_text(cols[6], fighter_idx)
        sub = get_p_text(cols[7], fighter_idx)
        rev = get_p_text(cols[8], fighter_idx)
        ctrl = get_p_text(cols[9], fighter_idx)
        
        return {
            "knockdowns": self._parse_int(kd),
            "sig_strikes": self._parse_fraction(sig_str),
            "sig_strikes_pct": self._parse_percentage(sig_pct),
            "total_strikes": self._parse_fraction(total_str),
            "takedowns": self._parse_fraction(td),
            "takedown_pct": self._parse_percentage(td_pct),
            "submission_attempts": self._parse_int(sub),
            "reversals": self._parse_int(rev),
            "control_time": ctrl
        }
    
    def _parse_significant_strikes(self, soup, fight_data):
        """Parse significant strikes breakdown."""
        tables = soup.find_all('table')
        if len(tables) < 3:
            return
        
        sig_strikes_table = tables[2]
        rows = sig_strikes_table.find_all('tr')
        
        # Row 0 is header, Row 1 has both fighters' data in paragraphs
        if len(rows) >= 2:
            data_row = rows[1]
            cols = data_row.find_all('td')
            
            if len(cols) >= 9:
                fight_data["fighter_red_stats"]["sig_strikes_breakdown"] = self._parse_sig_strikes_from_paragraphs(cols, 0)
                fight_data["fighter_blue_stats"]["sig_strikes_breakdown"] = self._parse_sig_strikes_from_paragraphs(cols, 1)
    
    def _parse_sig_strikes_from_paragraphs(self, cols, fighter_idx):
        """Parse significant strikes for one fighter from paragraph elements."""
        def get_p_text(col, idx):
            ps = col.find_all('p')
            return ps[idx].get_text(strip=True) if len(ps) > idx else ""
        
        head = get_p_text(cols[3], fighter_idx)
        body = get_p_text(cols[4], fighter_idx)
        leg = get_p_text(cols[5], fighter_idx)
        distance = get_p_text(cols[6], fighter_idx)
        clinch = get_p_text(cols[7], fighter_idx)
        ground = get_p_text(cols[8], fighter_idx)
        
        return {
            "head": self._parse_fraction(head),
            "body": self._parse_fraction(body),
            "leg": self._parse_fraction(leg),
            "distance": self._parse_fraction(distance),
            "clinch": self._parse_fraction(clinch),
            "ground": self._parse_fraction(ground)
        }
    
    def _parse_fraction(self, text):
        """Parse 'X of Y' format to dict."""
        match = re.search(r'(\d+)\s+of\s+(\d+)', text)
        if match:
            return {"landed": int(match.group(1)), "attempted": int(match.group(2))}
        return {"landed": 0, "attempted": 0}
    
    def _parse_percentage(self, text):
        """Parse percentage string to int."""
        match = re.search(r'(\d+)%', text)
        return int(match.group(1)) if match else 0
    
    def _parse_int(self, text):
        """Parse integer from text."""
        match = re.search(r'\d+', text)
        return int(match.group(0)) if match else 0
