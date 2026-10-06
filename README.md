# Agent Traveler

* Designed to work with you LLM, to help travelers with their trips,
So the idea is to give an accurate or idea of a trip, and the agentl will help you
to clarify ideas, show you options.

Is not going to schedule or pay the trip, the idea is just to give an accurate report
of the trip, and the user can use it to plan their trip.


## How It Works: Your Travel Team

The planner uses specialized helpers to research each part of your journey:

* **The Trip Coordinator (`.agents/agents/travel-supervisor.md`)**: Think of this as your main travel guide. It listens to what kind of trip you want, organizes the planning steps, and combines all findings into one clear, easy-to-read travel report.

* **Visa & Border Checker (`.agents/agents/cancilleria-scanner.md` & `.agents/skills/cancilleria-country-policy`)**: Border rules can be tricky. This agent checks official entry rules, visas, and stay limits specifically for travelers with Colombian passports so you never have surprises at immigration.

* **Route & Destination Explorer (`.agents/agents/destination-researcher.md` & `.agents/skills/travel-route-mapping`)**: The map builder. It organizes your stops in a logical order, suggests authentic cultural sights, and creates clickable Google Maps routes connecting your journey.

* **Weather & Transport Guide (`.agents/agents/weather-transport-researcher.md`)**: Traveling to unfamiliar climates can be challenging. This agent checks seasonal weather, tells you what to pack, and explains how to get around each city (trains, buses, metro, and reliable taxi apps).

* **Price & Budget Scout (`.agents/skills/travel-price-scouting`)**: Keeps your trip on budget. It looks up indicative prices for flights and accommodations (hostels, guesthouses, or hotels) on Booking, Airbnb, and Kayak, always converting costs to Colombian Pesos (COP) using live exchange rates.

## Roadmap & TODOs
* **Spec-Driven Development (SDD)**: Introduce an interactive interview step to formulate a validated `trip-spec` interview.
* **Agent Evals & Specs Tests**: Build automated spec/eval test suites using the Gemini SDK and Antigravity to validate the usage, (TBD How to create the test?)
* **ADK Workflow Migration**: Evaluate the same approach using Google ADK (Agent Development Kit) for deterministic state machines, typed schemas, and session checkpointing. 