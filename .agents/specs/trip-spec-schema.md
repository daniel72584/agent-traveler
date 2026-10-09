# Trip Specification (trip-spec v1.0) Schema

Spec-Driven Development (SDD) contract for Agent Traveler.
Every travel plan must be anchored by a validated `trip-spec` before launching in-depth research, flight routing, visa legalities, or price scouting.

---

## 1. Specification Fields

| Field | Type | Required | Description & Valid Options |
|---|---|---|---|
| `spec_version` | String | Yes | Version of specification schema (e.g., `1.0`). |
| `status` | String | Yes | `draft` \| `interviewing` \| `validated`. |
| `traveler_profile` | Object | Yes | Nationality (ordinary Colombian passport), party size, travel purpose (tourism / work / study). |
| `origin` | String | Yes | Departure city/airport in Colombia (e.g., `BOG - Bogotá`, `MDE - Medellín`). |
| `places_to_visit` | List[String] | Yes | Target destinations, specific cities, regions, and must-see attractions. |
| `timing` | Object | Yes | Travel dates, month, or season, plus total duration in days. |
| `preferred_weather` | String | Yes | Desired climate (e.g., `warm & sunny`, `mild / spring`, `cool / autumn`, `snow / winter`, `avoid rain`). |
| `accommodation` | Object | Yes | Detailed lodging criteria (see below). |
| `budget_cap_nightly` | Object | Optional | Maximum lodging price per night and currency (e.g., `50 USD` or `200,000 COP`). |
| `activity_style` | String | Optional | Travel pace: `relaxed`, `moderate`, `packed / fast-paced`. |

### Accommodation Sub-Schema
- **`kind`**: `hotel` | `hostel` | `apartment / Airbnb` | `guesthouse / posada` | `flexible`
- **`room_type`**: `private_room` | `shared_dorm` | `entire_place` | `flexible`
- **`bathroom`**: `private_bathroom` | `shared_bathroom` | `flexible`
- **`stars`**: `1-2 stars` | `3 stars` | `4 stars` | `5 stars` | `boutique` | `any`
- **`max_price_per_night`**: Numeric amount with currency (e.g., `60 USD / noche`, `250,000 COP / noche`).

---

## 2. Interactive SDD Interview Protocol

When a user submits a travel request that lacks these core fields, the primary agent (`travel-supervisor`) triggers the **SDD Interview**:

```markdown
### ✈️ Trip Specification Interview (SDD)

To build your personalized, accurate trip report, let's establish your **Trip Spec**:

1. **🏨 Accommodation Preferences**:
   - **Type**: Do you prefer hotels, hostels, apartments/Airbnb, or guesthouses?
   - **Room & Bath**: Do you require a private room and private bathroom, or are shared dorms/bathrooms acceptable?
   - **Standard & Stars**: Preferred star rating (e.g., 2★, 3★, 4★, boutique) or any standard?
   - **Max Nightly Price**: What is your maximum budget per night (in COP or USD)?

2. **📍 Places & Cities to Visit**:
   - Which specific cities, regions, or must-see landmarks do you want to explore?
   - Do you have an intended order or pace?

3. **☀️ Preferred Weather & Season**:
   - What kind of weather do you prefer (warm & sunny, mild spring, cool autumn, snow/winter)?
   - Any climate conditions you want to strictly avoid (e.g., monsoon, extreme heat)?

4. **🗓️ Timing & Traveler Profile**:
   - Approximate travel dates or travel month, and duration?
   - Purpose of travel (tourism, study, remote work)?
   - Departure city in Colombia (Bogotá BOG, Medellín MDE, etc.)?
```

---

## 3. Validated `trip-spec` Markdown Contract

Once confirmed, the validated spec is recorded in this standard block format:

```markdown
```yaml
trip_spec:
  version: "1.0"
  status: "validated"
  traveler:
    passport: "Colombian Ordinary"
    count: 1
    purpose: "Tourism"
  origin: "Bogotá (BOG)"
  destinations:
    places_to_visit:
      - "Tokyo"
      - "Kyoto"
      - "Osaka"
    route_order: ["Tokyo", "Kyoto", "Osaka"]
  timing:
    dates: "2026-11-05 to 2026-11-20"
    duration_days: 15
  preferred_weather: "Mild autumn, crisp, dry (fall foliage)"
  accommodation:
    kind: "hotel"
    room_type: "private_room"
    bathroom: "private_bathroom"
    stars: "3-star or business hotel"
    max_price_per_night: "80 USD (approx. 330,000 COP)"
  activity_style: "moderate cultural exploration"
```
```

---

## 4. Downstream Agent Contract Consumption

- **`cancilleria-scanner` / `travel-requirements`**: Reads `traveler.passport`, `timing.dates`, `destinations`, and `traveler.purpose`.
- **`weather-transport-researcher`**: Validates destination climate against `preferred_weather`. If the destination has monsoons or freezing cold when the user specified "warm & sunny", it alerts the traveler immediately.
- **`travel-route-mapping`**: Builds ordered route links connecting `destinations.places_to_visit`.
- **`travel-price-scouting`**: Filters accommodation search strictly by `accommodation.kind`, `room_type`, `bathroom`, `stars`, and `max_price_per_night`.
