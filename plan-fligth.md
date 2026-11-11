# Flight Ticket Searcher Agent — Implementation Plan (`plan-fligth.md`)

This document tracks the phased implementation of the **Ticket Searcher Agent (`ticket-searcher`)** and its 9 dedicated flight-search skills. Each phase is designed to be implemented and verified independently in its own chat session.

---

## Overview & Goal

Build a specialized **Ticket Searcher Agent** tailored for Colombian travelers (ordinary passport holders) that:
1. Accepts a structured route request (`from` origin, `to` destination, `dates`, `passengers`, `cabin_class`, `baggage`).
2. Researches flights across **9 dedicated provider skills** (aggregators, OTAs, hidden-city tools, and key airlines).
3. Ranks and returns the **Top 5 Flights** optimized by **Total Price (USD & live COP)** and **Layover Time (`layoff time`)**, while enforcing Colombian passport transit-visa feasibility checks (US C1/B1/B2, UK DATV, Schengen transit rules, and self-transfer/hidden-city caveats).
4. Runs natively as an **Antigravity Markdown Agent** ([`.agents/agents/ticket-searcher.md`](.agents/agents/ticket-searcher.md)) orchestrating the 9 `.agents/skills/*-flight-search` skills directly in Antigravity (no ADK microservice needed for tickets).
5. Saves every Antigravity execution (Markdown report + JSON execution history across all 9 providers) inside the **`run_fligth_agent/`** directory.

---

## Phase 1: Update `README.md` (Architecture & Roadmap Documentation)
- **Status**: `[x] Completed` (Initial Roadmap linked) / `[ ] Final Architecture Update after Phase 4`
- **Scope**:
  1. Add the **Ticket Searcher Agent** and its 9 flight-provider skills to the **Roadmap ("Work to Do")** section in [`README.md`](./README.md).
  2. Link [`plan-fligth.md`](./plan-fligth.md) as the master tracking document.
  3. Update the **Architecture** and **ADK Execution** sections in `README.md` as each phase lands.

---

## Phase 2: Create the 9 Flight Provider Skills (`.agents/skills/`)
- **Status**: `[x] Completed`
- **Scope**:
  Create one self-contained `SKILL.md` per flight search page/airline under `.agents/skills/`. Every skill must normalize URLs (stripping tracking parameters such as `gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`), enforce read-only research guardrails, and output a standardized flight candidate table.

### Provider Skills to Create

| # | Skill Path | Provider & Clean Base URL | Core Research Capability |
|---|---|---|---|
| 1 | `.agents/skills/google-flights-search/SKILL.md` | **Google Flights** (`https://www.google.com/travel/flights`) | Best overall for speed, interactive explore maps, flexible date grids, and price tracking alerts. |
| 2 | `.agents/skills/kayak-flight-search/SKILL.md` | **KAYAK** (`https://www.kayak.com/flights` / `https://www.kayak.com.co/flights`) | Color-coded price calendars, nearby airport expansions, hacker fares, and smart filters. |
| 3 | `.agents/skills/skyscanner-flight-search/SKILL.md` | **Skyscanner** (`https://www.skyscanner.net/`) | Searching "Everywhere" to find cheap entry hubs and comparing budget vs. full-service airlines. |
| 4 | `.agents/skills/momondo-flight-search/SKILL.md` | **Momondo** (`https://www.momondo.com/`) | Deep cross-OTA price comparisons across hundreds of sites, price calendars, and hidden-fee transparency. |
| 5 | `.agents/skills/kiwi-flight-search/SKILL.md` | **Kiwi.com** (`https://www.kiwi.com/en/cheap-flights/`) | Virtual interlining, self-transfer combinations across non-partner carriers, and multi-city nomad routes. |
| 6 | `.agents/skills/skiplagged-flight-search/SKILL.md` | **Skiplagged** (`https://skiplagged.com/`) | "Hidden-city" layover ticketing hacks *(must enforce strict caveats: carry-on only, one-way only, airline cancellation risks, and visa checks for the final ticketed destination)*. |
| 7 | `.agents/skills/airfrance-flight-search/SKILL.md` | **Air France** (`https://wwws.airfrance.com.co/` / `https://www.airfrance.com/`) | Direct transatlantic corridor from Colombia (`BOG -> CDG`) and SkyTeam intra-European connections. |
| 8 | `.agents/skills/avianca-flight-search/SKILL.md` | **Avianca** (`https://www.avianca.com/`) | Primary Colombian flag carrier from `BOG` / `MDE` with direct corridors across the Americas and Europe (`MAD`, `LHR`, `BCN`). |
| 9 | `.agents/skills/ryanair-flight-search/SKILL.md` | **Ryanair** (`https://www.ryanair.com/gb/en`) | Ultra-low-cost intra-European point-to-point connector flights *(must flag strict cabin baggage dimensions, secondary airports, and non-protected self-transfers)*. |

