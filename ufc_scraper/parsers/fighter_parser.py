"""Fighter parser for extracting fighter data from HTML."""
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FighterParser:
    """Parser for fighter detail pages."""
    
    def parse_fighter(self, soup, fighter_id):
        """Parse complete fighter profile from soup."""
        fighter_data = {
            "ufcstats_fighter_id": fighter_id
        }
        
        # Parse name and record
        self._parse_name_and_record(soup, fighter_data)
        
        # Parse physical attributes
        self._parse_physical_attributes(soup, fighter_data)
        
        # Parse career statistics
        self._parse_career_stats(soup, fighter_data)
        
        return fighter_data
    
    def _parse_name_and_record(self, soup, fighter_data):
        """Extract fighter name and record."""
        name_elem = soup.find('span', class_='b-content__title-highlight')
        if name_elem:
            full_name = name_elem.get_text(strip=True)
            name_parts = full_name.split()
            fighter_data["fname"] = name_parts[0] if name_parts else ""
            fighter_data["sname"] = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Record
        record_elem = soup.find('span', class_='b-content__title-record')
        if record_elem:
            record_text = record_elem.get_text(strip=True)
            match = re.search(r'Record:\s*(\d+)-(\d+)-(\d+)', record_text)
            if match:
                fighter_data["record"] = {
                    "wins": int(match.group(1)),
                    "losses": int(match.group(2)),
                    "draws": int(match.group(3)),
                    "no_contests": 0,
                    "dqs": 0
                }
        
        # Nickname
        nickname_elem = soup.find('p', class_='b-content__Nickname')
        if nickname_elem:
            nickname = nickname_elem.get_text(strip=True).replace('Nickname:', '').strip()
            fighter_data["nickname"] = nickname if nickname else ""
    
    def _parse_physical_attributes(self, soup, fighter_data):
        """Extract physical attributes."""
        details = soup.find_all('li', class_='b-list__box-list-item')
        
        for detail in details:
            text = detail.get_text(strip=True)
            
            if 'Height:' in text:
                height = text.replace('Height:', '').strip()
                fighter_data["height_cm"] = self._convert_height_to_cm(height)
            elif 'Weight:' in text:
                weight = text.replace('Weight:', '').strip()
                fighter_data["weight_lbs"] = self._parse_weight(weight)
            elif 'Reach:' in text:
                reach = text.replace('Reach:', '').strip()
                fighter_data["reach_cm"] = self._convert_inches_to_cm(reach)
            elif 'STANCE:' in text:
                stance = text.replace('STANCE:', '').strip()
                fighter_data["stance"] = stance if stance != '--' else None
            elif 'DOB:' in text:
                dob = text.replace('DOB:', '').strip()
                fighter_data["dob"] = self._parse_dob(dob)
    
    def _parse_career_stats(self, soup, fighter_data):
        """Extract career statistics."""
        stats = {}
        stat_items = soup.find_all('li', class_='b-list__box-list-item b-list__box-list-item_type_block')
        
        for item in stat_items:
            text = item.get_text(strip=True)
            
            if 'SLpM:' in text:
                stats["slpm"] = self._parse_float(text.replace('SLpM:', ''))
            elif 'Str. Acc.:' in text:
                stats["str_acc"] = self._parse_percentage(text.replace('Str. Acc.:', ''))
            elif 'SApM:' in text:
                stats["sapm"] = self._parse_float(text.replace('SApM:', ''))
            elif 'Str. Def:' in text:
                stats["str_def"] = self._parse_percentage(text.replace('Str. Def:', ''))
            elif 'TD Avg.:' in text:
                stats["td_avg"] = self._parse_float(text.replace('TD Avg.:', ''))
            elif 'TD Acc.:' in text:
                stats["td_acc"] = self._parse_percentage(text.replace('TD Acc.:', ''))
            elif 'TD Def.:' in text:
                stats["td_def"] = self._parse_percentage(text.replace('TD Def.:', ''))
            elif 'Sub. Avg.:' in text:
                stats["sub_avg"] = self._parse_float(text.replace('Sub. Avg.:', ''))
        
        fighter_data["career_stats"] = stats
    
    def _convert_height_to_cm(self, height_str):
        """Convert height from feet'inches to cm."""
        match = re.search(r"(\d+)'\s*(\d+)\"", height_str)
        if match:
            feet = int(match.group(1))
            inches = int(match.group(2))
            total_inches = feet * 12 + inches
            return round(total_inches * 2.54, 1)
        return None
    
    def _convert_inches_to_cm(self, inches_str):
        """Convert inches to cm."""
        match = re.search(r'(\d+)', inches_str)
        if match:
            inches = int(match.group(1))
            return round(inches * 2.54, 1)
        return None
    
    def _parse_weight(self, weight_str):
        """Parse weight in lbs."""
        match = re.search(r'(\d+)', weight_str)
        return int(match.group(1)) if match else None
    
    def _parse_dob(self, dob_str):
        """Parse date of birth to ISO format."""
        try:
            dt = datetime.strptime(dob_str, "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except:
            return None
    
    def _parse_float(self, text):
        """Parse float from text."""
        match = re.search(r'[\d.]+', text)
        return float(match.group(0)) if match else 0.0
    
    def _parse_percentage(self, text):
        """Parse percentage to integer."""
        match = re.search(r'(\d+)%', text)
        return int(match.group(1)) if match else 0
