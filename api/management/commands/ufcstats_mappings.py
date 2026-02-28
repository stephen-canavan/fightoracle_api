"""Mapping utilities for converting UFCStats data to Django model choices."""

# Map UFCStats weight classes to Django WeightClass choices
WEIGHT_CLASS_MAP = {
    "Strawweight": "SW",
    "Women's Strawweight": "SW",
    "Flyweight": "FLY",
    "Women's Flyweight": "FLY",
    "Bantamweight": "BW",
    "Women's Bantamweight": "BW",
    "Featherweight": "FW",
    "Women's Featherweight": "FW",
    "Lightweight": "LW",
    "Welterweight": "WW",
    "Middleweight": "MW",
    "Light Heavyweight": "LHW",
    "Heavyweight": "HW",
    "Super Heavyweight": "SHW",
    "Catch Weight": "CW",
    "Catchweight": "CW",
}

# Map UFCStats methods to Django Method choices
METHOD_MAP = {
    "KO/TKO": "KO/TKO",
    "KO": "KO",
    "TKO": "KO/TKO",
    "SUB": "SUB",
    "Submission": "SUB",
    "U-DEC": "DEC",
    "S-DEC": "DEC-SPLIT",
    "M-DEC": "DEC",
    "Decision": "DEC",
    "DQ": "DQ",
    "NC": "NC",
    "No Contest": "NC",
}


def map_weight_class(ufcstats_weight_class):
    """Map UFCStats weight class to Django choice."""
    if not ufcstats_weight_class:
        return "MW"  # Default
    
    mapped = WEIGHT_CLASS_MAP.get(ufcstats_weight_class)
    if mapped:
        return mapped
    
    # Fallback: try to match partial
    for key, value in WEIGHT_CLASS_MAP.items():
        if key.lower() in ufcstats_weight_class.lower():
            return value
    
    return "MW"  # Default to Middleweight


def map_method(ufcstats_method):
    """Map UFCStats method to Django choice."""
    if not ufcstats_method:
        return "FINISH"  # Default
    
    mapped = METHOD_MAP.get(ufcstats_method)
    if mapped:
        return mapped
    
    # Fallback: try to match partial
    method_upper = ufcstats_method.upper()
    if "KO" in method_upper or "TKO" in method_upper:
        return "KO/TKO"
    elif "SUB" in method_upper:
        return "SUB"
    elif "DEC" in method_upper:
        if "SPLIT" in method_upper:
            return "DEC-SPLIT"
        return "DEC"
    elif "DQ" in method_upper:
        return "DQ"
    elif "NC" in method_upper or "NO CONTEST" in method_upper:
        return "NC"
    
    return "FINISH"  # Default
