# ✈️ Flight Ticket Searcher Report (Run #6): BOG -> BUD (Air France Focus)
*Tailored for Ordinary Colombian Passport Holders (`@ticket-searcher` — Run #6, Air France Focus)*

## 1. Search Criteria & Live Exchange Rate
- **Execution ID**: `antigravity-flight-run-006`
- **Route**: `BOG` (Bogotá El Dorado) -> `BUD` (Budapest Ferenc Liszt) -> `BOG` (Round-Trip)
- **Dates**: `2027-03-09` (Outbound) | `2027-04-10` (Return)
- **Passengers & Cabin**: `1` Adult | `economy` | Baggage: `carry_on` (default)
- **Airline Preference**: **Air France** (`BOG -> CDG -> BUD` / `BUD -> CDG -> BOG`), benchmarked across all 9 flight-provider skills
- **Live Exchange Rate**: `1 USD = 3,316.64 COP` (Source: `https://api.exchangerate-api.com/v4/latest/USD`, rate date `2026-11-16`, fetched `2026-11-16 20:29 UTC`)
- **Saved Execution Files**:
  - `run_fligth_agent/run_06_bog_bud_airfrance_mar09_apr10.md`
  - `run_fligth_agent/latest_execution.md`
  - `run_fligth_agent/executions.json`

---

## 2. Top 5 Ranked Flights (Optimized by Price + Layover Time + Air France Focus)

| Rank | Source Skill | Airline(s) & Route | Total Price (USD / Live COP) | Layover Time (`layoff time`) & Hub | Total Duration | Baggage & Ticketing Notes | Colombian Transit Visa & Safety Check | Clean Link |
|---|---|---|---|---|---|---|---|---|
| **#1** | **Air France** (`airfrance-flight-search`) | **Air France (Protected Single-PNR)**<br/>Out: `BOG -> CDG -> BUD` (`AF423` + `AF1394`)<br/>Ret: `BUD -> CDG -> BOG` (`AF` + `AF422`) | **~$1,020 USD**<br/>(`$3,382,973 COP`) | Out: **2h 10m** at `CDG`<br/>Ret: **2h 25m** at `CDG` | Out: `13h 50m`<br/>Ret: `14h 35m` | Economy Light includes `12 kg` carry-on + personal item; single-PNR EU261 protection (Standard `23 kg` checked ~$1,140 USD / `$3,780,970 COP`) | ✅ **Visa-free Schengen entry/transit at `CDG`** (90 days/180 days for ordinary Colombian passport); bypasses US/UK transit visas | `https://wwws.airfrance.com.co/` |
| **#2** | **Air France + Skyscanner** (`airfrance-flight-search` / `skyscanner-flight-search`) | **Air France + KLM (Extended-Buffer Single-PNR)**<br/>Out: `BOG -> CDG -> BUD` (`AF423` + evening `AF1694`)<br/>Ret: `BUD -> AMS/CDG -> BOG` | **~$995 USD**<br/>(`$3,300,057 COP`) | Out: **6h 25m** at `CDG`<br/>Ret: **2h 15m – 3h 30m** at `AMS`/`CDG` | Out: `18h 10m`<br/>Ret: `15h 10m` | Economy Light (`12 kg` carry-on included); bags checked through on single PNR with large CDG buffer | ✅ **Visa-free Schengen entry/transit at `CDG`/`AMS`**; zero self-transfer risk | `https://www.skyscanner.net/transport/flights/bog/bud/270309/270410/` |
| **#3** | **Google Flights** (`google-flights-search`) | **Lufthansa (Star Alliance 1-Stop)**<br/>Out: `BOG -> FRA -> BUD` (`LH543` + `LH`)<br/>Ret: `BUD -> FRA -> BOG` (`LH` + `LH542`) | **~$1,045 USD**<br/>(`$3,465,889 COP`) | Out: **2h 15m – 3h 35m** at `FRA`<br/>Ret: **2h 10m** at `FRA` | Out: `14h 50m`<br/>Ret: `14h 15m` | Economy Light (`8 kg` carry-on + personal item); single-PNR Star Alliance protection | ✅ **Visa-free Schengen entry/transit at `FRA`** for ordinary Colombian passport holders | `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-09+return+2027-04-10` |
| **#4** | **Avianca** (`avianca-flight-search`) | **Avianca + Iberia (Via Madrid)**<br/>Out: `BOG -> MAD -> BUD`<br/>Ret: `BUD -> MAD -> BOG` | **~$960 USD**<br/>(`$3,183,974 COP`) | Out: **2h 35m** at `MAD`<br/>Ret: **2h 50m** at `MAD` | Out: `15h 30m`<br/>Ret: `15h 55m` | Verify `Light`/`S` fare (`10 kg` carry-on) vs `XS` (personal item only); single-PNR via `MAD` | ✅ **Visa-free Schengen entry/transit at `MAD`**; Spanish-language transit hub | `https://www.avianca.com/es/` |
| **#5** | **KAYAK** (`kayak-flight-search`) | **Turkish Airlines (Via Istanbul)**<br/>Out: `BOG -> IST -> BUD`<br/>Ret: `BUD -> IST -> BOG` | **~$1,080 USD**<br/>(`$3,581,971 COP`) | Out: **3h 10m** at `IST`<br/>Ret: **3h 25m** at `IST` | Out: `18h 30m`<br/>Ret: `19h 05m` | Includes `23 kg` checked bag + `8 kg` carry-on in standard economy; longer eastward routing | ✅ **Visa-free airside transit at `IST`** (Turkey is also visa-free for short stays on Colombian ordinary passports) | `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a` |

---

## 3. All 9 Provider Skill Snapshots
- **1. Google Flights (`google-flights-search`)**: Confirms 1-stop legacy options via `CDG` (Air France), `FRA` (Lufthansa), `MAD` (Iberia), and `AMS` (KLM) typically ranging **$960–$1,300 USD** (`$3,183,974–$4,311,632 COP`) for `2027-03-09` to `2027-04-10`. Clean URL: `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-09+return+2027-04-10`
- **2. KAYAK (`kayak-flight-search`)**: Surfaces Turkish Airlines via `IST` (~$1,080 USD / `$3,581,971 COP` with 23 kg checked bag) alongside Air France/KLM SkyTeam combinations. Clean URL: `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
- **3. Skyscanner (`skyscanner-flight-search`)**: Highlights March/April shoulder-season savings and Air France/KLM combinations via `CDG`/`AMS` starting ~$995 USD (`$3,300,057 COP`). Clean URL: `https://www.skyscanner.net/transport/flights/bog/bud/270309/270410/`
- **4. Momondo (`momondo-flight-search`)**: Compares cross-OTA fares for Air France, Iberia, and KLM (~$945–$1,020 USD / `$3,134,225–$3,382,973 COP`); verify OTA payment/baggage fees before checkout. Clean URL: `https://www.momondo.com/flight-search/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
- **5. Kiwi.com (`kiwi-flight-search`)**: Virtual interlining (`BOG -> MAD/CDG` + Wizz Air/Ryanair `-> BUD`) from ~$865 USD (`$2,868,894 COP`) with carry-on add-ons, but requires a **4h+ self-transfer buffer**, Schengen border clearance, and baggage re-check. Clean URL: `https://www.kiwi.com/en/search/results/bogota-colombia/budapest-hungary/2027-03-09/2027-04-10`
- **6. Skiplagged (`skiplagged-flight-search`)**: Disqualified for hidden-city use on a round-trip (`2027-03-09` to `2027-04-10`) because skipping a leg cancels the return ticket; standard fares align with ~$980–$1,050 USD (`$3,250,307–$3,482,472 COP`). Clean URL: `https://skiplagged.com/flights/BOG/BUD/2027-03-09/2027-04-10`
- **7. Air France (`airfrance-flight-search`)**: **Top Recommended Carrier** for this request — daily `AF423` (`BOG -> CDG`, ~10h 15m) + `AF1394`/`AF1694` (`CDG -> BUD`, ~2h 15m) and return via `AF422` (`CDG -> BOG`, ~11h 10m). Indicative `Economy Light` (`12 kg` carry-on) ~$995–$1,020 USD (`$3,300,057–$3,382,973 COP`). Clean URL: `https://wwws.airfrance.com.co/`
- **8. Avianca (`avianca-flight-search`)**: `BOG -> MAD` + Iberia/partner `MAD -> BUD` from ~$960 USD (`$3,183,974 COP`); confirm `Light`/`S` fare includes `10 kg` carry-on. Clean URL: `https://www.avianca.com/es/`
- **9. Ryanair (`ryanair-flight-search`)**: Intra-European point-to-point only (e.g., `Paris Beauvais BVA -> BUD` ~$45–$75 USD / `$149,249–$248,748 COP` with Priority `10 kg` bag). Not recommended over a single-PNR Air France ticket because `BVA` is ~85 km from `CDG` and requires an unprotected landside transfer. Clean URL: `https://www.ryanair.com/gb/en`

---

## 4. Booking & Transit Caveats
- **Indicative Pricing**: All fares are read-only indicative planning estimates; verify exact live availability, fare family (`Light` vs `Standard`), and seat/baggage fees on `airfrance.com.co` or the OTA checkout page before payment.
- **Colombian Passport & Schengen Rules**: Ordinary Colombian passport holders enjoy **90 days visa-free** entry in the Schengen Area (France `CDG`, Hungary `BUD`, Spain `MAD`, Germany `FRA`, Netherlands `AMS`). Ensure passport validity is **≥ 6 months** beyond `2027-04-10` (plus any applicable ETIAS authorization if active by March 2027) and avoid US (`MIA`/`JFK`) or UK (`LHR`) transit hubs unless holding valid transit visas.
