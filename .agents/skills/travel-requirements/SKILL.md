---
name: travel-requirements
description: >-
  Checks official travel entry requirements, visa rules, passport constraints, vaccination requirements, transit caveats, and consular coverage for international trips. Use whenever the user asks ANY of the following - even without saying "visa" explicitly - "what documents do I need for X", "can I enter country X with my passport", "do I need a visa for X", Cancillería/Cancilleria guidance, embassy or consular information, passport validity rules, yellow-fever or vaccination requirements, customs limits, border crossing rules, transit-visa rules, or any question about whether a specific nationality (especially Colombian ordinary passport) can legally enter or transit a country. Apply BEFORE finalizing any route that crosses one or more international borders.
---

# Travel Requirements

Use this skill to verify official visa rules, passport validity, border transit, and health requirements before planning an international route. It relies on verified government authorities so travelers know exactly what documents are needed before departure.

## Required Inputs

Collect or preserve these facts when available:

- Traveler nationality or passport country.
- Passport type: ordinary, diplomatic, official, service, refugee/stateless, or unknown.
- Destination countries and transit countries.
- Purpose of travel: tourism, work, study, business, transit, family visit, or unknown.
- Travel dates or intended length of stay.
- Residence country when visa exemptions may depend on residence.

## Missing-Details Gate

If entry requirements matter and nationality or passport type is missing, ask before researching final requirements. Do not make a final visa claim from destination alone. Country rules are not horoscopes; passport context matters.

Ask for:

- Passport nationality.
- Passport type: ordinary, diplomatic, official, service, refugee/stateless, or other.
- Travel purpose.
- Approximate dates or intended length of stay.
- Transit countries, if the route is known.

If the user only wants a rough planning caveat, proceed with `Low` confidence and state exactly which details must be verified.

## Source Order

Prefer sources in this order:

1. Traveler's foreign ministry or consular authority, such as Colombia's Cancillería for Colombian travelers.
2. Destination country's immigration, foreign affairs, embassy, consulate, or official eVisa portal.
3. Airline, airport, or official transit authority pages for transit rules.
4. High-quality secondary travel requirement aggregators only as supporting context, never final authority.

For Colombian travelers, search Spanish variants as needed:

- `Cancillería [country in Spanish] colombianos visa`
- `site:cancilleria.gov.co [country in Spanish] visa colombianos`
- `site:cancilleria.gov.co [country slug]`

Normalize country names across languages, accents, and common spellings, for example `Kazakhstan` / `Kazajistán` and `Uzbekistan` / `Uzbekistán`.

## Fetch Workflow

1. Try structured or direct fetch tools first for public URLs.
2. If an official page returns `403`, anti-bot, or unusable HTML:
   - Use search results to locate the official page and quote only what the result snippet or accessible cache actually supports.
   - Use browser automation if available and appropriate.
   - Cross-check with the destination country's official immigration or eVisa site.
3. Do not use URLs containing tokens, session IDs, or secrets. Redact them if the user provides one.
4. Do not perform state-changing requests such as form submission, payment, booking, or application creation.

## Analysis Checklist

For each country, check:

- Visa required, visa-free, eVisa, visa on arrival, or unknown.
- Maximum permitted stay and entry count when available.
- Passport validity and blank-page requirements when available.
- Required documents: return ticket, proof of funds, accommodation, insurance, invitation letter, registration, vaccines, or permits.
- Transit rules when the route passes through another country.
- Official application URL when visa or eVisa is required.
- Embassy, consulate, or concurrent diplomatic coverage.
- Date sensitivity: whether rules depend on travel dates, length of stay, or purpose.

## Confidence Labels

Use one of these labels:

- `High`: official page was fetched/read directly and matches another official source or is sufficiently explicit.
- `Medium`: official source was found through search snippets or one official source is accessible but not fully cross-checked.
- `Low`: only secondary sources are available, sources conflict, or key traveler facts are missing.

Keep blocked official pages visible in the confidence explanation. A blocked government page is not evidence; it is just bureaucracy wearing sunglasses.

## Output Contract

Return this structure:

```markdown
## Travel Requirements

### [Country]
- Traveler context: [nationality, passport type, purpose, dates/length if known]
- Entry status: [visa-free | visa required | eVisa | visa on arrival | transit-only | unknown]
- Stay limit: [duration or unknown]
- Required documents: [bullets or unknown]
- Official sources: [links and what each source supports]
- Consular coverage: [embassy/consulate/concurrent coverage or unknown]
- Confidence: [High | Medium | Low] - [short reason]
- Verify before booking: [specific items]

## Cross-Border Or Transit Caveats
- [route-wide caveats, or "none identified from available sources"]

## Assumptions
- [only assumptions actually used, or "none"]
```

## Guardrails

- Do not present secondary aggregator data as final truth.
- Do not invent visa fees, processing times, document lists, or eligibility rules.
- Do not hide uncertainty to make the trip plan look cleaner.
- Recommend final manual verification with official authorities before booking or departure when requirements affect entry.
