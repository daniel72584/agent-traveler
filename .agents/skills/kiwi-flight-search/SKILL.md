---
name: kiwi-flight-search
description: >-
  Researches read-only virtual interlining, self-transfer flight combinations across non-partner airlines, and multi-city nomad routes on Kiwi.com (`https://www.kiwi.com/en/cheap-flights/`). Normalizes URLs, converts fares to live COP, and enforces strict self-transfer immigration and baggage warnings for Colombian ordinary passport holders.
---

# Kiwi.com Flight Search (`kiwi-flight-search`)

Use this skill to research virtual interlining and creative multi-carrier self-transfer connections on **Kiwi.com**. Do not book, log in, or submit traveler details.

## Provider & Clean Base URL

- **Provider**: Kiwi.com
- **Clean Base URL**: `https://www.kiwi.com/en/cheap-flights/`
- **Parameterized Search URL Pattern**:
  ```text
  https://www.kiwi.com/en/search/results/[origin-slug]/[destination-slug]/[departure_date]/[return_date]
  ```

### URL Normalization Rules
- Strip all tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `user_id`, `deeplinkId`).
- Keep only clean search or route URLs.

## Core Research Capabilities

1. **Virtual Interlining (Non-Partner Combinations)**: Links transatlantic full-service flights (e.g., Avianca to Madrid `MAD` or Air France to Paris `CDG`) with intra-European low-cost carriers (e.g., Ryanair, Wizz Air, airBaltic) on a single search screen.
2. **NOMAD Multi-City Optimizer**: Tests permutations of multi-stop trips (e.g., Budapest -> Vienna/Sopron -> Tallinn) to find the cheapest sequence of dates.
3. **Self-Transfer Layover Analysis**: Identifies minimum connection windows needed when changing between separate tickets or terminals.

## Mandatory Self-Transfer & Colombian Visa Caveats

Because Kiwi.com specializes in **self-transfer (separate PNR)** combinations:
1. **Immigration Clearance at Layover Hub**: Even if you have only cabin baggage, self-transfer tickets frequently require exiting into the public landside terminal, passing border control, and re-clearing security. The traveler **MUST** hold full entry permission (not just airside transit) for the layover country!
2. **Minimum Layover Buffer (`layoff time`)**: For self-transfers on separate tickets, recommend at least **3.5h–5h** layover buffer (unlike `1.5h–3h` on a single airline PNR), as the second airline has zero obligation to rebook you if the first flight is delayed.
3. **Checked Baggage Penalty**: Checked bags (`checked`) must be collected at the baggage carousel and paid for separately on each leg.

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
If `origin`, `destination`, or `departure_date` is missing, ask for the missing route details before running the search.

### Live Currency Conversion Rule
Convert USD/EUR fares to COP using the live rate from `https://www.google.com/finance/quote/USD-COP` or `https://api.exchangerate-api.com/v4/latest/USD` with fetch timestamp.

## Standardized Output Contract

```markdown
### Kiwi.com Flight Candidates (`kiwi-flight-search`)
- **Search URL**: `https://www.kiwi.com/en/cheap-flights/`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Kiwi.com | [e.g., Avianca + Wizz Air (Self-Transfer)] | [e.g., BOG -> MAD -> BUD] | [e.g., 4h 10m self-transfer in MAD (Total: 15h 45m)] | $[amount] USD | $[amount] COP | [Separate tickets; carry-on recommended; checked bags charged twice] | [Self-transfer requires full entry permission at hub] | [Clean URL] |
```

Structured fields required:
- `provider`: `"Kiwi.com"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: Included bags vs. extra fees + self-transfer baggage warning
- `transit_visa_warning`: Colombian passport entry/transit alert for self-transfer hubs
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Never book or purchase Kiwi Guarantee add-ons.
- Always flag virtual interlining / self-transfer risks clearly so the traveler knows the tickets are not protected by a single airline alliance.

