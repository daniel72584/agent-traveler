---
name: travel-price-scouting
description: >-
  Researches read-only indicative prices for accommodations and flights using sites such as Booking, Airbnb, Hostelworld, and Kayak. Use whenever the user asks ANY of the following - even without saying "price" or "cost" explicitly - compare lodging or flight prices, find hostels/hotels/houses/flats/posadas/guesthouses/albergues by criteria, check amenities like internet/wifi/private bathroom/parking/private room, estimate trip budget, "how much will X cost", "what's a reasonable budget for X", "cheapest options to X", any backpacker / mid-budget / luxury framing, "how much per night", "is X enough budget for Y days", booking-site comparison, OR whenever the user mentions a budget figure (in COP, USD, EUR, or any currency) alongside lodging or transport. When converting between currencies, ALWAYS fetch the live rate from `https://www.google.com/finance/quote/USD-COP` (or the relevant pair) or `https://api.exchangerate-api.com/v4/latest/USD` as JSON fallback - never state an exchange rate from training data. Do NOT invent specific fares or per-night prices - this skill is for indicative ranges only.
---

# Travel Price Scouting

Use this skill to research indicative prices for flights and accommodations. Do not book, reserve, hold, message hosts, log in, pay, or submit traveler details. Treat every price as a helpful planning estimate, not a guaranteed transaction.

## Supported Sources

Default public sources:

- Booking: `https://www.booking.com/`
- Airbnb: `https://www.airbnb.com/`
- Kayak flights: `https://www.kayak.com.co/flights`
- Google `https://www.google.com/travel/flights`

Normalize user-provided URLs before using them:

- Strip ad/tracking parameters such as `gclid`, `gbraid`, `gad_source`, `aid`, `label`, and `force_referer` unless needed for page access.
- Never preserve tokens, session IDs, account IDs, or private referral data in outputs.
- Prefer the clean domain or search page in citations.

## Required Inputs

For accommodation scouting, collect or preserve (from the validated `trip-spec`):

- Destination city or neighborhood.
- Check-in and check-out dates, or travel month/season if flexible.
- Number of guests and rooms/beds.
- Accommodation kind: hostel, hotel, house, flat/apartment, private room, shared dorm, or flexible.
- Room configuration: private room vs. shared dormitory.
- Bathroom: private bathroom vs. shared bathroom.
- Preferred standard/stars: unrated, 2★, 3★, 4★, 5★, or boutique.
- Nightly budget limit: maximum price cap and currency (COP, USD, EUR).
- Required amenities: internet/Wi-Fi, air conditioning, workspace, breakfast, elevator, etc.
- Preferred area, safety/location priorities, cancellation flexibility, rating/review minimum, and maximum distance from center or transit when available.

For flight scouting, collect or preserve:

- Origin and destination airports/cities.
- Departure and return dates, or flexible date window.
- One-way, round trip, or multi-city.
- Number of travelers and cabin class.
- Baggage needs, direct-flight preference, maximum stops, preferred airlines, and budget when available.

## Missing-Details Gate

Ask a clarifying question before searching or claiming price ranges when any blocking input is missing.

Accommodation blockers:

- Destination city or neighborhood.
- Check-in/check-out dates, or at least travel month/season for rough scouting.
- Number of guests and rooms/beds.

Flight blockers:

- Origin and destination cities/airports.
- Departure and return dates, or flexible date window.
- Number of travelers.

If the user asks for matching accommodation rather than exact prices, still ask for dates/month and guest count because availability changes the result. If the user explicitly asks for a rough, no-price strategy, proceed and label it as planning guidance.

Ask in this format:

```markdown
I can scout Booking/Airbnb/Kayak, but I need:
- [blocking input]
- [blocking input]

Optional filters:
- budget/currency
- private room only vs dorms acceptable
- required amenities beyond Wi-Fi/private bathroom/parking
```

## Search Workflow

1. Convert the user's criteria into filters before opening source pages.
2. Use browser automation or web search/fetch tools when available. If a site blocks automation, use accessible search snippets or ask for manual screenshots/exported page text.
3. Search at least two sources when possible for accommodations, usually Booking plus Airbnb.
4. For flights, use Kayak as an aggregator and label prices as provider-dependent.
5. Capture only visible, public listing details:
   - Listing/property name or airline/route when visible.
   - Price, currency, taxes/fees visibility, dates, and occupancy.
   - Amenities that match or fail the user's required filters.
   - Cancellation/refund hints only if visible.
   - Source URL or clean source name.
6. Do not bypass captchas, login walls, paywalls, or anti-bot protections.

## Matching Rules

Separate criteria into:

- `Must-have`: filters that disqualify a result, such as private bathroom or Wi-Fi.
- `Nice-to-have`: preferences that can rank results, such as breakfast or central area.
- `Unknown`: criteria not visible in the source result.

Do not mark a listing as matching an amenity unless the source explicitly shows it. If the page only implies it, write `unknown`; apparently ambiguity also needed a vacation.

## Output Contract

Return this structure:

```markdown
## Price Scouting Criteria
- Destination/route: [value]
- Dates: [value or "not provided"]
- Travelers/guests: [value or "not provided"]
- Must-have filters: [list]
- Nice-to-have filters: [list]
- Budget/currency: [value or "not provided"]

## Accommodation Price Snapshot
### [City Or Area]
| Source | Type | Candidate | Visible Price | Matches | Missing/Unknown | Notes |
|---|---|---|---|---|---|---|
| [Booking/Airbnb/etc.] | [hostel/hotel/flat/etc.] | [name or "not captured"] | [price + currency + period] | [must-haves met] | [unknowns] | [fees/cancellation/location caveats] |

## Flight Price Snapshot
| Source | Route | Dates | Visible Price | Stops/Baggage | Notes |
|---|---|---|---|---|---|
| [Kayak/etc.] | [origin -> destination] | [dates] | [price + currency] | [visible details or unknown] | [provider/date caveats] |

## Best Fit
- [Short recommendation based on criteria and price, or "not enough data"]

## Caveats
- Prices can change quickly and may exclude taxes, cleaning fees, baggage, resort fees, or city taxes.
- Booking/payment availability must be verified manually on the source site before purchase.
- [Any site blocks, login walls, or missing criteria]
```

If no tables are practical in the final user response, keep the same fields as bullets.

## Guardrails

- Read-only only. No booking, no account login, no payment, no messaging hosts, no traveler profile entry.
- Do not scrape aggressively or bypass bot protection.
- Do not recommend unsafe neighborhoods without checking current context.
- Do not expose full tracking URLs or personal identifiers.
- Do not treat Airbnb or Booking prices as final until fees and taxes are visible at checkout.
