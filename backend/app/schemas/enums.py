from enum import Enum

class Difficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    UNKNOWN = "Unknown"
