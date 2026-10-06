---
name: travel-route-mapping
description: >-
  Generates Google Maps route, search, place, and coordinate links for travel planning. Use whenever the user asks ANY of the following - even without saying "Google Maps" explicitly - how to get from one city to another, transportation or routing between stops, what to see along the way on a multi-stop trip, mapping a journey or itinerary, tracing a historical/themed route across multiple places, connecting waypoints by car/train/bus/walking, generating Google Maps URLs, inspecting an existing Maps URL, or any query that involves linking two or more geographic stops in sequence (even if the user just says "I want to go from X to Y to Z").
---

# Travel Route Mapping

Use this skill to create clean, clickable Google Maps links for your itinerary. Google Maps helps travelers visualize travel distances, see the ordered sequence of destinations, and locate train stations, safe neighborhoods, and key attractions along the journey.

Reference guide: `https://gotoapplemaps.com/guides/google-maps-url-formats-explained/`

## Supported Google Maps URL Types

Recognize these formats:

- Directions path: `https://www.google.com/maps/dir/Origin/Destination`
- Directions with waypoints in path: `https://www.google.com/maps/dir/A/B/C`
- Clean directions API URL: `https://www.google.com/maps/dir/?api=1&origin=A&destination=B&waypoints=C|D&travelmode=driving`
- Search URL: `https://www.google.com/maps/search/?api=1&query=coffee+shops+near+me`
- Place URL: `https://www.google.com/maps/place/Place+Name/@lat,lng,zoom`
- Coordinate URL: `https://www.google.com/maps/@lat,lng,zoom`
- Short links: `https://maps.app.goo.gl/...` or `https://goo.gl/maps/...`
- Place ID/CID links: URLs containing `place_id:` or `cid=`

## Parsing Rules

When inspecting a Google Maps URL:

1. Identify the URL type from the path and query.
2. For `/maps/dir/` path URLs, treat path segments after `/dir/` as ordered route stops.
3. Decode `+` as spaces and percent-encoded values such as `%23` as `#`.
4. Extract viewport coordinates after `@lat,lng,zoom` when present, but do not treat them as the route itself.
5. Extract explicit coordinates using the pattern `@(-?\d+\.\d+),(-?\d+\.\d+)` when present.
6. Treat `!3e0` as driving mode when visible in Google Maps' internal route URLs.
7. Ignore tracking/session parameters such as `entry`, `g_ep`, `utm_*`, `gclid`, `gbraid`, and similar fields unless needed to explain the original URL.
8. For short links, say they must be expanded before reliable parsing.

## Generation Rules

Prefer clean directions API URLs for generated links:

```text
https://www.google.com/maps/dir/?api=1&origin=[origin]&destination=[destination]&waypoints=[waypoint1]|[waypoint2]&travelmode=[mode]
```

Supported `travelmode` values:

- `driving`
- `walking`
- `bicycling`
- `transit`

Use `driving` as the default visual skeleton for long overland route tracing unless the user asks otherwise. For real travel recommendations, defer feasibility to the transport specialist.

Encode values safely:

- Replace spaces with `+` or percent encoding.
- Encode waypoint separators as `%7C` when presenting a raw one-line URL.
- Keep country names in stops to reduce ambiguous pins.

## Search Link Patterns

Generate search links for route-adjacent planning:

```text
https://www.google.com/maps/search/?api=1&query=[query]
```

Useful travel searches:

- `hostels near [city] train station`
- `hotels with wifi near [city] downtown`
- `bus station [city country]`
- `train station [city country]`
- `safe central neighborhoods [city country]`
- `luggage storage near [station/city]`

Do not claim search results are vetted until another tool or the user inspects them.

## Output Contract

Return this structure:

```markdown
## Route Mapping
- Route: [ordered stops]
- Mode: [driving/transit/walking/bicycling]
- Google Maps route: [clean link]
- What this link is good for: [visual tracing, rough distance, waypoint sanity check]
- What this link is not good for: [visa, schedules, prices, border feasibility]

## Map Searches
- [purpose]: [Google Maps search link]

## Caveats
- [ambiguities, short-link limitations, odd routing, border/transport caveats]
```

## Guardrails

- Do not treat a driving route as proof that border crossings, roads, rental cars, or transit are feasible.
- Do not expose tracking-heavy URLs when a clean generated link is enough.
- Do not infer exact travel time, tolls, road conditions, or border wait times without current source evidence.
- Prefer route links as user-facing artifacts and transport research as the decision layer.
