---
name: ryanair-flight-search
description: >-
  Researches read-only ultra-low-cost intra-European point-to-point connector flights on Ryanair (`https://www.ryanair.com/gb/en`). Enforces strict caveats for Colombian travelers: strict cabin baggage dimensions (`40x20x25cm` personal item vs. Priority `10kg` cabin bag), secondary airports, mandatory online check-in/document verification rules for non-EU passports, and non-protected self-transfers.
---

# Ryanair Flight Search (`ryanair-flight-search`)

Use this skill to research ultra-low-cost intra-European point-to-point flights (e.g., connecting between Madrid/Paris/Budapest/Vienna and Baltic or regional European hubs like Tallinn `TLL`, Riga `RIX`, or Stansted `STN`) on **Ryanair**. Note that Ryanair does **not** operate transatlantic flights from Colombia; it is used either for intra-European hops or as the second leg of a self-transfer from a European gateway.

## Provider & Clean Base URL

- **Provider**: Ryanair
- **Clean Base URL**: `https://www.ryanair.com/gb/en`

### URL Normalization Rules
- Strip all ad and tracking parameters (`gclid`, `gbraid`, `gad_source`, `utm_*`, `affilid`, `mkwid`, `cmpid`).
- Keep only clean `https://www.ryanair.com/gb/en` links.

## Core Research Capabilities

1. **Ultra-Low-Cost Intra-European Point-to-Point Links**: Connects major European hubs (`MAD`, `BCN`, `BUD`, `VIE`, `BER`, `BGY`) with regional and Baltic cities (`TLL` Tallinn, `RIX` Riga, `VNO` Vilnius, `DUB` Dublin, `STN` London Stansted) at rock-bottom base fares.
2. **True Cost Calculation (Base Fare + Baggage Add-Ons)**:
   - **Value Fare**: Includes ONLY 1 small personal bag (`40 x 20 x 25 cm`, must fit under the seat).
   - **Regular / Priority & 2 Cabin Bags**: Adds 1 overhead cabin bag (`carry_on`, `55 x 40 x 20 cm`, max `10 kg`) + priority boarding.
   - **Plus / Checked Bag**: Adds a `10 kg` or `20 kg` checked bag (`checked`) + airport check-in fee protection.

## Mandatory Ryanair Caveats for Colombian Travelers

Whenever a Ryanair flight is included in a route or self-transfer combination, you **MUST** highlight these 4 operational rules:
1. **Strict Baggage Dimensions & Gate Fines**: If `baggage_type` is `carry_on` or `checked` (typical for a traveler coming from Colombia), never quote the bare "Value" fare alone—include the **Priority & 2 Cabin Bags** (`+$20–$40 USD`) or **20kg Checked Bag** (`+$35–$65 USD`) cost, as oversized bags at the boarding gate incur a ~€60–€75 penalty.
2. **Secondary Airports**: Ryanair frequently uses distant secondary airports—for example, **Paris Beauvais (`BVA`)** (~85 km from Paris, ~1h45m+ from `CDG`), **Brussels Charleroi (`CRL`)**, **Milan Bergamo (`BGY`)**, or **London Stansted (`STN`)**. Flag airport transfer time and cost if connecting from a transatlantic flight!
3. **Non-Protected Self-Transfer**: Ryanair sells strictly point-to-point tickets. If pairing a transatlantic flight (e.g., Avianca to `MAD` or Air France to `CDG`) with a separate Ryanair ticket, allow at least **4h+ connection time** (or an overnight stay in the gateway city) and clear immigration/baggage claim.
4. **Online Check-In & Non-EU Passport Verification**: Travelers must check in online via the Ryanair app before the 2-hour pre-departure deadline (airport check-in costs ~€55), and non-EU (Colombian) passport holders should verify visa/passport scan in the Ryanair app or at the visa-check desk before security.

## Standard Skill Contract

### Required Inputs
- `origin` (`from`): European departure airport/city (or Colombian origin when evaluating a transatlantic + Ryanair self-transfer corridor).
- `destination` (`to`): European destination airport/city.
- `departure_date`: Outbound date (`YYYY-MM-DD`).
- `return_date` *(optional)*: Return date (`YYYY-MM-DD`).
- `passengers`: Number of passengers (default `1`).
- `cabin_class`: `economy` (Ryanair operates all-economy cabins).
- `baggage_type`: `personal_item`, `carry_on`, or `checked` (default `carry_on`).

### Missing-Details Gate
If `origin`, `destination`, or `departure_date` is missing, ask for the missing route details before returning candidate options.

### Live Currency Conversion Rule
Convert EUR/USD fares to COP using the live rate from `https://www.google.com/finance/quote/USD-COP` or `https://api.exchangerate-api.com/v4/latest/USD` with fetch timestamp.

## Standardized Output Contract

```markdown
### Ryanair Flight Candidates (`ryanair-flight-search`)
- **Search URL**: `https://www.ryanair.com/gb/en`
- **Live Exchange Rate**: `1 USD = [rate] COP (Source: [source], fetched [timestamp])`

| Provider | Airlines | Route (`Origin -> Hub -> Dest`) | Layover Time (`layoff time`) & Total Duration | Price (USD) | Price (Live COP) | Baggage & Fee Notes | Transit Visa Warning (Colombian Passport) | Clean Search URL |
|---|---|---|---|---|---|---|---|---|
| Ryanair | Ryanair (or Transatlantic Carrier + Ryanair Self-Transfer) | [e.g., VIE -> TLL or BOG -> MAD -> BUD] | [e.g., Direct 2h 15m intra-EU, or 4h 30m self-transfer in MAD] | $[amount] USD | $[amount] COP | [Includes Priority 10kg carry-on / 20kg checked bag add-on; Value fare is 40x20x25cm only] | [Self-transfer requires Schengen entry & baggage re-check; check secondary airport codes] | `https://www.ryanair.com/gb/en` |
```

Structured fields required:
- `provider`: `"Ryanair"`
- `airlines`: Operating carrier(s)
- `route`: `Origin -> Layover Hub(s) -> Destination`
- `layover_time`: Layover duration per stop (`h/m`) and total trip duration
- `price_usd` & `price_cop`: Indicative price (including realistic baggage add-on) converted via live `USD-COP` rate with timestamp
- `baggage_and_fee_notes`: Value (`40x20x25cm`) vs. Priority (`10kg`) / Checked (`20kg`) fee breakdown + online check-in rule
- `transit_visa_warning`: Colombian passport Schengen entry & secondary airport (`BVA`/`STN`) self-transfer warning
- `search_url`: Clean parameterized deep link

## Guardrails
- Read-only research only. Do not log in to myRyanair accounts or initiate bookings.
- Never pair a transatlantic arrival at `CDG` (Paris Charles de Gaulle) with a tight `< 4h` departure from `BVA` (Paris Beauvais) without flagging the cross-city transfer risk.

