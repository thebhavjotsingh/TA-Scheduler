"""
Data parsing functions for CSV files containing TA availability and requirements.
"""
import os
import re
import pandas as pd
from ..utils.time_utils import convert_hour, convert_24_to_12_hour


def parse_max_hours(file_path: str):
    """
    Load the maximum hours each TA is hired for from MAX_FILE.

    Args:
        file_path (str): Path to the CSV file containing TA max hours data.

    Returns:
        employees (list): List of TA names.
        max_hours (dict): Mapping from TA name to hours hired for.

    Raises:
        FileNotFoundError: If file is missing.
        ValueError: If required columns are absent.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"'{file_path}' not found.")
    df = pd.read_csv(file_path)
    required = {'TA', 'Hired for'}
    if not required.issubset(df.columns):
        raise ValueError(f"'{file_path}' must contain columns: {required}.")

    # Extract TA names and their corresponding max hours
    employees = df['TA'].astype(str).tolist()
    max_hours = df.set_index('TA')['Hired for'].to_dict()
    return employees, max_hours


def parse_responses(file_path: str, employees: list):
    """
    Parse RESP_FILE to build hourly availability for each TA.
    Now handles unavailability columns instead of availability.

    Args:
        file_path (str): Path to the responses CSV file.
        employees (list): List of expected TA names.

    Returns:
        availability (dict): Mapping TA name to a DataFrame of availability.
        missing (list): List of TAs with no response record.

    Raises:
        FileNotFoundError: If file is missing.
        ValueError: If file is misformatted.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"'{file_path}' not found.")
    df = pd.read_csv(file_path)
    if 'Name' not in df.columns:
        raise ValueError("'Name' column missing in responses.")

    # Identify unavailability columns by pattern matching
    pattern = r' \[(\d+)(am|pm) to (\d+)(am|pm).*?\]'  # More flexible pattern to handle trailing spaces
    slot_infos = []
    for col in df.columns:
        m = re.match(pattern, col)
        if m:
            start = convert_hour(m.group(1), m.group(2))
            end = convert_hour(m.group(3), m.group(4))
            slot_infos.append({'col': col, 'start': start, 'end': end})
    if not slot_infos:
        raise ValueError("No unavailability columns detected.")

    # Gather unique days from all unavailability entries
    days = set()
    for info in slot_infos:
        for entry in df[info['col']].dropna().astype(str):
            days.update(d.strip() for d in entry.split(','))

    availability = {}
    missing = []
    # Build a boolean DataFrame for each TA indicating available hours
    for ta in employees:
        sub = df[df['Name'] == ta]
        if sub.empty:
            missing.append(ta)
            continue
        row = sub.iloc[0]
        df_av = pd.DataFrame({'Hour': [info['start'] for info in slot_infos]})
        for d in days:
            df_av[d] = True  # Default to available (True)
        for info in slot_infos:
            val = row.get(info['col'], '')
            if pd.isna(val) or not isinstance(val, str):
                continue
            for d in (x.strip() for x in val.split(',')):
                if d in days:
                    df_av.loc[df_av['Hour'] == info['start'], d] = False  # Mark as unavailable (False)
        availability[ta] = df_av
    return availability, missing


def parse_requirements(file_path: str):
    """
    Load lab section requirements from REQ_FILE.

    Args:
        file_path (str): Path to the requirements CSV file.

    Returns:
        slots (list): Each dict has keys: id, section, day, start, end, required.

    Raises:
        FileNotFoundError: If file is missing.
        ValueError: If required columns are absent.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"'{file_path}' not found.")
    df = pd.read_csv(file_path)
    req_cols = {'Day', 'Start', 'End', 'Required'}
    if not req_cols.issubset(df.columns):
        raise ValueError(f"'{file_path}' missing columns: {req_cols}.")

    slots = []
    for idx, row in df.iterrows():
        s, e = row['Start'], row['End']
        required = int(row['Required'])
        
        # Skip slots with zero requirements
        if required == 0:
            print(f"Skipping slot {row.get('Lab Section', idx)} with 0 required TAs")
            continue
            
        # Validate numeric start/end and logical ordering
        if not (isinstance(s, (int, float)) and isinstance(e, (int, float)) and s < e):
            print(f"Warning: Skipping invalid slot at row {idx}.")
            continue
        slots.append({
            'id': idx,
            'section': row.get('Lab Section', ''),
            'day': row['Day'],
            'start': s,
            'end': e,
            'required': required
        })
    return slots


def get_ta_unavailable_slots(ta_row: pd.Series, ta_data: pd.DataFrame) -> dict:
    """
    Extract unavailable time slots for a single TA in the format needed by schedule generator.
    
    Args:
        ta_row: Single row from the responses DataFrame for one TA
        ta_data: The full responses DataFrame (needed for column structure)
        
    Returns:
        dict: {time_slot: [list_of_unavailable_days]}
    """
    unavailable_slots = {}
    
    # Use the same pattern as parse_responses for consistency
    pattern = r' \[(\d+)(am|pm) to (\d+)(am|pm).*?\]'
    
    for col in ta_data.columns:
        match = re.match(pattern, col)
        if match:
            start_hour = convert_hour(match.group(1), match.group(2))
            end_hour = convert_hour(match.group(3), match.group(4))
            time_slot = f"{start_hour}-{end_hour}"
            
            # Get the unavailable days for this time slot
            value = ta_row[col]
            if pd.notna(value) and str(value).strip():
                # Split by comma and clean up the days
                unavailable_days = [day.strip() for day in str(value).split(',') if day.strip()]
                if unavailable_days:
                    unavailable_slots[time_slot] = unavailable_days
    
    return unavailable_slots


def is_available(ta_name: str, slot_day: str, slot_start_hour: int, slot_end_hour: int, ta_data: pd.DataFrame) -> bool:
    """
    Check if a TA is available for every hour in a given time range on a specific day.
    This function interprets the CSV as UNAVAILABILITY data (presence = unavailable).

    Args:
        ta_name (str): Name of the TA
        slot_day (str): Day name (e.g., 'Tuesday')
        slot_start_hour (int): Start hour in 24-hour format
        slot_end_hour (int): End hour in 24-hour format
        ta_data (pd.DataFrame): DataFrame with TA availability responses

    Returns:
        bool: True if available for all hours in the interval; False otherwise.
    """
    ta_info = ta_data[ta_data['Name'] == ta_name]
    if ta_info.empty:
        return False
    
    ta_row = ta_info.iloc[0]
    
    # For multi-hour slots, check availability for each hour
    current_hour = slot_start_hour
    while current_hour < slot_end_hour:
        next_hour = current_hour + 1
        
        # Create the time range pattern for this hour
        current_str = convert_24_to_12_hour(current_hour)
        next_str = convert_24_to_12_hour(next_hour)
        
        # Look for column matching this hour range  
        hour_is_available = True  # Default to available
        for col in ta_data.columns:
            # More robust matching - remove all spaces and compare
            col_normalized = re.sub(r'\s+', '', col)
            target_normalized = re.sub(r'\s+', '', f"[{current_str}to{next_str}]")
            
            if target_normalized in col_normalized:
                value = ta_row[col]
                # If the day is listed in this UNAVAILABILITY column, TA is NOT available
                if pd.notna(value) and slot_day in str(value):
                    hour_is_available = False
                break
        
        # If any hour is unavailable, the whole slot is unavailable
        if not hour_is_available:
            return False
        
        current_hour = next_hour
    
    return True
