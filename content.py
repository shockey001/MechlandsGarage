"""
Content data for Mechlands Garage.
Edit these lists to add/update blog posts, events, and gallery items.
"""

# ============ BLOG POSTS ============
# Each post: slug (URL-safe), title, date, excerpt, and full body (markdown-style line breaks)
BLOG_POSTS = [
    {
        "slug": "why-ev-conversion-makes-sense-in-kenya",
        "title": "Why EV Conversion Makes Sense in Kenya Right Now",
        "date": "2026-09-15",
        "excerpt": "Fuel costs are rising, EV imports are duty-exempt, and the technology has matured. Here's why 2026 is the year conversion starts to make economic sense for Kenyan motorists.",
        "body": """
Kenya's fuel prices have climbed steadily over the past three years. At the same time, the government has exempted the first 100,000 imported EVs from duty, and charging infrastructure is expanding across Nairobi.

For many Kenyan motorists, the question is no longer whether to go electric — it's how. New EVs are still expensive. But converting an existing petrol or diesel vehicle to electric is a different calculation entirely.

**What conversion actually involves**

A typical ICE-to-EV conversion replaces the engine, fuel system, and exhaust with an electric motor, battery pack, motor controller, and battery management system. The transmission may be retained, replaced, or removed depending on the design.

**The economics**

A full conversion currently costs between KES 950,000 and 2,000,000 depending on battery size and motor choice. Set that against the lifetime fuel and maintenance savings of a vehicle you already own, and the payback period for high-mileage vehicles can be surprisingly short.

**The right candidates**

Not every vehicle is a good conversion candidate. Heavier vehicles need larger batteries. Older vehicles with structural rust aren't worth the investment. The best candidates are typically 5–15 year old vehicles with solid bodies and high annual mileage.

If you're considering conversion, the first step is a feasibility assessment — not a commitment.
""",
    },
    {
        "slug": "diagnosing-electrical-faults-modern-cars",
        "title": "Diagnosing Electrical Faults in Modern Cars: A Practical Approach",
        "date": "2026-08-22",
        "excerpt": "Modern vehicles have dozens of ECUs and hundreds of sensors. Here's how we approach electrical diagnostics systematically — instead of swapping parts and hoping.",
        "body": """
The most common mistake in automotive electrical diagnostics is guessing. A car won't start, so the mechanic replaces the battery. Still won't start — replace the starter. Still won't start — replace the alternator. By the time the real fault is found, the owner has paid for three parts they didn't need.

At Mechlands Garage, we diagnose before we replace.

**Step 1: Scan for fault codes**

Every modern vehicle stores diagnostic trouble codes (DTCs) in its ECUs. An OBD2 scan is the starting point — but codes are clues, not conclusions. A "misfire on cylinder 3" code could be a spark plug, an injector, a coil pack, a wiring fault, or a compression issue.

**Step 2: Verify the circuit**

For electrical faults, we test the actual circuit. Is voltage reaching the component? Is the ground solid? Is resistance within spec? A multimeter and a wiring diagram solve more problems than any parts catalog.

**Step 3: Isolate the fault**

We narrow the problem to a specific component, connection, or wire. Only then do we quote a repair.

**Why this matters**

Systematic diagnosis saves customers money and builds trust. It's also the foundation for EV work — high-voltage systems demand the same discipline, with much higher stakes.
""",
    },
    {
        "slug": "what-to-check-before-buying-used-car-kenya",
        "title": "What to Check Before Buying a Used Car in Kenya",
        "date": "2026-07-10",
        "excerpt": "A pre-purchase inspection costs a few thousand shillings and can save you hundreds of thousands. Here's what we look at — and what you should too.",
        "body": """
Buying a used car in Kenya is a high-stakes decision. The market is full of vehicles with hidden problems — clocked odometers, accident damage that's been cosmetically repaired, and electrical gremlins that only show up weeks after purchase.

A professional pre-purchase inspection is the cheapest insurance you can buy.

**What we inspect**

- **Structural integrity:** Chassis alignment, panel gaps, welding marks that suggest accident repair
- **Engine health:** Compression test, oil analysis, coolant condition, leak inspection
- **Transmission:** Shift quality, fluid condition, fault codes
- **Electrical systems:** Battery health, alternator output, all electronics functioning
- **Suspension and brakes:** Wear patterns, alignment, bushing condition
- **Documentation:** VIN verification, service history, logbook authenticity

**What we deliver**

A written report with photos, an honest assessment of the vehicle's condition, and an estimated cost of any repairs needed. You make the decision — but you make it informed.

For vehicles priced above KES 500,000, an inspection is not optional. It's essential.
""",
    },
]


