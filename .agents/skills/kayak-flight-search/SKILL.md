---
name: kayak-flight-search
description: >-
  Researches read-only flight options, color-coded price calendars, nearby airport expansions, Hacker Fares, and layover duration filters on KAYAK (`https://www.kayak.com/flights` and `https://www.kayak.com.co/flights`). Normalizes URLs, converts fares to live COP, and enforces Colombian passport transit visa checks.
---

# KAYAK Flight Search (`kayak-flight-search`)

Use this skill to research flight routes, multi-OTA fare comparisons, Hacker Fares, and layover filters on **KAYAK**. Do not book, reserve, log in, or submit traveler payment details.

## Provider & Clean Base URL

- **Provider**: KAYAK / KAYAK Colombia
- **Clean Base URLs**:
  - `https://www.kayak.com/flights`
  - `https://www.kayak.com.co/flights`
- **Parameterized Search URL Pattern**:
  ```text
  https://www.kayak.com.co/flights/[ORIGIN]-[DESTINATION]/[DEPARTURE_DATE]/[RETURN_DATE]?sort=bestflight_a
  ```
  *(For one-way flights, omit `/[RETURN_DATE]`.)*

### URL Normalization Rules
- Strip all tracking and affiliate parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `aid`, `label`).
- Keep only clean route path segments and essential sort/filter query parameters (`sort=bestflight_a` or `sort=price_a`).

## Core Research Capabilities

1. **Color-Coded Price Calendars**: Spots low-fare departure days across a 30-day window.
2. **Nearby Airport Expansion**: Checks whether flying into or out of nearby hubs (e.g., Vienna `VIE` for Sopron/Bratislava, or Fort Lauderdale `FLL` vs. Miami `MIA`) lowers total cost.
3. **KAYAK Hacker Fares**: Combines two separate one-way tickets on different airlines when cheaper than a traditional round-trip *(must flag self-transfer and separate ticket risks)*.
4. **Smart Layover & Fee Assistant Filters**: Filters maximum layover duration and calculates true total cost after adding carry-on (`carry_on`) or checked (`checked`) baggage.

## Standard Skill Contract

### Required Inputs
- `origin` (`from`): Origin airport IATA code or city (e.g., `BOG`, `MDE`).
- `destination` (`to`): Destination airport IATA code or city.
- `departure_date`: Outbound date (`YYYY-MM-DD`).
- `return_date` *(optional)*: Return date (`YYYY-MM-DD`) for round-trip searches.
- `passengers`: Number of passengers (default `1`).
- `cabin_class`: `economy`, `premium_economy`, `business`, or `first` (default `economy`).
- `baggage_type`: `personal_item`, `carry_on`, or `checked` (default `carry_on`).

### Missing-Details Gate
If `origin`, `destination`, or `departure_date` is missing, ask for the missing fields before running or claiming search results.

### Live Currency Conversion Rule
Always convert USD/EUR fares into COP using the live rate from `https://www.google.com/finance/quote/USD-COP` or `https://api.exchangerate-api.com/v4/latest/USD` with a fetch timestamp.

### Colombian Passport Transit Check
- Flag US layovers (`MIA`, `JFK`, `IAH`, `FLL`, `ATL`) as requiring a valid US `C1/B1/B2` visa.
- Flag UK layovers (`LHR`, `LGW`) as requiring a UK `DATV` unless exempt.
- Flag **Hacker Fares** or multi-ticket combinations that require clearing immigration to re-check bags at a layover hub.

## Standardized Output Contract

```markdown
### KAYAK Flight Candidates (`kayak-flight-search`)
- **Search URL**: `https://www.kayak.com.co/flights/[ORIGIN]-[DESTINATION]/[DEPARTURE_DATE]`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| KAYAK | [Operating carrier(s)] | [e.g., BOG -> CDG -> TLL] | [e.g., 2h 40m in CDG (Total: 15h 10m)] | $[amount] USD | $[amount] COP | [Fee Assistant baggage notes / Hacker Fare warning] | [Transit visa status] | [Clean URL] |
```

Structured fields required:
- `provider`: `"KAYAK"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: Included bags vs. extra fees (including Hacker Fare dual-ticket notes)
- `transit_visa_warning`: Colombian passport transit alert for layover hubs
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Do not follow OTA checkout redirects or submit passenger data.
- Clearly distinguish single-PNR protected transfers from KAYAK Hacker Fares (two separate tickets).