### Standard Skill Contract (Required in all 9 `SKILL.md` files)
- **Inputs**: `origin` (`from`), `destination` (`to`), `departure_date`, `return_date` (optional/round-trip), `passengers`, `cabin_class`, `baggage_type` (`personal_item`, `carry_on`, `checked`).
- **Outputs**: Standardized candidate records containing:
  - `provider`: Skill/site name
  - `airlines`: Operating carrier(s)
  - `route`: `Origin -> Layover Hub(s) -> Destination`
  - `layover_time`: Layover duration per stop (`h/m`) and total trip duration
  - `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` / `EUR-COP` rate with timestamp
  - `baggage_and_fee_notes`: Included bags vs. extra fees
  - `transit_visa_warning`: Colombian passport transit alert for layover hubs
  - `search_url`: Clean parameterized deep link

---

## Phase 3: Define the Ticket Searcher Markdown Agent (`.agents/agents/ticket-searcher.md`)
- **Status**: `[x] Completed`
- **Scope**:
  1. Create `.agents/agents/ticket-searcher.md` defining the specialist agent's persona, mandatory verification rules, input validation gate (`from`, `to`, `dates`), and orchestration across the 9 skills.
  2. Define the **Top 5 Flights Ranking Rubric (Price + Layover Time)**:
     - **Price Score (50%)**: Total fare in USD and live COP (accounting for baggage and hidden OTA/carrier fees).
     - **Layover Time (`layoff time`) Score (35%)**: Optimal connection window (`1.5h–3.5h` protected transfer); penalize risky `< 1.5h` connections, self-transfers requiring immigration clearance, or exhausting `> 6h` layovers.
     - **Colombian Transit Visa & Ticketing Safety (15% + Hard Gate)**: Flag or filter out connections through hubs requiring a visa not held by the traveler (e.g., US `C1/B1/B2`, UK `DATV`, Schengen `ATV`/entry for self-transfers), and clearly label `Skiplagged` hidden-city risks.
  3. Define the **Top 5 Flights Output Table** format (`Rank #1–#5`, `Source Skill`, `Airline & Route`, `Price (USD / Live COP)`, `Layover Time & Hub`, `Total Duration`, `Caveats & Visa Notes`, `Clean Link`).
  4. Wire `@ticket-searcher` into [`.agents/agents/travel-supervisor.md`](.agents/agents/travel-supervisor.md) (Step 4: Flights & Transit Connections) and [`AGENTS.md`](./AGENTS.md).

---

## Phase 4: Native Antigravity Execution & Saved Runs (`run_fligth_agent/`)
- **Status**: `[x] Completed`
- **Scope**:
  Run the Ticket Searcher Agent (`.agents/agents/ticket-searcher.md`) and its 9 skills (`.agents/skills/*-flight-search/SKILL.md`) directly inside **Antigravity** (using live web research and skill workflows rather than ADK) and persist every execution inside **`run_fligth_agent/`**:
  1. `run_fligth_agent/run_<N>_<route_slug>.md` — Per-case saved Markdown execution report.
  2. `run_fligth_agent/latest_execution.md` — Latest complete Markdown report with the Top 5 Ranked Flights table and all 9 provider skill snapshots.
  3. `run_fligth_agent/executions.json` — Structured JSON log of each Antigravity execution (query parameters, live `USD-COP` rate, all 9 provider candidates, and Top 5 ranked flights).
  4. Re-index the repository via Grafeando (`index_codebase(".")`).

