import re
from email.utils import parseaddr
from dateutil import parser as date_parser

ENTITY_PATTERNS = {
    'order_number': r'\bOrder\s*#?\s*(\d+)\b',
    'amount': r'\b(?:EUR|€|USD|\$)?\s?([0-9]+(?:\.[0-9]{1,2})?)\b',
    'date': r'\b(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\b',
    'product_code': r'\bPROD-\d+\b',
}

def extract_entities(text):
    entities = {}
    for key, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            entities[key] = matches
    # Extract names (simple heuristic)
    name_matches = re.findall(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text)
    if name_matches:
        entities['names'] = name_matches
    return entities

def extract_dates(text):
    dates = []
    for match in re.findall(ENTITY_PATTERNS['date'], text):
        try:
            dt = date_parser.parse(match, dayfirst=True, fuzzy=True)
            dates.append(dt)
        except Exception:
            continue
    return dates

def normalize_email_address(email):
    name, addr = parseaddr(email)
    return addr.lower() 