from django.db import models
from django_countries import Countries


class Promotions(models.TextChoices):
    UFC = "UFC", "Ultimate Fighting Championship"
    PFL = "PFL", "Professional Fighters League"
    BELLA = "Bellator", "Bellator MMA"
    ONE = "ONE", "ONE Championship"


## Fights
class WeightClass(models.TextChoices):
    UNKNOWN = "UNKNOWN", "Unknown"
    STRAWWEIGHT = "SW", "Strawweight"
    FLYWEIGHT = "FLY", "Flyweight"
    BANTAMWEIGHT = "BW", "Bantamweight"
    FEATHERWEIGHT = "FW", "Featherweight"
    LIGHTWEIGHT = "LW", "Lightweight"
    WELTERWEIGHT = "WW", "Welterweight"
    MIDDLEWEIGHT = "MW", "Middleweight"
    LIGHTHEAVYWEIGHT = "LHW", "Light Heavyweight"
    HEAVYWEIGHT = "HW", "Heavyweight"
    SUPERHEAVYWEIGHT = "SHW", "Super Heavyweight"
    CATCHWEIGHT = "CW", "Catchweight"


class FightStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class EventStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class Method(models.TextChoices):
    KO = "KO"
    TKO = "TKO"
    KOTKO = "KO/TKO"
    SUB = "SUB"
    DEC = "DEC"
    DEC_U = "DEC-U"
    DEC_MAJ = "DEC-MAJ"
    DEC_SPLIT = "DEC-SPLIT"
    DRAW = "DRAW"
    DRAW_U = "DRAW-U"
    DRAW_MAJ = "DRAW-MAJ"
    DRAW_SPLIT = "DRAW-SPLIT"
    DQ = "DQ"
    NC = "NC"
    FINISH = "FINISH"
    UNKNOWN = "UNKNOWN"


class Bookmaker(models.TextChoices):
    BET365 = "Bet365"
    PADDYPOWER = "PaddyPower"


class CardTier(models.TextChoices):
    MAIN_CARD = "MAIN_CARD"
    PRELIMS = "PRELIMS"
    EARLY_PRELIMS = "EARLY_PRELIMS"


class PredictionStatus(models.TextChoices):
    PENDING = "PENDING"
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"


class CustomCountries(Countries):
    override = {
        "ENG": "England",
        "SCT": "Scotland",
        "WLS": "Wales",
    }

    # Map country codes to flag URLs
    flags = {
        "ENG": "https://flagcdn.com/gb-eng.svg",
        "SCT": "https://flagcdn.com/gb-sct.svg",
        "WLS": "https://flagcdn.com/gb-wls.svg",
    }

    @classmethod
    def get_flag(cls, code):
        # Return custom flag if defined
        if code in cls.flags:
            return cls.flags[code]

        # Fallback to standard ISO flag
        if code:
            return f"https://flagcdn.com/{code.lower()}.svg"

        return None