# ============ EVENTS ============
EVENTS = [
    {
        "slug": "ev-conversion-open-day",
        "title": "EV Conversion Open Day",
        "date": "2026-11-15",
        "location": "Mechlands Garage, Nairobi",
        "status": "upcoming",
        "description": "See a live ICE-to-EV conversion in progress. Meet the team, ask questions, and understand what conversion involves. Free entry, all welcome.",
    },
    {
        "slug": "fleet-ev-transition-workshop",
        "title": "Fleet EV Transition Workshop",
        "date": "2026-12-05",
        "location": "Nairobi (venue TBC)",
        "status": "upcoming",
        "description": "A half-day workshop for SME fleet operators considering the shift to electric vehicles. Cost modeling, pilot conversion options, and Q&A with our engineering team.",
    },
    {
        "slug": "mechlands-launch",
        "title": "Mechlands Garage Launch",
        "date": "2026-10-01",
        "location": "Mechlands Garage, Nairobi",
        "status": "past",
        "description": "The official opening of Mechlands Garage — a gathering of customers, partners, and supporters to mark the start of a new kind of workshop in Kenya.",
    },
]


# ============ GALLERY ============
# Each item: image (filename in static/images/gallery/), caption, category
# Categories used: 'ice', 'ev', 'tuning', 'engineering'
GALLERY_ITEMS = [
    {
        "image": "placeholder-1.jpg",
        "caption": "Engine diagnostics in progress",
        "category": "ice",
    },
    {
        "image": "placeholder-2.jpg",
        "caption": "High-voltage battery pack inspection",
        "category": "ev",
    },
    {
        "image": "placeholder-3.jpg",
        "caption": "Performance exhaust fabrication",
        "category": "tuning",
    },
    {
        "image": "placeholder-4.jpg",
        "caption": "Custom wiring harness build",
        "category": "engineering",
    },
    {
        "image": "placeholder-5.jpg",
        "caption": "Suspension rebuild",
        "category": "ice",
    },
    {
        "image": "placeholder-6.jpg",
        "caption": "Motor controller integration",
        "category": "ev",
    },
]


