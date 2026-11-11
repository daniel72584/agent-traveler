---
name: skyscanner-flight-search
description: >-
  Researches read-only flight routes and indicative fares on Skyscanner (`https://www.skyscanner.net/`). Excels at searching "Everywhere" to discover cheap regional entry hubs and comparing budget vs. full-service airlines across global OTAs. Normalizes URLs, converts fares to live COP, and enforces Colombian passport transit visa checks.
---

# Skyscanner Flight Search (`skyscanner-flight-search`)

Use this skill to compare full-service and low-cost carrier combinations and discover the cheapest entry hubs on **Skyscanner**. Do not book, log in, or submit traveler details.

## Provider & Clean Base URL

- **Provider**: Skyscanner
- **Clean Base URL**: `https://www.skyscanner.net/`
- **Parameterized Search URL Pattern**:
  ```text
  https://www.skyscanner.net/transport/flights/[origin_lower]/[dest_lower]/[yymmdd_depart]/[yymmdd_return]/
  ```
  *(Or `https://www.skyscanner.net/transport/flights/[origin_lower]/[dest_lower]/` when dates are flexible.)*

### URL Normalization Rules
- Strip all tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `associateid`, `kpid`).
- Never retain session IDs or affiliate redirect strings in outputs.

## Core Research Capabilities

1. **"Everywhere" & Cheapest Entry Hub Discovery**: Finds the lowest-cost gateway airport into Europe, Asia, or the Americas from Bogotá (`BOG`) or Medellín (`MDE`).
2. **Full-Service vs. Low-Cost Carrier (LCC) Blending**: Compares legacy alliances (SkyTeam, Star Alliance, oneworld) alongside regional low-cost airlines (Wizz Air, Ryanair, airBaltic, EasyJet, Vueling).
3. **Whole-Month View**: Identifies low-season vs. peak-day pricing across an entire calendar month.

## Standard Skill Contract

### Required Inputs
- `origin` (`from`): Origin airport IATA code or city.
- `destination` (`to`): Destination airport IATA code or city.
- `departure_date`: Outbound date (`YYYY-MM-DD`).
- `return_date` *(optional)*: Return date (`YYYY-MM-DD`).
- `passengers`: Number of passengers (default `1`).
- `cabin_class`: `economy`, `premium_economy`, `business`, or `first` (default `economy`).
- `baggage_type`: `personal_item`, `carry_on`, or `checked` (default `carry_on`).

### Missing-Details Gate
If `origin`, `destination`, or `departure_date` is missing, prompt for the missing inputs before returning specific route fares.

### Live Currency Conversion Rule
Convert all indicative fares to COP using the live rate from `https://www.google.com/finance/quote/USD-COP` or `https://api.exchangerate-api.com/v4/latest/USD` with fetch timestamp.

### Colombian Passport Transit Check
- Verify whether Skyscanner "Mash-up" (multi-airline non-protected transfer) itineraries require clearing customs and immigration at the layover airport.
- Flag US (`C1/B1/B2`), UK (`DATV`), and self-transfer visa requirements for Colombian ordinary passports.

## Standardized Output Contract

```markdown
### Skyscanner Flight Candidates (`skyscanner-flight-search`)
- **Search URL**: `https://www.skyscanner.net/transport/flights/...`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Skyscanner | [Operating carrier(s)] | [e.g., BOG -> MAD -> VIE] | [e.g., 3h 05m in MAD (Total: 14h 50m)] | $[amount] USD | $[amount] COP | [Baggage & OTA vs airline direct note] | [Transit visa & self-transfer check] | [Clean URL] |
```

Structured fields required:
- `provider`: `"Skyscanner"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: Included bags vs. extra fees
- `transit_visa_warning`: Colombian passport transit alert for layover hubs
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only planning only. Do not trigger booking forms or bypass anti-bot protections.
- Flag when a third-party OTA price on Skyscanner excludes cabin baggage or charges higher change/support fees than booking directly with the airline.

