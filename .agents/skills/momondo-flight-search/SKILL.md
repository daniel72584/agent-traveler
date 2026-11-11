---
name: momondo-flight-search
description: >-
  Researches read-only cross-OTA flight price comparisons, Flight Insight trends, and hidden-fee transparency on Momondo (`https://www.momondo.com/`). Normalizes URLs, converts fares to live COP, and enforces Colombian passport transit visa checks.
---

# Momondo Flight Search (`momondo-flight-search`)

Use this skill to perform deep cross-OTA price comparisons, inspect payment/baggage fee transparency, and evaluate layover vs. price trade-offs on **Momondo**. Do not book, log in, or submit traveler details.

## Provider & Clean Base URL

- **Provider**: Momondo
- **Clean Base URL**: `https://www.momondo.com/`
- **Parameterized Search URL Pattern**:
  ```text
  https://www.momondo.com/flight-search/[ORIGIN]-[DESTINATION]/[DEPARTURE_DATE]/[RETURN_DATE]?sort=bestflight_a
  ```
  *(Omit `/[RETURN_DATE]` for one-way searches.)*

### URL Normalization Rules
- Strip all tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `aid`).
- Output only clean `https://www.momondo.com/flight-search/...` links.

## Core Research Capabilities

1. **Deep Cross-OTA Comparison**: Scans smaller online travel agencies alongside major airlines to surface discounted consolidator fares.
2. **Cheapest vs. Fastest vs. Best Matrix**: Balances total price against layover duration (`layoff time`) to avoid 12+ hour overnight airport waits that save only a few dollars.
3. **Fee & Baggage Transparency**: Highlights how payment method fees or checked bag add-ons affect the real checkout price.

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
If `origin`, `destination`, or `departure_date` is missing, request the missing fields before generating candidate tables.

### Live Currency Conversion Rule
Convert USD/EUR fares to COP using the live rate from `https://www.google.com/finance/quote/USD-COP` or `https://api.exchangerate-api.com/v4/latest/USD` with fetch timestamp.

### Colombian Passport Transit Check
- Check every intermediate hub for Colombian passport transit rules (US `C1/B1/B2`, UK `DATV`, Canadian transit visa, Schengen multi-stop entry).
- Warn when third-party OTA split tickets require self-transfer through border control.

## Standardized Output Contract

```markdown
### Momondo Flight Candidates (`momondo-flight-search`)
- **Search URL**: `https://www.momondo.com/flight-search/[ORIGIN]-[DESTINATION]/[DEPARTURE_DATE]`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Momondo | [Operating carrier(s)] | [e.g., BOG -> CDG -> BUD] | [e.g., 2h 25m in CDG (Total: 14h 15m)] | $[amount] USD | $[amount] COP | [OTA vs direct airline fee & baggage notes] | [Transit visa status] | [Clean URL] |
```

Structured fields required:
- `provider`: `"Momondo"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: Included bags vs. extra fees
- `transit_visa_warning`: Colombian passport transit alert for layover hubs
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Never submit traveler data or follow payment links.
- Remind travelers to verify baggage rules directly on the operating airline's site when Momondo surfaces a third-party OTA fare.

