---
name: google-flights-search
description: >-
  Researches read-only flight routes, schedules, flexible date grids, and indicative fares on Google Flights (`https://www.google.com/travel/flights`). Best overall for speed, interactive explore maps, flexible date grids, and price tracking alerts. Always normalizes URLs, converts fares to COP using live exchange rates, and flags transit visa requirements for Colombian ordinary passport holders.
---

# Google Flights Search (`google-flights-search`)

Use this skill to research flight options, layover durations, airlines, and indicative price ranges on **Google Flights**. Do not book, log in, enter passenger details, or process payments.

## Provider & Clean Base URL

- **Provider**: Google Flights
- **Clean Base URL**: `https://www.google.com/travel/flights`
- **Parameterized Search URL Pattern**:
  ```text
  https://www.google.com/travel/flights?q=Flights+from+[origin]+to+[destination]+on+[departure_date]
  ```

### URL Normalization Rules
- Strip all ad and tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `ved`, `ei`).
- Never preserve session tokens, user account identifiers, or referral hashes.

## Core Research Capabilities

1. **Speed & Route Discovery**: Fast comparison of direct vs. 1-stop and 2-stop itineraries from Colombian hubs (`BOG`, `MDE`, `CLO`, `CTG`).
2. **Flexible Date Grids & Price Graphs**: Identifies whether shifting departure or return dates by 1–3 days significantly drops the total fare.
3. **Interactive Explore Map**: Pinpoints the cheapest entry hub in a target continent (e.g., Madrid `MAD` or Paris `CDG` for Europe).
4. **Baggage & Cabin Filtering**: Filters Basic Economy vs. Main Cabin fares to account for carry-on (`carry_on`) and checked bag (`checked`) fees.

## Standard Skill Contract

### Required Inputs
- `origin` (`from`): Origin airport IATA code or city (e.g., `BOG`, `MDE`).
- `destination` (`to`): Destination airport IATA code or city.
- `departure_date`: Outbound date (`YYYY-MM-DD`) or flexible month/window.
- `return_date` *(optional)*: Return date (`YYYY-MM-DD`) for round-trip searches.
- `passengers`: Number of adult/child passengers (default `1`).
- `cabin_class`: `economy`, `premium_economy`, `business`, or `first` (default `economy`).
- `baggage_type`: `personal_item`, `carry_on`, or `checked` (default `carry_on`).

### Missing-Details Gate
If `origin`, `destination`, or `departure_date` is missing, pause and ask the traveler or calling agent to supply the missing route fields before claiming flight availability or prices.

### Live Currency Conversion Rule
When reporting `price_cop`, ALWAYS fetch the live rate from `https://www.google.com/finance/quote/USD-COP` (or `https://api.exchangerate-api.com/v4/latest/USD` as JSON fallback) and cite the timestamp. Never invent exchange rates.

### Colombian Passport Transit Check
Always inspect layover hubs for ordinary Colombian passport holders:
- **United States (`MIA`, `JFK`, `ATL`, `IAH`, `FLL`, `MCO`)**: Mandatory US `C1` or `B1/B2` visa even for airside international transit.
- **United Kingdom (`LHR`, `LGW`)**: Mandatory UK Direct Airside Transit Visa (`DATV`) or Visitor in Transit visa unless exempt.
- **Schengen Area (`MAD`, `CDG`, `AMS`, `FRA`)**: Visa-free up to 90 days; note if a connection involves 2+ Schengen stops requiring Schengen entry clearance.

## Standardized Output Contract

Return candidate flight records in this structure:

```markdown
### Google Flights Candidates (`google-flights-search`)
- **Search URL**: `https://www.google.com/travel/flights?q=...`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Google Flights | [Operating carrier(s)] | [e.g., BOG -> MAD -> BUD] | [e.g., 2h 15m in MAD (Total: 14h 30m)] | $[amount] USD | $[amount] COP | [Included bags vs. extra fees] | [Visa-free transit / US Visa Required / etc.] | [Clean URL] |
```

And expose the structured fields:
- `provider`: `"Google Flights"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price in USD and live COP with timestamp
- `baggage_and_fee_notes`: Included bags vs. extra fees
- `transit_visa_warning`: Colombian passport transit alert for layover hubs
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Do not initiate checkout, seat selection, or booking redirects.
- Never fabricate flight numbers or guaranteed fares; label all fares as indicative planning snapshots.

