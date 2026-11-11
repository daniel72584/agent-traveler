---
name: airfrance-flight-search
description: >-
  Researches read-only direct transatlantic flights from Colombia (`BOG -> CDG`) and SkyTeam intra-European connections on Air France (`https://wwws.airfrance.com.co/` and `https://www.airfrance.com/`). Ideal for visa-free Schengen transit for Colombian ordinary passport holders traveling to Europe, Central/Eastern Europe, the Baltics, Africa, or Asia.
---

# Air France Flight Search (`airfrance-flight-search`)

Use this skill to research direct transatlantic flights from Bogotá (`BOG`) and SkyTeam/KLM one-ticket protected connections via Paris Charles de Gaulle (`CDG`) or Amsterdam (`AMS`) on **Air France Colombia**. Do not book, log in to Flying Blue accounts, or submit payment details.

## Provider & Clean Base URL

- **Provider**: Air France / Air France Colombia
- **Clean Base URLs**:
  - `https://wwws.airfrance.com.co/`
  - `https://www.airfrance.com/`

### URL Normalization Rules
- Strip all ad and tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `WT.mc_id`).
- Keep only clean Air France domain and route search paths.

## Core Research Capabilities

1. **Direct Transatlantic Corridor (`BOG <-> CDG`)**: Daily non-stop Boeing 787 / Airbus A350 service from Bogotá El Dorado (`BOG`) to Paris Charles de Gaulle (`CDG`), completely avoiding US (`MIA`/`JFK`) and UK (`LHR`) transit visa barriers for Colombian citizens.
2. **Protected Single-PNR European Connections**: Seamless through-checked baggage from `BOG` via `CDG` (or KLM partner `AMS`) to Central/Eastern Europe (`BUD` Budapest, `VIE` Vienna, `PRG` Prague, `WAW` Warsaw) and Nordic/Baltic capitals (`TLL` Tallinn, `RIX` Riga, `HEL` Helsinki).
3. **Fare Family Comparison (`Light`, `Standard`, `Flex`)**:
   - **Economy Light**: Includes 1 cabin bag (`carry_on`, 12 kg total with personal item), 0 checked bags (`checked` costs extra).
   - **Economy Standard**: Includes 1 cabin bag + 1 checked bag (`23 kg`).

## Standard Skill Contract

### Required Inputs
- `origin` (`from`): Origin airport IATA code or city (typically `BOG`, or `MDE`/`CLO`/`CTG` via domestic partner feed).
- `destination` (`to`): Destination airport IATA code or city.
- `departure_date`: Outbound date (`YYYY-MM-DD`).
- `return_date` *(optional)*: Return date (`YYYY-MM-DD`).
- `passengers`: Number of passengers (default `1`).
- `cabin_class`: `economy`, `premium_economy`, `business`, or `first` (default `economy`).
- `baggage_type`: `personal_item`, `carry_on`, or `checked` (default `carry_on`).

### Missing-Details Gate
If `origin`, `destination`, or `departure_date` is missing, ask for the missing route parameters before returning fare estimates.

### Live Currency Conversion Rule
Convert USD/EUR fares to COP using the live rate from `https://www.google.com/finance/quote/USD-COP` (or `EUR-COP`) or `https://api.exchangerate-api.com/v4/latest/USD` with fetch timestamp.

### Colombian Passport Transit Check
- **Paris (`CDG`) & Amsterdam (`AMS`)**: Ordinary Colombian passports enjoy **90-day visa-free Schengen entry**. When flying `BOG -> CDG -> Intra-Schengen Destination` (e.g., `BUD` or `VIE`), travelers clear Schengen passport control at `CDG` (recommend **`1h 45m` to `3h 30m`** connection window at CDG Terminal 2E -> 2F).
- For non-Schengen onward destinations via `CDG`, airside international transit is also available (subject to standard Cancillería/destination visa rules).

## Standardized Output Contract

```markdown
### Air France Flight Candidates (`airfrance-flight-search`)
- **Search URL**: `https://wwws.airfrance.com.co/`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Air France | Air France (or Air France + KLM / airBaltic codeshare) | [e.g., BOG -> CDG -> BUD] | [e.g., 2h 15m in CDG (Total: 13h 55m)] | $[amount] USD | $[amount] COP | [Light (carry-on 12kg) vs Standard (23kg checked included)] | [✅ Visa-free Schengen entry at CDG; bypasses US/UK transit visas] | `https://wwws.airfrance.com.co/` |
```

Structured fields required:
- `provider`: `"Air France"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: `Light` vs. `Standard` baggage inclusion details
- `transit_visa_warning`: Colombian passport Schengen entry/transit note at `CDG`/`AMS`
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Do not create bookings, hold PNRs, or enter Flying Blue credentials.
- Highlight open-jaw (multi-city) savings on `airfrance.com.co` when a traveler arrives in one European city (e.g., Budapest `BUD`) and returns from another (e.g., Tallinn `TLL` or Vienna `VIE`).

