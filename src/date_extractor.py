import re
from datetime import datetime

def extract_date(text):
    """
    Extract and validate date from transcribed text.
    Returns standardized date string in YYYY-MM-DD format.
    """
    # Common date patterns
    date_patterns = [
        r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',  # YYYY-MM-DD
        r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',  # DD-MM-YYYY
        r'\b(\w+)\s+(\d{1,2}),?\s+(\d{4})\b',      # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            for match in matches:
                try:
                    # Convert month name to number if necessary
                    if len(match[0]) > 2:  # Likely a month name
                        date_obj = datetime.strptime(f"{match[0]} {match[1]} {match[2]}", "%B %d %Y")
                    else:
                        # Assume YYYY-MM-DD format
                        date_obj = datetime.strptime(f"{match[0]}-{match[1]}-{match[2]}", "%Y-%m-%d")
                    
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
    
    raise ValueError("No valid date found in the transcribed text")
