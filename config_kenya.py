"""
Kenyan market data for calculators.
Update these values as prices and rates change.

Last updated: 2026-10
"""

# ============ FUEL & ENERGY ============

# Petrol and diesel prices in Kenya (KES per litre). Source: EPRA monthly review.
PETROL_PRICE_KES = 190.00
DIESEL_PRICE_KES = 180.00

# Electricity tariff for EV charging (KES per kWh).
# Domestic rate from KPLC. Adjust based on your actual tariff tier.
ELECTRICITY_PRICE_KES = 27.00

# ============ VEHICLE CONSUMPTION ============

# Typical consumption for each vehicle type.
# ICE values in L/100km, EV in kWh/100km.

# Petrol sedan (e.g. Toyota Axio, Nissan Note)
PETROL_SEDAN_L_PER_100KM = 7.5

# Petrol SUV (e.g. Toyota Harrier, Nissan X-Trail)
PETROL_SUV_L_PER_100KM = 10.5

# Diesel pickup (e.g. Toyota Hilux, Isuzu D-Max)
DIESEL_PICKUP_L_PER_100KM = 9.0

# Electric car (typical consumption, Kenyan conditions)
EV_KWH_PER_100KM = 17.0

# ============ MAINTENANCE COSTS (KES per 10,000 km) ============

# ICE vehicles: oil changes, filters, belts, wear items, occasional repairs
ICE_MAINTENANCE_PER_10K_KM = 25_000

# EV vehicles: far fewer moving parts — no oil, no belts, minimal wear on brakes
EV_MAINTENANCE_PER_10K_KM = 8_000

# ============ INSURANCE ============

# Comprehensive insurance as % of vehicle value (annual)
INSURANCE_RATE_COMPREHENSIVE = 0.040

# ============ DEPRECIATION ============

# Annual depreciation rate (as decimal of remaining value)
# ICE vehicles depreciate faster in Kenya due to import age rules.
ICE_ANNUAL_DEPRECIATION = 0.12
EV_ANNUAL_DEPRECIATION = 0.10

# ============ NOTES ============
# These are indicative values based on Kenyan market conditions.
# Actual costs vary by vehicle, driver, and location.
# Update quarterly or when major price changes occur.




# ============ ROUTE COST ESTIMATOR ============

# Known toll costs on Kenyan highways (KES per passenger car).
# Update as toll rates change.
KENYAN_TOLLS = {
    'nairobi-mombasa': {
        'name': 'Nairobi – Mombasa (A109)',
        'cost_kes': 0,  # No tolls on this route currently
    },
    'nairobi-naivasha': {
        'name': 'Nairobi – Naivasha (A104)',
        'cost_kes': 0,
    },
    'nairobi-nakuru': {
        'name': 'Nairobi – Nakuru (A104)',
        'cost_kes': 0,
    },
    'nairobi-kericho': {
        'name': 'Nairobi – Kericho',
        'cost_kes': 0,
    },
    # Add more as toll infrastructure develops.
    # Note: Kenya currently has minimal toll roads for private cars.
}

# Average additional costs (Kes)
ROUTE_EXTRA_COST_PER_HOUR_KES = 0  # Driver time value — optional, default 0



# ============ MAINTENANCE COST ESTIMATOR ============

# Typical service intervals (in km) for each component.
# These drive how often each item is replaced.
SERVICE_INTERVALS_KM = {
    'oil_and_filter': 10_000,
    'air_filter': 20_000,
    'brake_pads_front': 40_000,
    'brake_pads_rear': 60_000,
    'tyres_set': 50_000,
    'battery': 50_000,
    'suspension_check': 40_000,
    'transmission_fluid': 80_000,
    'coolant_flush': 60_000,
}

# Typical replacement costs (KES) for each item, including labor.
# These override the shop product prices when the product isn't in the catalog.
# ICE vehicles: full range of items.
# EV vehicles: drastically reduced (no oil, no belts, minimal brake wear).
MAINTENANCE_COSTS_ICE = {
    'oil_and_filter': 6_500,
    'air_filter': 2_500,
    'brake_pads_front': 8_500,
    'brake_pads_rear': 7_500,
    'tyres_set': 45_000,
    'battery': 12_000,
    'suspension_check': 6_000,
    'transmission_fluid': 8_500,
    'coolant_flush': 4_500,
}

MAINTENANCE_COSTS_EV = {
    'oil_and_filter': 0,           # No engine oil in an EV
    'air_filter': 2_000,           # Cabin air filter only
    'brake_pads_front': 3_500,     # Regenerative braking reduces wear
    'brake_pads_rear': 3_000,
    'tyres_set': 45_000,           # Same tyres, same cost
    'battery': 0,                  # EV battery is different — not comparable
    'suspension_check': 5_000,
    'transmission_fluid': 0,       # No traditional transmission
    'coolant_flush': 3_000,        # Battery thermal management fluid
}

# Additional cost multipliers by vehicle age (as decimal)
# Older vehicles need more unplanned repairs.
VEHICLE_AGE_MULTIPLIER = {
    '0-3': 1.00,   # New vehicles — mostly warranty work
    '4-7': 1.20,   # Moderate wear
    '8-12': 1.50,  # Significant maintenance
    '13+': 2.00,   # High maintenance
}