# ============ SHOP PRODUCTS ============
# Each product: id, category, name, description, price (or None for "request price")
# Categories: 'spares', 'tools', 'accessories'
SHOP_PRODUCTS = [
    # ---- SPARES ----
    {
        "id": "sp-001",
        "category": "spares",
        "name": "Oil Filter (Universal Fit)",
        "description": "High-quality oil filter compatible with most common petrol and diesel engines.",
        "price": 800,
    },
    {
        "id": "sp-002",
        "category": "spares",
        "name": "Brake Pad Set (Front)",
        "description": "Ceramic front brake pads, low dust and long life. Specify vehicle model at order.",
        "price": 3500,
    },
    {
        "id": "sp-003",
        "category": "spares",
        "name": "Spark Plug Set (4pc)",
        "description": "Iridium spark plugs for improved ignition and fuel economy.",
        "price": 2400,
    },
    {
        "id": "sp-004",
        "category": "spares",
        "name": "Air Filter",
        "description": "High-flow air filter for popular sedan and SUV models.",
        "price": 1500,
    },
    {
        "id": "sp-005",
        "category": "spares",
        "name": "Wiper Blade Pair",
        "description": "All-weather wiper blades. Specify length at order.",
        "price": 1200,
    },
    {
        "id": "sp-006",
        "category": "spares",
        "name": "Car Battery (Maintenance-Free)",
        "description": "Reliable sealed battery. Multiple sizes available — specify vehicle at order.",
        "price": None,
    },

    # ---- TOOLS ----
    {
        "id": "tl-001",
        "category": "tools",
        "name": "Socket Set (40pc)",
        "description": "Chrome vanadium socket set — metric and imperial, with ratchet and extensions.",
        "price": 6500,
    },
    {
        "id": "tl-002",
        "category": "tools",
        "name": "Hydraulic Trolley Jack (2T)",
        "description": "Low-profile 2-tonne hydraulic jack for safe vehicle lifting.",
        "price": 12000,
    },
    {
        "id": "tl-003",
        "category": "tools",
        "name": "OBD2 Diagnostic Scanner",
        "description": "Entry-level scanner for reading and clearing fault codes on most OBD2 vehicles.",
        "price": 8500,
    },
    {
        "id": "tl-004",
        "category": "tools",
        "name": "Torque Wrench",
        "description": "Precision torque wrench — essential for cylinder heads and wheel nuts.",
        "price": 5500,
    },
    {
        "id": "tl-005",
        "category": "tools",
        "name": "Digital Multimeter",
        "description": "For electrical diagnostics — voltage, resistance, continuity.",
        "price": 3000,
    },
    {
        "id": "tl-006",
        "category": "tools",
        "name": "Professional Diagnostic Kit",
        "description": "Advanced multi-brand diagnostic system. Contact us for pricing and demonstration.",
        "price": None,
    },

    # ---- ACCESSORIES ----
    {
        "id": "ac-001",
        "category": "accessories",
        "name": "Phone Mount (Universal)",
        "description": "Adjustable dashboard or vent phone mount with secure grip.",
        "price": 800,
    },
    {
        "id": "ac-002",
        "category": "accessories",
        "name": "Dash Cam (1080p)",
        "description": "Full HD dash camera with loop recording and night vision.",
        "price": 6500,
    },
    {
        "id": "ac-003",
        "category": "accessories",
        "name": "LED Headlight Kit",
        "description": "Bright, efficient LED upgrade. Specify bulb type at order.",
        "price": 4500,
    },
    {
        "id": "ac-004",
        "category": "accessories",
        "name": "Seat Cover Set",
        "description": "Durable, water-resistant seat covers. Specify vehicle and colour preference.",
        "price": 5500,
    },
    {
        "id": "ac-005",
        "category": "accessories",
        "name": "Floor Mat Set (Custom Fit)",
        "description": "Rubber floor mats — specify vehicle for exact fit.",
        "price": 3500,
    },
    {
        "id": "ac-006",
        "category": "accessories",
        "name": "Premium Roof Rack",
        "description": "Heavy-duty roof rack. Installation available at our workshop. Contact for sizing.",
        "price": None,
    },
]



# ============ CAREERS — OPEN POSITIONS ============
# Each position: slug (unique), title, department, location, type, description, requirements (list)
# status: "open" or "closed"
OPEN_POSITIONS = [
    {
        "slug": "auto-electrician",
        "title": "Auto Electrician",
        "department": "Workshop",
        "location": "Nairobi, Kenya",
        "type": "Full-time",
        "status": "open",
        "description": "We're looking for an experienced auto electrician to join our workshop team. You'll work on both ICE and EV electrical systems — from wiring faults to high-voltage diagnostics.",
        "requirements": [
            "3+ years hands-on automotive electrical experience",
            "Comfortable with OBD2 diagnostics and multimeter work",
            "Willing to train on high-voltage EV systems",
            "Strong attention to detail and safety protocols",
        ],
    },
    {
        "slug": "workshop-apprentice",
        "title": "Workshop Apprentice",
        "department": "Workshop",
        "location": "Nairobi, Kenya",
        "type": "Apprenticeship",
        "status": "open",
        "description": "An entry-level apprenticeship for someone who wants to learn the trade properly. You'll work alongside experienced technicians on real jobs — ICE repair today, EV conversion tomorrow.",
        "requirements": [
            "Genuine interest in automotive engineering",
            "Willingness to learn and follow instructions",
            "Basic mechanical or electrical knowledge is a plus",
            "Reliable and punctual",
        ],
    },
    {
        "slug": "sales-customer-care",
        "title": "Sales & Customer Care",
        "department": "Front Office",
        "location": "Nairobi, Kenya",
        "type": "Full-time",
        "status": "open",
        "description": "First point of contact for customers. You'll handle bookings, follow up on quotes, manage the shop order inbox, and help grow our customer base.",
        "requirements": [
            "Strong communication skills in English and Swahili",
            "Comfortable with WhatsApp, email, and basic spreadsheets",
            "Customer-service mindset — patient, clear, professional",
            "Interest in automotive or EV industry is a plus",
        ],
    },
]