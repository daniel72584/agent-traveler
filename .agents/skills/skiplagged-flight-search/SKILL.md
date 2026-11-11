---
name: skiplagged-flight-search
description: >-
  Researches read-only "hidden-city" layover ticketing opportunities and standard fares on Skiplagged (`https://skiplagged.com/`). Enforces mandatory caveats for Colombian travelers: carry-on/personal item only, one-way only, airline return-leg cancellation risks, and visa/entry eligibility required for BOTH the hidden-city layover hub and the final ticketed destination.
---

# Skiplagged Flight Search (`skiplagged-flight-search`)

Use this skill to research standard fares and "hidden-city" layover ticketing opportunities on **Skiplagged**, where the traveler disembarks at the layover city rather than flying the final leg of the ticket. Do not book, log in, or submit traveler details.

## Provider & Clean Base URL

- **Provider**: Skiplagged
- **Clean Base URL**: `https://skiplagged.com/`
- **Parameterized Search URL Pattern**:
  ```text
  https://skiplagged.com/flights/[ORIGIN]/[DESTINATION]/[DEPARTURE_DATE]
  ```
  *(Or `https://skiplagged.com/flights/[ORIGIN]/[DESTINATION]/[DEPARTURE_DATE]/[RETURN_DATE]` for standard round-trip comparisons.)*

### URL Normalization Rules
- Strip all tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `ref`).
- Never retain session identifiers or affiliate tracking tokens.

## Core Research Capabilities

1. **Hidden-City Layover Discovery**: Identifies when a ticket `Origin -> Target Destination (Layover) -> Final Ticketed City` is cheaper than a direct `Origin -> Target Destination` ticket.
2. **Standard Fare Comparison**: Also displays regular non-hidden-city flights alongside hidden-city options so travelers can compare the savings against the risks.

## Mandatory Hidden-City Guardrails & Colombian Passport Rules

Whenever a **hidden-city** fare from Skiplagged is surfaced, you **MUST** enforce and display all 5 caveats:
1. **Strictly No Checked Baggage (`personal_item` / `carry_on` only)**: Checked luggage (`checked`) will be tagged and flown to the final ticketed destination. Even with a full-size carry-on, gate-check enforcement on full flights can send your bag to the final city—under-seat backpack (`personal_item`) is safest.
2. **One-Way Only (Or Final Leg of Trip)**: The moment you skip a leg on a round-trip or multi-city ticket, the airline automatically cancels all remaining onward or return flights on that reservation.
3. **Visa & Entry Eligibility Required for the FINAL Ticketed Destination**: Airline check-in agents in Colombia (`BOG`/`MDE`) verify your passport and visa for the **final destination printed on the ticket** (plus any transit hubs). If the final ticketed city requires a visa you do not hold (e.g., a US, UK, or Canadian city), you will be denied boarding at origin!
4. **Irregular Operations (IRROPS) Re-Routing Risk**: In case of weather or mechanical delays, the airline is only contractually obligated to get you from `Origin` to the `Final Ticketed City` and may re-route you via a completely different hub, bypassing your intended layover city.
5. **Frequent Flyer & Airline Policy Risk**: Never attach a frequent-flyer loyalty number to a hidden-city ticket; airlines prohibit hidden-city ticketing in their Conditions of Carriage.

## Standard Skill Contract

### Required Inputs
- `origin` (`from`): Origin airport IATA code or city.
- `destination` (`to`): Intended destination airport IATA code or city.
- `departure_date`: Outbound date (`YYYY-MM-DD`).
- `return_date` *(optional)*: Return date (`YYYY-MM-DD`).
- `passengers`: Number of passengers (default `1`).
- `cabin_class`: `economy`, `premium_economy`, `business`, or `first` (default `economy`).
- `baggage_type`: `personal_item`, `carry_on`, or `checked` *(if `checked`, automatically disqualify hidden-city fares and only return standard fares from Skiplagged)*.

### Missing-Details Gate
If `origin`, `destination`, or `departure_date` is missing, prompt for the missing fields before running the search.

### Live Currency Conversion Rule
Convert USD/EUR fares to COP using the live rate from `https://www.google.com/finance/quote/USD-COP` or `https://api.exchangerate-api.com/v4/latest/USD` with fetch timestamp.

## Standardized Output Contract

```markdown
### Skiplagged Flight Candidates (`skiplagged-flight-search`)
- **Search URL**: `https://skiplagged.com/flights/[ORIGIN]/[DESTINATION]/[DEPARTURE_DATE]`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Skiplagged | [Operating carrier(s)] | [e.g., BOG -> MAD -> BUD (Hidden-City exit at BUD, ticketed onward)] | [e.g., 2h 20m in MAD (Total to exit: 14h 10m)] | $[amount] USD | $[amount] COP | [⚠️ Hidden-City: personal item/carry-on ONLY; one-way only] | [Must hold valid entry/visa for BOTH layover exit AND final ticketed city] | [Clean URL] |
```

Structured fields required:
- `provider`: `"Skiplagged"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: Mandatory hidden-city carry-on-only / one-way caveats
- `transit_visa_warning`: Colombian passport check for intermediate hubs AND final ticketed city
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Never initiate booking or recommend violating immigration laws.
- Never recommend a hidden-city fare if `baggage_type == "checked"` or if the final ticketed city requires a visa the Colombian traveler does not possess.

