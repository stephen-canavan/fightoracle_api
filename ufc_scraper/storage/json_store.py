"""JSON storage management."""
import json
import os
from pathlib import Path
from config import EVENTS_FILE, FIGHTS_DIR, FIGHTERS_DIR, METADATA_FILE


class JSONStore:
    """Handle JSON file operations."""
    
    def __init__(self):
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Ensure all data directories exist."""
        for path in [EVENTS_FILE, FIGHTS_DIR, FIGHTERS_DIR, METADATA_FILE]:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    def save_events(self, events):
        """Save events list to JSON."""
        with open(EVENTS_FILE, 'w') as f:
            json.dump({"events": events}, f, indent=2)
    
    def load_events(self):
        """Load events from JSON."""
        if not os.path.exists(EVENTS_FILE):
            return []
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f).get("events", [])
    
    def save_fight(self, fight_data):
        """Save individual fight to JSON."""
        fight_id = fight_data["ufcstats_fight_id"]
        path = f"{FIGHTS_DIR}/{fight_id}.json"
        with open(path, 'w') as f:
            json.dump(fight_data, f, indent=2)
    
    def load_fight(self, fight_id):
        """Load individual fight from JSON."""
        path = f"{FIGHTS_DIR}/{fight_id}.json"
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            return json.load(f)
    
    def save_fighter(self, fighter_data):
        """Save individual fighter to JSON."""
        fighter_id = fighter_data["ufcstats_fighter_id"]
        fname = fighter_data.get("fname", "").lower().replace(" ", "_")
        sname = fighter_data.get("sname", "").lower().replace(" ", "_")
        path = f"{FIGHTERS_DIR}/{fighter_id}_{fname}_{sname}.json"
        with open(path, 'w') as f:
            json.dump(fighter_data, f, indent=2)
    
    def load_fighter(self, fighter_id):
        """Load individual fighter from JSON by ID."""
        for file in os.listdir(FIGHTERS_DIR):
            if file.startswith(fighter_id):
                with open(f"{FIGHTERS_DIR}/{file}", 'r') as f:
                    return json.load(f)
        return None
    
    def save_metadata(self, metadata):
        """Save metadata to JSON."""
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_metadata(self):
        """Load metadata from JSON."""
        if not os.path.exists(METADATA_FILE):
            return {}
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
