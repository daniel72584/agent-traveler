# Agent Traveler Orchestration Rule

This repository operates as an intelligent travel-planning system tailored for travelers holding ordinary Colombian passports.

## Mandatory Orchestration Entrypoint

Whenever the user submits a travel-planning query, route request, trip idea, or destination inquiry:

1. **Primary Supervisor First**:
   - You MUST consult and follow the orchestration protocol defined in [.agents/agents/travel-supervisor.md](.agents/agents/travel-supervisor.md) as the initial router and coordinator.
   - Do NOT jump directly into ad-hoc price scouting, lodging research, or mapping skills without following the supervisor's sequential steps.

2. **Sequential Steps Workflow**:
   - **Step 1 (SDD Trip-Spec Interview & Validation Gate)**:
     - Formulate a validated `trip-spec` (defined in [.agents/specs/trip-spec-schema.md](.agents/specs/trip-spec-schema.md)) before launching deep research.
     - If the user's initial inquiry is incomplete, trigger the interactive **SDD Interview** to gather:
       1. **Accommodation**: Kind of hotel/hostel, private room vs. shared dorm, private vs. shared bathroom, preferred stars, and max nightly price cap.
       2. **Places & Cities**: Target cities, regions, and must-see places to visit.
       3. **Preferred Weather**: Climate preferences (warm, mild, cool, snow, avoiding rain).
       4. **Timing & Profile**: Travel dates/month, duration, departure hub in Colombia (BOG/MDE), and travel purpose (tourism/work/study).
     - Use [.agents/agents/destination-researcher.md](.agents/agents/destination-researcher.md) to extract and structure the validated `trip-spec` contract.
   - **Step 2 (Visa & Legal Feasibility)**:
     - Run entry requirement verification using [.agents/agents/cancilleria-scanner.md](.agents/agents/cancilleria-scanner.md) and the [travel-requirements](.agents/skills/travel-requirements/SKILL.md) / [cancilleria-country-policy](.agents/skills/cancilleria-country-policy/SKILL.md) skill for Colombian citizens.
     - *Hard stop*: If entry is not feasible, alert the traveler before researching lodging or attractions.
   - **Step 3 (Places, Culture & Route Mapping)**:
     - Use [travel-route-mapping](.agents/skills/travel-route-mapping/SKILL.md) and [.agents/agents/weather-transport-researcher.md](.agents/agents/weather-transport-researcher.md) for clean Google Maps routes, local sights, cultural highlights, and climate/packing guidance.
   - **Step 4 (Flights & Transit Connections)**:
     - Analyze outbound corridors from Colombia (BOG El Dorado / MDE José María Córdova) and flag transit visa requirements for layovers (US, UK, Schengen, etc.).
   - **Step 5 (Price Scouting & Live Currency)**:
     - Activate [travel-price-scouting](.agents/skills/travel-price-scouting/SKILL.md) to scout indicative ranges on Booking/Airbnb/Kayak.
     - Always fetch live exchange rates (USD/EUR ↔ COP) with timestamps; never invent rates or prices.

3. **Output Format**:
   - Synthesize all findings into the unified report structure specified in [.agents/agents/travel-supervisor.md](.agents/agents/travel-supervisor.md#final-output-structure).
