# Agent Traveler

* Designed to work with you LLM, to help travelers with their trips,
So the idea is to give an accurate or idea of a trip, and the agentl will help you
to clarify ideas, show you options.

Is not going to schedule or pay the trip, the idea is just to give an accurate report
of the trip, and the user can use it to plan their trip.


## How It Works: Your Travel Team

The planner uses specialized helpers to research each part of your journey:

* **The Trip Coordinator (`.agents/agents/travel-supervisor.md`)**: Think of this as your main travel guide. It listens to what kind of trip you want, conducts an interactive **Spec-Driven Development (SDD)** interview to formulate a formal `trip-spec` (lodging type/room/bathroom/stars/price, cities/places, preferred weather, dates), organizes the planning steps, and combines all findings into one clear, easy-to-read travel report.

* **Visa & Border Checker (`.agents/agents/cancilleria-scanner.md` & `.agents/skills/cancilleria-country-policy`)**: Border rules can be tricky. This agent checks official entry rules, visas, and stay limits specifically for travelers with Colombian passports so you never have surprises at immigration.

* **Route & Destination Explorer (`.agents/agents/destination-researcher.md` & `.agents/skills/travel-route-mapping`)**: The map builder. It organizes your stops in a logical order, suggests authentic cultural sights, and creates clickable Google Maps routes connecting your journey.

* **Weather & Transport Guide (`.agents/agents/weather-transport-researcher.md`)**: Traveling to unfamiliar climates can be challenging. This agent checks seasonal weather, evaluates alignment with your preferred climate, tells you what to pack, and explains how to get around each city (trains, buses, metro, and reliable taxi apps).

* **Price & Budget Scout (`.agents/skills/travel-price-scouting`)**: Keeps your trip on budget. It looks up indicative prices for flights and accommodations (hostels, guesthouses, or hotels filtered by your exact room, bathroom, star, and price preferences) on Booking, Airbnb, and Kayak, always converting costs to Colombian Pesos (COP) using live exchange rates.

## Spec-Driven Development (SDD) Workflow
Before spending tokens or fetching external sites, the system enforces an SDD Gate:
1. **Interactive Interview**: Asks for accommodation style (hotel/hostel, private/shared room and bath, preferred stars, max nightly budget), target cities/landmarks, preferred weather, and trip dates.
2. **Validated `trip-spec`**: Freezes the formal specification contract defined in [`.agents/specs/trip-spec-schema.md`](.agents/specs/trip-spec-schema.md).
3. **Execution**: Downstream specialist agents execute their tasks anchored to the validated spec.

## Roadmap & TODOs
* [x] **Spec-Driven Development (SDD)**: Implemented interactive interview protocol and validated `trip-spec` schema contract ([`.agents/specs/trip-spec-schema.md`](.agents/specs/trip-spec-schema.md)).
* [ ] **Agent Evals & Specs Tests**: Build automated spec/eval test suites using the Gemini SDK and Antigravity to validate the usage, (TBD How to create the test?)
* [ ] **ADK Workflow Migration**: Evaluate the same approach using Google ADK (Agent Development Kit) for deterministic state machines, typed schemas, and session checkpointing. 