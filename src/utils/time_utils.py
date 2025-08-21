"""
Utility functions for time conversion and data processing.
"""


def convert_hour(hour_str: str, ampm: str) -> int:
    """
    Convert a 12-hour clock time with AM/PM to a 24-hour integer representation.

    Args:
        hour_str (str): Hour component as a string (e.g., '8').
        ampm (str): 'AM' or 'PM' indicator (case-insensitive).

    Returns:
        int: Hour in 24-hour format (0-23).

    Raises:
        ValueError: If the hour_str cannot be converted to int.
    """
    h = int(hour_str)
    if ampm.lower() == 'am':
        return 0 if h == 12 else h
    # For PM times, add 12 hours unless it's 12 PM
    return 12 if h == 12 else h + 12


def convert_24_to_12_hour(hour_24: int) -> str:
    """Convert 24-hour time to 12-hour format string"""
    if hour_24 == 0:
        return "12am"
    elif hour_24 < 12:
        return f"{hour_24}am"
    elif hour_24 == 12:
        return "12pm"
    else:
        return f"{hour_24-12}pm"


def slots_overlap(slot1: dict, slot2: dict) -> bool:
    """
    Check if two slots overlap in time on the same day.

    Args:
        slot1 (dict): First slot with keys 'day', 'start', 'end'
        slot2 (dict): Second slot with keys 'day', 'start', 'end'

    Returns:
        bool: True if slots overlap (same day and overlapping times)
    """
    if slot1['day'] != slot2['day']:
        return False
    
    # Check if time ranges overlap: slots overlap if start1 < end2 and start2 < end1
    return slot1['start'] < slot2['end'] and slot2['start'] < slot1['end']


def get_slots_by_day(slots: list) -> dict:
    """
    Group slots by day for easier daily hour calculation.

    Args:
        slots (list): List of slot dictionaries

    Returns:
        dict: Mapping from day to list of slots on that day
    """
    slots_by_day = {}
    for slot in slots:
        day = slot['day']
        if day not in slots_by_day:
            slots_by_day[day] = []
        slots_by_day[day].append(slot)
    return slots_by_day
