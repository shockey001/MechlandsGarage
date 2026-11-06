"""
VIN decoding service using NHTSA vPIC API.
Free, no API key required.
"""

import re
import requests


NHTSA_URL = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json'


class VinServiceError(Exception):
    """Raised when VIN decoding fails."""
    pass


def validate_vin(vin):
    """
    Check VIN format.
    Real VINs are 17 characters, letters (except I, O, Q) and digits.
    Some JDM chassis codes are shorter — we accept 9–17.
    """
    vin = (vin or '').strip().upper()
    if not vin:
        raise VinServiceError('Please enter a VIN.')

    if len(vin) < 9 or len(vin) > 17:
        raise VinServiceError('VIN should be 17 characters (or 9+ for older JDM chassis numbers).')

    if not re.match(r'^[A-HJ-NPR-Z0-9]+$', vin):
        raise VinServiceError('VIN contains invalid characters. Valid characters are A–Z (except I, O, Q) and 0–9.')

    return vin


# Friendly labels for the most useful fields returned by NHTSA
FIELD_LABELS = {
    'Make': 'Make',
    'Model': 'Model',
    'ModelYear': 'Model Year',
    'Series': 'Series',
    'Trim': 'Trim',
    'BodyClass': 'Body Type',
    'VehicleType': 'Vehicle Type',
    'EngineCylinders': 'Engine Cylinders',
    'DisplacementCC': 'Engine Displacement (cc)',
    'DisplacementL': 'Engine Displacement (L)',
    'EngineHP': 'Horsepower',
    'FuelTypePrimary': 'Fuel Type',
    'DriveType': 'Drive Type',
    'TransmissionStyle': 'Transmission',
    'PlantCountry': 'Manufactured In',
    'PlantCity': 'Plant City',
    'Manufacturer': 'Manufacturer',
    'Doors': 'Doors',
    'SeatBeltsAll': 'Seat Belts',
    'GVWR': 'Gross Vehicle Weight Rating',
    'Note': 'Notes',
}


def decode_vin(vin):
    """
    Decode a VIN via NHTSA vPIC.
    Returns a dict with 'fields' (label → value) and 'raw' (full response).
    Raises VinServiceError on failure.
    """
    vin = validate_vin(vin)

    try:
        resp = requests.get(NHTSA_URL.format(vin=vin), timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise VinServiceError(f'Could not reach the VIN service: {e}')

    results = data.get('Results', [])
    if not results:
        raise VinServiceError('No data returned for that VIN.')

    record = results[0]

    # Check for error codes
    error_code = record.get('ErrorCode', '')
    error_text = record.get('ErrorText', '')

    # Common successful codes: 0 = clean, 1 = some minor issues, 6 = clean with details
    # If almost nothing was decoded AND there's an error, treat as failure
    if error_code not in ('0', '1', '6', '') and 'invalid' in error_text.lower():
        raise VinServiceError('That VIN could not be decoded. Please check it and try again.')

    # Build a clean field list — only non-empty values
    fields = {}
    for key, label in FIELD_LABELS.items():
        value = record.get(key, '').strip() if record.get(key) else ''
        # Skip empty values and "0" strings (NHTSA returns "0" for missing numbers)
        if value and value != '0' and value.lower() not in ('not applicable', 'unknown'):
            fields[label] = value

    if not fields:
        raise VinServiceError('The VIN service returned no usable data. Try a different VIN.')

    return {
        'vin': vin,
        'fields': fields,
        'raw': record,
    }