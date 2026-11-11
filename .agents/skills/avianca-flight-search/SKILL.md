---
name: avianca-flight-search
description: >-
  Researches read-only direct and connecting flights on Avianca (`https://www.avianca.com/`), Colombia's primary flag carrier from Bogotá (`BOG`) and Medellín (`MDE`) across the Americas and Europe (`MAD`, `BCN`, `LHR`, `CDG`). Evaluates branded fare sizes (`XS`, `S`, `M`, `L`, `XXL`), normalizes URLs, converts prices to live COP, and enforces Colombian passport transit visa checks.
---

# Avianca Flight Search (`avianca-flight-search`)

Use this skill to research direct corridors from Colombia (`BOG`, `MDE`, `CLO`, `CTG`), Star Alliance connections, and branded fare baggage rules on **Avianca**. Do not book, log in to LifeMiles accounts, or process payments.

## Provider & Clean Base URL

- **Provider**: Avianca
- **Clean Base URL**: `https://www.avianca.com/`
- **Clean Colombian Storefront**: `https://www.avianca.com/es/`

### URL Normalization Rules
- Strip all tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `chn`, `cmp`).
- Never retain session tokens or booking flow state parameters in outputs.

## Core Research Capabilities

1. **Primary Colombian Hub Network (`BOG` & `MDE`)**:
   - **Direct European Gateways**: Non-stop flights from `BOG` to Madrid (`MAD`), Barcelona (`BCN`), Paris (`CDG`), and London Heathrow (`LHR`), plus `MDE -> MAD`.
   - **Direct Americas Network**: Non-stop flights across South America (`EZE`, `GRU`, `SCL`, `LIM`, `UIO`), Central America/Caribbean (`PTY`, `SJO`, `CUN`, `PUJ`), and North America (`MIA`, `JFK`, `MCO`, `IAD`, `YYZ`).
2. **Branded Fare Baggage Breakdown (`XS` / `S` / `M` / `L`)**:
   - **`XS` (Basic — Americas/Domestic)**: Personal item only (`personal_item`); carry-on and checked bag cost extra.
   - **`S` / `Light` (Europe & Americas)**: 1 personal item + 1 carry-on bag (`carry_on`, 10 kg).
   - **`M` / `Classic`**: 1 personal item + 1 carry-on (`10 kg`) + 1 checked bag (`checked`, `23 kg`).
   - **`L` / `Flex`**: Includes checked bag + seat selection + flexible changes/refunds.
3. **Star Alliance & Partner Interline**: Connects via Madrid (`MAD`) or Bogota (`BOG`) onto European and global partner airlines on a single ticket.

## Standard Skill Contract

### Required Inputs
- `origin` (`from`): Origin airport IATA code or city (e.g., `BOG`, `MDE`).
- `destination` (`to`): Destination airport IATA code or city.
- `departure_date`: Outbound date (`YYYY-MM-DD`).
- `return_date` *(optional)*: Return date (`YYYY-MM-DD`).
- `passengers`: Number of passengers (default `1`).
- `cabin_class`: `economy`, `premium_economy`, `business` (`Insignia` on Boeing 787 to Europe), or `first` (default `economy`).
- `baggage_type`: `personal_item`, `carry_on`, or `checked` (default `carry_on`).

### Missing-Details Gate
If `origin`, `destination`, or `departure_date` is missing, ask for the missing inputs before claiming schedules or prices.

### Live Currency Conversion Rule
Convert USD/EUR fares to COP using the live rate from `https://www.google.com/finance/quote/USD-COP` or `https://api.exchangerate-api.com/v4/latest/USD` with fetch timestamp.

### Colombian Passport Transit Check
- **Madrid (`MAD`) / Barcelona (`BCN`) / Paris (`CDG`)**: Visa-free Schengen entry for ordinary Colombian passports (up to 90 days). Ideal European entry hubs.
- **London Heathrow (`LHR` via `BOG -> LHR`)**: While Colombian citizens can visit the UK visa-free for short tourism stays (subject to UK ETA / current Cancillería rules), switching between London airports (`LHR` to `STN`/`LGW` for Ryanair/Wizz Air) requires passing UK border control and lengthy ground transit.
- **US Gateways (`MIA`, `JFK`, `MCO`, `FLL`)**: Requires a valid US `C1/B1/B2` visa even for connecting flights.

## Standardized Output Contract

```markdown
### Avianca Flight Candidates (`avianca-flight-search`)
- **Search URL**: `https://www.avianca.com/es/`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Avianca | Avianca (+ partner connection if applicable) | [e.g., BOG -> MAD -> BUD] | [e.g., 2h 35m in MAD (Total: 14h 20m)] | $[amount] USD | $[amount] COP | [Fare Light (10kg carry-on) vs Classic (23kg checked)] | [✅ Visa-free Schengen transit at MAD] | `https://www.avianca.com/es/` |
```

Structured fields required:
- `provider`: `"Avianca"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: Branded fare (`XS`/`Light`/`Classic`/`Flex`) baggage inclusion notes
- `transit_visa_warning`: Colombian passport transit alert for layover hubs
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Do not initiate LifeMiles redemptions or checkout sessions.
- Always warn travelers about Avianca's strict `XS` (personal item only) vs. `Light`/`Classic` baggage rules so they account for true baggage costs.

